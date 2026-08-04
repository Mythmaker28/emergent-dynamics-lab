module route_e_drand_verify

go 1.24.0

toolchain go1.24.7

require (
	github.com/drand/kyber v1.3.1
	github.com/drand/kyber-bls12381 v0.3.4
)

require (
	github.com/kilic/bls12-381 v0.1.0 // indirect
	golang.org/x/crypto v0.43.0 // indirect
	golang.org/x/sys v0.38.0 // indirect
)

// The canonical golang.org/x/* module paths resolve through golang.org, which this
// build environment does not allow.  These replacements point at the SAME upstream
// repositories (the golang.org/x/* modules are published from github.com/golang/*),
// pinned to exact versions and recorded in go.sum.
replace golang.org/x/sys => github.com/golang/sys v0.38.0

replace golang.org/x/crypto => github.com/golang/crypto v0.43.0
