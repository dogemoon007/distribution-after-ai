#!/usr/bin/env python3
"""
verify.py -- numerical and exact checks of every formula in

    "Separating Capture from Allocation:
     A Commitment Model of Distribution after AI"

Requires Python 3 and numpy only. Every closed form stated in the paper is
checked either (i) exactly, in rational arithmetic, or (ii) by brute-force
optimisation on a fine grid, without using the closed form to find the optimum.
The script exits with status 1 if any check fails.

Model
-----
Output            Y = A k + theta E,  E = mean contribution
Costs             k^2/2 (capturer), e_i^2/2 (individual i)
Linear rule       t_i = sigma A k + s theta e_i,  (sigma, s) in [0,1]^2
Payoffs           Pi = (1-sigma) A k + (1-s) theta E - k^2/2
                  u_i = sigma A k + s theta e_i - e_i^2/2
Rule-setter       maximises Pi + omega U
"""
import itertools
import math
import sys
from fractions import Fraction as Fr

import numpy as np

rng = np.random.default_rng(20261110)
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


def close(a, b, tol=1e-6):
    return abs(a - b) <= tol * (1.0 + abs(a) + abs(b))


# ----------------------------------------------------------------------------
# Primitives
# ----------------------------------------------------------------------------
def payoffs(A, th, sig, s, k, e):
    """Symmetric profile: every individual contributes e."""
    Pi = (1 - sig) * A * k + (1 - s) * th * e - k * k / 2
    U = sig * A * k + s * th * e - e * e / 2
    return Pi, U


def eq_rule(A, th, sig, s):
    """Equilibrium under an observed, irrevocable rule (closed form)."""
    k = (1 - sig) * A
    e = s * th
    Pi, U = payoffs(A, th, sig, s, k, e)
    return k, e, Pi, U


def sigma_star(w):
    return 0.0 if w <= 1 else (w - 1) / (2 * w - 1)


def s_star(w):
    return 1.0 / (2 - w) if w <= 1 else 1.0


# ----------------------------------------------------------------------------
# C1. Best responses under a committed rule, by brute force
# ----------------------------------------------------------------------------
ok = True
worst = 0.0
for _ in range(200):
    A, th = rng.uniform(0.2, 3.0, size=2)
    sig, s = rng.uniform(0, 1, size=2)
    kg = np.linspace(0, 2 * A, 400001)
    eg = np.linspace(0, 2 * th, 400001)
    k_bf = kg[np.argmax((1 - sig) * A * kg - kg ** 2 / 2)]
    e_bf = eg[np.argmax(s * th * eg - eg ** 2 / 2)]
    d = max(abs(k_bf - (1 - sig) * A), abs(e_bf - s * th))
    worst = max(worst, d)
    ok &= d < 1e-4
check("C1  best responses k=(1-sigma)A, e=s*theta (grid search, 200 draws)", ok,
      f"max abs error {worst:.2e}")

# ----------------------------------------------------------------------------
# C2. Payoff identities, exact rational arithmetic
# ----------------------------------------------------------------------------
ok = True
for _ in range(2000):
    A = Fr(int(rng.integers(1, 40)), int(rng.integers(1, 40)))
    th = Fr(int(rng.integers(0, 40)), int(rng.integers(1, 40)))
    sig = Fr(int(rng.integers(0, 101)), 100)
    s = Fr(int(rng.integers(0, 101)), 100)
    k = (1 - sig) * A
    e = s * th
    Pi = (1 - sig) * A * k + (1 - s) * th * e - k * k / 2
    U = sig * A * k + s * th * e - e * e / 2
    ok &= Pi == (1 - sig) ** 2 * A ** 2 / 2 + s * (1 - s) * th ** 2
    ok &= U == sig * (1 - sig) * A ** 2 + s ** 2 * th ** 2 / 2
    ok &= Pi + U == A ** 2 * (1 - sig ** 2) / 2 + th ** 2 * s * (2 - s) / 2
    # transfers and output
    T = sig * A * k + s * th * e
    Y = A * k + th * e
    ok &= T <= Y
check("C2  closed forms for Pi, U, W under a rule (exact, 2000 rational draws)", ok)

