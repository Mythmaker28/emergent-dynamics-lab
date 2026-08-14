"""Explicit counterexample that withdraws the universal 'bilinear birth + linear Y death makes
maintenance and boundedness mutually exclusive' statement. Pure algebra on the well-mixed
reduction of the MINCORE reaction WITH the capacity factor that the real engine has
(cand = min(n_res, free)); no engine, no RNG, no trajectory."""
import json
from fractions import Fraction as F
import numpy as np

kX, kY, muX, muY = F(2, 100), F(8, 10000), F(5, 1000), F(5, 10000)   # MINCORE frozen Spec
s, K = F(3), F(10)          # resource set-point and free-capacity scale

# interior equilibrium: kX*y*c = muX and kY*x*c = muY, c = s*(1-(x+y)/K)
rho = kY * muX / (kX * muY)                    # y = rho * x
# muX/(kX*rho*x) = s*(1-(1+rho)x/K)  ->  a x^2 + b x + c0 = 0
a = s * (1 + rho) / K
b = -s
c0 = muX / (kX * rho)
disc = b * b - 4 * a * c0
roots = [(-b + r) / (2 * a) for r in (F(np.sqrt(float(disc))).limit_denominator(10**12), )]
roots += [(-b - F(np.sqrt(float(disc))).limit_denominator(10**12)) / (2 * a)]

out = {"rho_y_over_x": float(rho), "discriminant": float(disc), "equilibria": []}
for x in roots:
    y = rho * x
    c = s * (1 - (x + y) / K)
    fx = float(kX * x * y * c - muX * x)
    fy = float(kY * x * y * c - muY * y)
    X, Y, S, KK = float(x), float(y), float(s), float(K)
    kx, ky, mx, my = float(kX), float(kY), float(muX), float(muY)
    C = S * (1 - (X + Y) / KK)
    dC = -S / KK
    J = np.array([[kx * Y * C + kx * X * Y * dC - mx, kx * X * C + kx * X * Y * dC],
                  [ky * Y * C + ky * X * Y * dC,      ky * X * C + ky * X * Y * dC - my]])
    ev = np.linalg.eigvals(J)
    out["equilibria"].append({
        "x": X, "y": Y, "cand_density": C, "occupancy_x_plus_y": X + Y,
        "residual_dx": fx, "residual_dy": fy,
        "eigenvalues": [complex(e).real for e in ev],
        "stable": bool(np.all(np.real(ev) < 0))})
print(json.dumps(out, indent=1))
json.dump(out, open("out/_withdrawal_counterexample.json", "w"), indent=1)
