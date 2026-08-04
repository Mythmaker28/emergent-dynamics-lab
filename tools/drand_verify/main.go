// Command drand_verify is an OFFLINE drand beacon-round verifier for the scheme
// "bls-unchained-g1-rfc9380" (drand quicknet family).
//
// IT PERFORMS NO NETWORK ACCESS OF ANY KIND.  It reads ONE bounded JSON request on
// stdin and writes ONE JSON response on stdout.  It never selects a round, never
// fetches a beacon, and never contacts drand.  All cryptography is performed by the
// maintained drand libraries github.com/drand/kyber-bls12381 and
// github.com/drand/kyber (sign/bls); no BLS arithmetic is written here.
//
// Verified properties, each checked against library source, not documentation:
//   - scheme id, DST and message construction are those of drand crypto/schemes.go
//     NewPedersenBLSUnchainedG1: SigGroup = G1, KeyGroup = G2,
//     DST_G1 = "BLS_SIG_BLS12381G1_XMD:SHA-256_SSWU_RO_NUL_",
//     message = SHA256(uint64 big-endian round);
//   - compressed deserialisation goes through kilic/bls12-381 FromCompressed, which
//     requires the compression flag, rejects x >= p (canonical encoding, fp.fromBytes
//     "must be less than modulus"), solves the curve equation and enforces
//     InCorrectSubgroup;
//   - FromCompressed ACCEPTS the point at infinity (it returns Zero), so this program
//     rejects the infinity encoding explicitly, for both G1 and G2;
//   - re-serialisation must reproduce the input bytes exactly, which rejects any
//     non-canonical encoding the library might tolerate;
//   - randomness must equal SHA256(signature).
//
// Exit codes: 0 a verdict was produced (status verified|invalid); 2 configuration
// error (bad request, unsupported scheme, oversized input); 3 internal error.
package main

import (
	"crypto/sha256"
	"encoding/binary"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"os"

	bls12381 "github.com/drand/kyber-bls12381"
	"github.com/drand/kyber/sign/bls"
)

// SchemeID is the ONLY scheme this program will verify.
const SchemeID = "bls-unchained-g1-rfc9380"

// DstG1 and DstG2 are the RFC 9380 domain separation tags of that scheme, copied
// literally from drand crypto/schemes.go NewPedersenBLSUnchainedG1.
const (
	DstG1 = "BLS_SIG_BLS12381G1_XMD:SHA-256_SSWU_RO_NUL_"
	DstG2 = "BLS_SIG_BLS12381G2_XMD:SHA-256_SSWU_RO_NUL_"
)

const (
	maxRequestBytes = 8192
	pubKeyBytes     = 96 // G2, compressed
	signatureBytes  = 48 // G1, compressed
	randomnessBytes = 32
)

type request struct {
	Scheme     string `json:"scheme"`
	PublicKey  string `json:"public_key"`
	Round      uint64 `json:"round"`
	Signature  string `json:"signature"`
	Randomness string `json:"randomness"`
}

type response struct {
	Status  string `json:"status"`
	Reason  string `json:"reason"`
	Scheme  string `json:"scheme"`
	Dst     string `json:"dst"`
	Version string `json:"verifier_version"`
}

const verifierVersion = "route-e-drand-verify/v1"

func emit(status, reason string, code int) {
	out, err := json.Marshal(response{
		Status:  status,
		Reason:  reason,
		Scheme:  SchemeID,
		Dst:     DstG1,
		Version: verifierVersion,
	})
	if err != nil {
		fmt.Fprintln(os.Stderr, "internal: response marshal failed")
		os.Exit(3)
	}
	fmt.Println(string(out))
	os.Exit(code)
}

// decodeExact decodes a hex string of exactly n bytes.
func decodeExact(value string, n int, what string) ([]byte, error) {
	raw, err := hex.DecodeString(value)
	if err != nil {
		return nil, fmt.Errorf("%s is not valid hex", what)
	}
	if len(raw) != n {
		return nil, fmt.Errorf("%s must be exactly %d bytes, got %d", what, n, len(raw))
	}
	return raw, nil
}

// isInfinity reports whether a compressed encoding is the point at infinity.
// FromCompressed accepts it and returns the zero point, so it must be rejected here.
func isInfinity(raw []byte) bool {
	if len(raw) == 0 || raw[0] != 0xc0 {
		return false
	}
	for _, b := range raw[1:] {
		if b != 0x00 {
			return false
		}
	}
	return true
}