# ----------------------------------------------------------------------------
# C3. The rule-setter's optimal committed rule, by brute force
# ----------------------------------------------------------------------------
ok = True
worst = 0.0
grid = np.linspace(0, 1, 2000001)
for w in [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 0.999, 1.0, 1.001, 1.25, 1.5, 2.0,
          2.5, 3.0, 10.0, 100.0, 1e4]:
    for A, th in [(1.0, 1.0), (2.0, 0.3), (0.7, 1.9)]:
        obj_sig = A ** 2 * ((1 - grid) ** 2 / 2 + w * grid * (1 - grid))
        obj_s = th ** 2 * (grid * (1 - grid) + w * grid ** 2 / 2)
        sig_bf = grid[np.argmax(obj_sig)]
        s_bf = grid[np.argmax(obj_s)]
        d = max(abs(sig_bf - sigma_star(w)), abs(s_bf - s_star(w)))
        worst = max(worst, d)
        ok &= d < 1e-5
check("C3  sigma*(w)=max{0,(w-1)/(2w-1)}, s*(w)=1/(2-w) or 1 (grid search)", ok,
      f"max abs error {worst:.2e}")

# special cases quoted in the text and in Table 1
ok = (sigma_star(0), s_star(0)) == (0.0, 0.5)
ok &= (sigma_star(1), s_star(1)) == (0.0, 1.0)
ok &= close(sigma_star(1e12), 0.5) and s_star(1e12) == 1.0
ok &= all(sigma_star(w) < 0.5 for w in np.linspace(1, 1e6, 10001))
check("C3b special cases (0,1/2), (0,1), (1/2,1); sigma* < 1/2 always", ok)

# ----------------------------------------------------------------------------
# C4. Discretion: backward induction by brute force
#     The setter picks (sigma, s) after (k, e) are sunk.
# ----------------------------------------------------------------------------
def discretion_bf(A, th, w, n=401):
    cand = np.linspace(0, 1, 11)  # ex post objective is linear: corners suffice

    def ex_post(k, e):
        best, arg = -1e99, None
        for sg, ss in itertools.product(cand, cand):
            Pi, U = payoffs(A, th, sg, ss, k, e)
            v = Pi + w * U
            if v > best + 1e-12:
                best, arg = v, (sg, ss)
        return arg

    # capturer: anticipates sigma(k); individuals: anticipate s(e).
    # (finite-population logic: a contributor's own e triggers the ex post s.)
    kg = np.linspace(0, 2 * A, n)
    eg = np.linspace(0, 2 * th, n) if th > 0 else np.array([0.0])
    # ex post sigma depends only on whether k>0; s only on whether e>0
    best_k, best_val = 0.0, -1e99
    for k in kg:
        sg, _ = ex_post(k, 1.0 if th > 0 else 0.0) if k > 0 else (0.0, 0.0)
        val = (1 - sg) * A * k - k * k / 2
        if val > best_val + 1e-12:
            best_val, best_k = val, k
    best_e, best_val = 0.0, -1e99
    for e in eg:
        _, ss = ex_post(1.0, e) if e > 0 else (0.0, 0.0)
        val = ss * th * e - e * e / 2
        if val > best_val + 1e-12:
            best_val, best_e = val, e
    sg, ss = ex_post(max(best_k, 1e-9), max(best_e, 1e-9))
    Pi, U = payoffs(A, th, sg, ss, best_k, best_e)
    T = sg * A * best_k + ss * th * best_e
    return best_k, best_e, sg, ss, Pi, U, T


ok = True
for A, th in [(1.0, 1.0), (2.0, 0.5), (0.8, 1.6)]:
    for w in [0.0, 0.3, 0.9]:
        k, e, sg, ss, Pi, U, T = discretion_bf(A, th, w)
        ok &= close(k, A, 1e-2) and e == 0.0 and T == 0.0
        ok &= close(Pi, A * A / 2, 1e-3) and U == 0.0
    for w in [1.1, 2.0, 50.0]:
        k, e, sg, ss, Pi, U, T = discretion_bf(A, th, w)
        ok &= k == 0.0 and close(e, th, 1e-2) and (sg, ss) == (1.0, 1.0)
        ok &= close(Pi, 0.0, 1e-3) and close(U, th * th / 2, 1e-3)
        ok &= close(T, th * th, 1e-2)          # everything is transferred
check("C4  discretion: w<1 -> (k,e,T)=(A,0,0); w>1 -> (0,theta,theta^2)", ok)

# slope of the ex post objective is (w-1) * base
ok = True
for _ in range(500):
    A, th, k, e, w = rng.uniform(0.1, 3, size=5)
    f = lambda sg, ss: sum(x * y for x, y in zip(payoffs(A, th, sg, ss, k, e), (1, w)))
    ok &= close(f(1, 0) - f(0, 0), (w - 1) * A * k)
    ok &= close(f(0, 1) - f(0, 0), (w - 1) * th * e)
check("C4b ex post objective is linear with slopes (w-1)Ak and (w-1)theta*E", ok)

# ----------------------------------------------------------------------------
# C5. Everyone prefers to be bound
# ----------------------------------------------------------------------------
ok = True
for A, th in [(1.0, 1.0), (2.0, 0.5), (0.8, 1.6)]:
    for w in np.concatenate([np.linspace(0, 0.99, 34), np.linspace(1.01, 30, 67)]):
        _, _, Pi_r, U_r = eq_rule(A, th, sigma_star(w), s_star(w))
        if w < 1:
            Pi_d, U_d = A * A / 2, 0.0
        else:
            Pi_d, U_d = 0.0, th * th / 2
        ok &= (Pi_r + w * U_r) > (Pi_d + w * U_d) + 1e-12
    # the two named cases
    _, _, Pi_r, _ = eq_rule(A, th, 0.0, 0.5)
    ok &= close(Pi_r, A * A / 2 + th * th / 4)
    _, _, _, U_r = eq_rule(A, th, 0.5, 1.0)
    ok &= close(U_r, A * A / 4 + th * th / 2)
check("C5  setter's objective strictly higher under its optimal rule (w != 1)", ok)

# ----------------------------------------------------------------------------
# C6. Capturer's commitment: linear and unrestricted rules
# ----------------------------------------------------------------------------
ok = True
for A, th in [(1.0, 1.0), (2.0, 0.5), (0.8, 1.6)]:
    # linear
    k, e, Pi, U = eq_rule(A, th, 0.0, 0.5)
    T = 0.5 * th * e
    ok &= close(T, th * th / 4) and close(U, th * th / 8)
    # unrestricted: choose (e, t) with t >= e^2/2 (participation); profit th*e - t
    eg = np.linspace(0, 3 * th, 600001)
    prof = th * eg - eg ** 2 / 2          # t = e^2/2 binds at the optimum
    e_bf = eg[np.argmax(prof)]
    ok &= close(e_bf, th, 1e-4) and close(e_bf ** 2 / 2, th * th / 2, 1e-4)
    # any unconditional payment lowers profit one for one
    ok &= all(eq_rule(A, th, sg, 0.5)[2] < Pi for sg in np.linspace(0.01, 1, 100))
check("C6  capturer's rule: sigma=0; T=theta^2/4 (linear), theta^2/2 (forcing)", ok)

# ----------------------------------------------------------------------------
# C7. Repeated discretion
# ----------------------------------------------------------------------------
# (i) Lemma 2: per-period joint surplus <= (A^2 + theta^2)/2, any profile
ok = True
for _ in range(20000):
    A, th = rng.uniform(0.1, 3, size=2)
    k = rng.uniform(0, 3 * A)
    e_i = rng.uniform(0, 3 * th, size=int(rng.integers(1, 50)))
    surplus = A * k - k * k / 2 + th * e_i.mean() - (e_i ** 2).mean() / 2
    ok &= surplus <= (A * A + th * th) / 2 + 1e-12
check("C7a Lemma 2: joint surplus <= (A^2+theta^2)/2 (20000 random profiles)", ok)

# (ii) Lemma 1: capturer's security level: k=A, T=0 gives >= A^2/2 whatever E
ok = all(A * A + th * E - A * A / 2 >= A * A / 2
         for A, th, E in rng.uniform(0, 3, size=(5000, 3)))
check("C7b Lemma 1: capturer secures A^2/2 per period with k=A, T=0", ok)


# (iii) stationary linear relational rule s: sustainable iff s <= delta.
def pv(stream_first, stream_rest, delta, horizon=20000):
    return stream_first + delta * stream_rest / (1 - delta)