func main() {
	if len(os.Args) != 2 || os.Args[1] != "verify" {
		emit("configuration_error", "usage: drand_verify verify  (one JSON request on stdin)", 2)
	}

	limited := io.LimitReader(os.Stdin, maxRequestBytes+1)
	payload, err := io.ReadAll(limited)
	if err != nil {
		emit("internal_error", "could not read stdin", 3)
	}
	if len(payload) > maxRequestBytes {
		emit("configuration_error", "request exceeds the bounded input size", 2)
	}

	decoder := json.NewDecoder(newByteReader(payload))
	decoder.DisallowUnknownFields()
	var req request
	if err := decoder.Decode(&req); err != nil {
		emit("configuration_error", "request is not a strict JSON object: "+err.Error(), 2)
	}
	if err := noTrailingContent(decoder); err != nil {
		emit("configuration_error", err.Error(), 2)
	}

	if req.Scheme != SchemeID {
		emit("configuration_error", "unsupported scheme; only "+SchemeID+" is verified here", 2)
	}
	if req.Round == 0 {
		emit("configuration_error", "round must be a positive integer", 2)
	}

	pubRaw, err := decodeExact(req.PublicKey, pubKeyBytes, "public_key")
	if err != nil {
		emit("configuration_error", err.Error(), 2)
	}
	sigRaw, err := decodeExact(req.Signature, signatureBytes, "signature")
	if err != nil {
		emit("invalid", err.Error(), 0)
	}
	randRaw, err := decodeExact(req.Randomness, randomnessBytes, "randomness")
	if err != nil {
		emit("invalid", err.Error(), 0)
	}

	if isInfinity(pubRaw) {
		emit("configuration_error", "public_key is the point at infinity", 2)
	}
	if isInfinity(sigRaw) {
		emit("invalid", "signature is the point at infinity", 0)
	}

	suite := bls12381.NewBLS12381SuiteWithDST([]byte(DstG1), []byte(DstG2))

	pub := suite.G2().Point()
	if err := pub.UnmarshalBinary(pubRaw); err != nil {
		emit("configuration_error", "public_key does not decompress: "+err.Error(), 2)
	}
	if err := canonical(pub, pubRaw); err != nil {
		emit("configuration_error", "public_key: "+err.Error(), 2)
	}

	sigPoint := suite.G1().Point()
	if err := sigPoint.UnmarshalBinary(sigRaw); err != nil {
		emit("invalid", "signature does not decompress: "+err.Error(), 0)
	}
	if err := canonical(sigPoint, sigRaw); err != nil {
		emit("invalid", "signature: "+err.Error(), 0)
	}

	digest := sha256.New()
	if err := binary.Write(digest, binary.BigEndian, req.Round); err != nil {
		emit("internal_error", "could not build the round digest", 3)
	}
	message := digest.Sum(nil)

	scheme := bls.NewSchemeOnG1(suite)
	if err := scheme.Verify(pub, message, sigRaw); err != nil {
		emit("invalid", "signature does not verify against the public key for this round", 0)
	}

	computed := sha256.Sum256(sigRaw)
	if !equalBytes(computed[:], randRaw) {
		emit("invalid", "randomness is not sha256(signature)", 0)
	}

	emit("verified", "signature and randomness verified offline", 0)
}

func canonical(point interface{ MarshalBinary() ([]byte, error) }, raw []byte) error {
	round, err := point.MarshalBinary()
	if err != nil {
		return errors.New("could not re-serialise the point")
	}
	if !equalBytes(round, raw) {
		return errors.New("encoding is not canonical")
	}
	return nil
}

func equalBytes(a, b []byte) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}

type byteReader struct {
	data []byte
	pos  int
}

func newByteReader(data []byte) *byteReader { return &byteReader{data: data} }

func (r *byteReader) Read(p []byte) (int, error) {
	if r.pos >= len(r.data) {
		return 0, io.EOF
	}
	n := copy(p, r.data[r.pos:])
	r.pos += n
	return n, nil
}

func noTrailingContent(decoder *json.Decoder) error {
	var extra json.RawMessage
	if err := decoder.Decode(&extra); err != io.EOF {
		return errors.New("request must contain exactly one JSON object")
	}
	return nil
}