ok = True
for A, th in [(1.0, 1.0), (2.0, 0.5)]:
    for delta in np.linspace(0.05, 0.95, 19):
        for s in np.linspace(0.01, 1.0, 100):
            on_path = A * A / 2 + s * (1 - s) * th * th     # per period
            T = s * s * th * th
            # at the payment stage: pay T and continue vs. keep T and revert
            pay = -T + delta * on_path / (1 - delta)
            renege = delta * (A * A / 2) / (1 - delta)
            sustainable = pay >= renege - 1e-12
            ok &= sustainable == (s <= delta + 1e-12)
            if sustainable:
                ok &= T <= delta * th * th / (2 * (1 - delta)) + 1e-12
                ok &= T <= delta ** 2 * th * th + 1e-12
check("C7c stationary linear rule sustainable iff s <= delta; T <= delta^2 theta^2", ok)

# (iv) all stationary contracts (e, T): individual IC T >= e^2/2, capturer IC
#      T <= delta*theta*e.  General bound T <= delta*theta^2 / (2(1-delta)).
ok = True
tight = 0.0
for delta in np.linspace(0.02, 0.98, 49):
    th = 1.0
    eg = np.linspace(0, 3, 3001)
    Tg = np.linspace(0, 5, 5001)
    Eg, TT = np.meshgrid(eg, Tg, indexing="ij")
    feas = (TT >= Eg ** 2 / 2 - 1e-12) & (TT <= delta * th * Eg + 1e-12)
    Tmax = TT[feas].max()
    bound = delta * th * th / (2 * (1 - delta))
    ok &= Tmax <= bound + 1e-9
    ok &= close(Tmax, 2 * delta ** 2 * th * th, 2e-3)
    if abs(delta - 0.5) < 1e-9:
        tight = bound - Tmax
check("C7d general bound holds on all stationary contracts; tight at delta=1/2", ok,
      f"slack at delta=1/2: {tight:.1e}")

# ----------------------------------------------------------------------------
# C8. Competition among m capturers
# ----------------------------------------------------------------------------
ok = True
for m in range(2, 9):
    th = 1.3
    s = np.full(m, 0.9)
    for _ in range(2000):                       # best-response iteration
        for j in range(m):
            others = s.sum() - s[j]
            g = np.linspace(0, 1, 20001)
            s[j] = g[np.argmax((1 - g) * (g + others))]
    ok &= np.allclose(s, 1 / (m + 1), atol=1e-3)
    S = m / (m + 1)
    T = (S * th) * (S * th)                     # sum_j s_j theta E, E = S theta
    ok &= T < th * th
    # sigma_j = 0 is dominant: profit strictly decreasing in sigma_j
    A = 1.7
    prof = [(1 - sg) ** 2 * A * A / 2 for sg in np.linspace(0, 1, 101)]
    ok &= all(prof[i] > prof[i + 1] for i in range(100))
check("C8  competition: s_j = 1/(m+1), sigma_j = 0, T < theta^2 (m = 2..8)", ok)

# ----------------------------------------------------------------------------
# C9. Dividend D = sigma A k in every regime (Proposition 4)
# ----------------------------------------------------------------------------
ok = True
for A, th in [(1.0, 1.0), (2.0, 0.5), (0.8, 1.6)]:
    for w in [0.0, 0.5, 0.99, 1.01, 1.5, 3.0, 40.0]:
        # rule
        sg = sigma_star(w)
        D_rule = sg * A * (1 - sg) * A
        if w > 1:
            ok &= close(D_rule, w * (w - 1) * A * A / (2 * w - 1) ** 2) and D_rule > 0
        else:
            ok &= D_rule == 0.0
        # discretion (also: unobserved rule)
        k, e, sgd, ssd, *_ = discretion_bf(A, th, w, n=201)
        ok &= sgd * A * k == 0.0
check("C9  D>0 iff rule is ex ante, observed and set with w>1; D formula", ok)

# dividend is increasing in w and bounded by A^2/4
ws = np.linspace(1.0001, 1e4, 200001)
D = ws * (ws - 1) / (2 * ws - 1) ** 2
check("C9b D/A^2 increasing in w with supremum 1/4",
      np.all(np.diff(D) > 0) and D.max() < 0.25 and close(D[-1], 0.25, 1e-3))

# ----------------------------------------------------------------------------
# C10. Surplus comparison: separated rule vs. capturer's rule
# ----------------------------------------------------------------------------
ok = True
for _ in range(5000):
    A, th = rng.uniform(0.1, 3, size=2)
    w = rng.uniform(1.0001, 50)
    sg = sigma_star(w)
    W_sep = sum(eq_rule(A, th, sg, 1.0)[2:])
    W_cap = sum(eq_rule(A, th, 0.0, 0.5)[2:])
    ok &= close(W_sep - W_cap, th * th / 8 - A * A * sg * sg / 2)
    ok &= (W_sep > W_cap) == (th / A > 2 * sg)
check("C10 W(separated) - W(capturer) = theta^2/8 - sigma^2 A^2/2", ok)

# ----------------------------------------------------------------------------
# C11. Optimal-linear-tax form, and constant-elasticity generalisation
# ----------------------------------------------------------------------------
ok = True
for w in np.linspace(1.01, 60, 300):
    g = 1 / w
    ok &= close(sigma_star(w), (1 - g) / (1 - g + 1.0))
check("C11 sigma* = (1-g)/(1-g+eps) with g=1/w, eps=1", ok)

ok = True
worst = 0.0
sg_grid = np.linspace(0, 1, 400001)[:-1]
for eps in [0.25, 0.5, 1.0, 2.0, 4.0]:
    for w in [1.2, 2.0, 5.0, 1e3, 1e9]:
        A = 1.4
        k = ((1 - sg_grid) * A) ** eps                    # capturer's FOC
        cost = k ** (1 + 1 / eps) / (1 + 1 / eps)
        obj = (1 - sg_grid) * A * k - cost + w * sg_grid * A * k
        bf = sg_grid[np.argmax(obj)]
        cf = (w - 1) / (w - 1 + w * eps)
        worst = max(worst, abs(bf - cf))
        ok &= abs(bf - cf) < 1e-4 and cf < 1 / (1 + eps) + 1e-12
check("C11b elasticity eps: sigma* = (w-1)/(w-1+w*eps) <= 1/(1+eps)", ok,
      f"max abs error {worst:.2e}")

# ----------------------------------------------------------------------------
# C12. Table 1
# ----------------------------------------------------------------------------
A, th = Fr(3, 2), Fr(4, 5)


def row(sig, s):
    k = (1 - sig) * A
    e = s * th
    T = sig * A * k + s * th * e
    Pi = (1 - sig) * A * k + (1 - s) * th * e - k * k / 2
    U = T - e * e / 2
    return k, e, T, Pi, U, Pi + U


h = Fr(1, 2)
ok = row(0, 0) == (A, 0, 0, A**2 / 2, 0, A**2 / 2)
ok &= row(1, 1) == (0, th, th**2, 0, th**2 / 2, th**2 / 2)
ok &= row(0, h) == (A, th / 2, th**2 / 4, A**2 / 2 + th**2 / 4, th**2 / 8,
                    A**2 / 2 + 3 * th**2 / 8)
ok &= row(0, 1) == (A, th, th**2, A**2 / 2, th**2 / 2, (A**2 + th**2) / 2)
ok &= row(h, 1) == (A / 2, th, A**2 / 4 + th**2, A**2 / 8, A**2 / 4 + th**2 / 2,
                    3 * A**2 / 8 + th**2 / 2)
check("C12 Table 1, all five rows (exact)", ok)

# ----------------------------------------------------------------------------
# C13. Vanishing transfers under capturer control as theta/A -> 0
# ----------------------------------------------------------------------------
ok = True
A, delta = 1.0, 0.9
prev = None
for th in [1.0, 0.5, 0.1, 0.01, 0.001]:
    Y0 = A * A                                          # autonomous output
    shares = [0.0, (th**2 / 4) / Y0, (th**2 / 2) / Y0,
              (delta * th**2 / (2 * (1 - delta))) / Y0]
    if prev is not None:
        ok &= all(a <= b for a, b in zip(shares, prev))
    prev = shares
ok &= max(prev) < 1e-5
sg = sigma_star(3.0)
T_sep = sg * (1 - sg) * A * A                            # theta = 0
ok &= close(T_sep / ((1 - sg) * A * A), sg)
check("C13 capturer-controlled T/Y0 -> 0 as theta/A -> 0; separated share -> sigma*", ok)

# ----------------------------------------------------------------------------
width = max(len(n) for n, _, _ in RESULTS)
failed = 0
for name, ok, detail in RESULTS:
    print(f"{'PASS' if ok else 'FAIL'}  {name.ljust(width)}  {detail}")
    failed += (not ok)
print(f"\n{len(RESULTS) - failed}/{len(RESULTS)} checks passed")
sys.exit(1 if failed else 0)
