#!/usr/bin/env python3
"""
verify_bottleneck.py -- numerical and exact checks of every formula in

    "Binding at the Bottleneck:
     An Enforcement Model of Distribution after AI"

Requires Python 3 and numpy only. Each closed form stated in the paper is
checked either exactly, in rational arithmetic, or by brute-force optimisation
that does not use the closed form to locate the optimum. The script exits with
status 1 if any check fails.

Model
-----
Capturers        type A (mean mu, variance s2, A_min >= mu/2), compute k,
                 cost k^2/2, autonomous output A k
Rule             share sigma of output passing the output point,
                 levy tau per unit of compute passing the input point
Bypass           kappa per unit of output routed around the output point,
                 b per unit of compute routed around the input point
Payoffs          Pi = A k [1 - (1-h_o) sigma - h_o kappa]
                      - k [(1-h_i) tau + h_i b] - k^2/2
                 D  = E[ sigma (1-h_o) A k + tau (1-h_i) k ]
Setter           separated (commits in advance), maximises E[Pi] + omega D,
                 omega > 1
"""
import itertools
import math
import sys
from fractions import Fraction as Fr

import numpy as np

rng = np.random.default_rng(20261119)
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))


def close(a, b, tol=1e-6):
    return abs(a - b) <= tol * (1.0 + abs(a) + abs(b))


# ----------------------------------------------------------------------------
# Primitives
# ----------------------------------------------------------------------------
def sigma_star(w):
    return (w - 1) / (2 * w - 1)


def gamma_star(w):
    return (w - 1) ** 2 / (2 * (2 * w - 1))


def e(x):
    return x * (2 - x)


def make_types(kind, n=41):
    """Discrete type distributions with A_min >= mu/2. Returns (A, prob)."""
    if kind == "homog":
        return np.array([1.3]), np.array([1.0])
    if kind == "two":
        return np.array([0.8, 1.9]), np.array([0.7, 0.3])
    if kind == "unif":
        A = np.linspace(0.7, 1.6, n)
        return A, np.full(n, 1.0 / n)
    if kind == "skew":                      # right-skewed, truncated lognormal
        A = np.exp(np.linspace(-0.25, 1.0, n))
        p = np.exp(-0.5 * ((np.log(A) - 0.1) / 0.35) ** 2)
        p /= p.sum()
        mu = (A * p).sum()
        keep = A >= mu / 2
        A, p = A[keep], p[keep] / p[keep].sum()
        return A, p
    raise ValueError(kind)


def moments(A, p):
    mu = float((A * p).sum())
    s2 = float(((A - mu) ** 2 * p).sum())
    return mu, s2


def outcome(A, p, w, sig, tau, kap, b):
    """Equilibrium under rule (sig, tau) with bypass costs (kap, b).

    Uses the capturer's best response (checked separately in C1/C2):
    route all output iff sig > kap, route all compute iff tau > b.
    Returns (W, D, mean profit, k vector).
    """
    sig_eff = min(sig, kap)
    tau_eff = min(tau, b)
    k = np.maximum(0.0, (1 - sig_eff) * A - tau_eff)
    col = (sig * A * k if sig <= kap else 0.0) + (tau * k if tau <= b else 0.0)
    D = float((col * p).sum())
    Pi = float((k ** 2 / 2 * p).sum())
    return Pi + w * D, D, Pi, k


def predicted_rule(mu, w, kap, b):
    ss = sigma_star(w)
    sig = min(ss, kap)
    tau = min(b, max(0.0, mu * (ss - kap)))
    return sig, tau


# ----------------------------------------------------------------------------
# C1. Capturer's routing and investment, brute force over (k, h_o, h_i)
# ----------------------------------------------------------------------------
ok = True
worst = 0.0
hg = np.linspace(0, 1, 21)
for _ in range(300):
    A = rng.uniform(0.6, 2.5)
    sig, kap = rng.uniform(0.02, 0.6, size=2)
    tau, b = rng.uniform(0.02, 0.5, size=2)
    if abs(sig - kap) < 0.01 or abs(tau - b) < 0.01:
        continue
    kg = np.linspace(0, 3 * A, 6001)
    best = (-1e99, None)
    for ho, hi in itertools.product(hg, hg):
        pay = A * kg * (1 - (1 - ho) * sig - ho * kap) \
            - kg * ((1 - hi) * tau + hi * b) - kg ** 2 / 2
        j = int(np.argmax(pay))
        if pay[j] > best[0] + 1e-12:
            best = (pay[j], (kg[j], ho, hi))
    k_bf, ho_bf, hi_bf = best[1]
    k_cf = max(0.0, (1 - min(sig, kap)) * A - min(tau, b))
    ok &= ho_bf == (1.0 if sig > kap else 0.0) or k_cf == 0
    ok &= hi_bf == (1.0 if tau > b else 0.0) or k_cf == 0
    worst = max(worst, abs(k_bf - k_cf))
    ok &= abs(k_bf - k_cf) < 2e-3
check("C1  capturer routes all-or-nothing; k = (1-min(sig,kap))A - min(tau,b)", ok,
      f"max abs error in k {worst:.1e}")

# ----------------------------------------------------------------------------
# C2. A levy above the bypass cost collects nothing and is never optimal
# ----------------------------------------------------------------------------
ok = True
for kind in ["homog", "two", "unif", "skew"]:
    A, p = make_types(kind)
    for _ in range(200):
        w = rng.uniform(1.05, 8)
        kap, b = rng.uniform(0.02, 0.45), rng.uniform(0.02, 0.4)
        sig_hi = rng.uniform(kap + 1e-3, 1.0)
        tau_ok = rng.uniform(0, b)
        W_hi, D_hi, _, _ = outcome(A, p, w, sig_hi, tau_ok, kap, b)
        W_at, D_at, _, _ = outcome(A, p, w, kap, tau_ok, kap, b)
        ok &= W_at > W_hi and D_at > D_hi
        tau_hi = rng.uniform(b + 1e-3, 1.0)
        sig_ok = rng.uniform(0, kap)
        W_hi, D_hi, _, _ = outcome(A, p, w, sig_ok, tau_hi, kap, b)
        W_at, D_at, _, _ = outcome(A, p, w, sig_ok, b, kap, b)
        ok &= W_at > W_hi and D_at > D_hi
check("C2  Prop.1: levy above bypass cost is dominated by levy at the cost", ok)

# ----------------------------------------------------------------------------
# C3. Gain identity, exact:  W - E[A^2]/2 = E[(w-1) A x - (2w-1) x^2 / 2]
# ----------------------------------------------------------------------------
ok = True
for _ in range(1000):
    n = int(rng.integers(1, 6))
    A = [Fr(int(rng.integers(10, 30)), 10) for _ in range(n)]
    pr = [Fr(1, n)] * n
    w = Fr(int(rng.integers(11, 90)), 10)
    sig = Fr(int(rng.integers(0, 30)), 100)
    tau = Fr(int(rng.integers(0, 30)), 100)
    W = sum(q * (((1 - sig) * a - tau) ** 2 / 2 + w * (sig * a + tau) * ((1 - sig) * a - tau))
            for a, q in zip(A, pr))
    base = sum(q * a * a / 2 for a, q in zip(A, pr))
    G = sum(q * ((w - 1) * a * (sig * a + tau) - (2 * w - 1) * (sig * a + tau) ** 2 / 2)
            for a, q in zip(A, pr))
    ok &= W - base == G
    # gamma(sigma) = gamma* e(sigma/sigma*), exact
    ss = (w - 1) / (2 * w - 1)
    gs = (w - 1) ** 2 / (2 * (2 * w - 1))
    if sig > 0:
        x = sig / ss
        ok &= (w - 1) * sig - (2 * w - 1) * sig ** 2 / 2 == gs * x * (2 - x)
    ok &= gs == (w - 1) * ss / 2
check("C3  gain identity and gamma(sigma) = gamma* e(sigma/sigma*) (exact)", ok)

# ----------------------------------------------------------------------------
# C4. Proposition 1: output point only
# ----------------------------------------------------------------------------
ok = True
worst = 0.0
grid = np.linspace(0, 1, 20001)
for kind in ["homog", "two", "unif", "skew"]:
    A, p = make_types(kind)
    mu, s2 = moments(A, p)
    for w in [1.2, 1.5, 2.0, 4.0, 25.0]:
        for kap in [0.01, 0.05, 0.15, 0.3, 0.45, 0.8]:
            Ws = np.array([outcome(A, p, w, sg, 0.0, kap, 1e9)[0] for sg in grid])
            sg_bf = grid[int(np.argmax(Ws))]
            sg_cf = min(sigma_star(w), kap)
            worst = max(worst, abs(sg_bf - sg_cf))
            ok &= abs(sg_bf - sg_cf) < 2e-4
            D = outcome(A, p, w, sg_cf, 0.0, kap, 1e9)[1]
            ok &= close(D, sg_cf * (1 - sg_cf) * (mu ** 2 + s2))
            ok &= D <= kap * (mu ** 2 + s2) + 1e-12
check("C4  Prop.1: sigma_hat = min(sigma*, kappa); D = sigma_hat(1-sigma_hat)E[A^2]", ok,
      f"max abs error {worst:.1e}")

# D -> 0 as kappa -> 0 although the rule is separated
A, p = make_types("unif")
Ds = [outcome(A, p, 3.0, min(sigma_star(3.0), kp), 0.0, kp, 1e9)[1]
      for kp in [0.2, 0.1, 0.01, 0.001, 1e-5]]
check("C4b Prop.1: D decreases to 0 as kappa -> 0",
      all(a > b for a, b in zip(Ds, Ds[1:])) and Ds[-1] < 3e-5)

# ----------------------------------------------------------------------------
# C5. Proposition 2: invariance with identical capturers; bypass costs add
# ----------------------------------------------------------------------------
ok = True
A, p = make_types("homog")
mu = float(A[0])
for _ in range(2000):
    w = rng.uniform(1.05, 9)
    kap, b = rng.uniform(0.01, 0.4), rng.uniform(0.01, 0.4)
    # two rules with the same total wedge, both within the caps
    wedge = rng.uniform(0, min(kap * mu, b))
    r1 = outcome(A, p, w, wedge / mu, 0.0, kap, b)
    r2 = outcome(A, p, w, 0.0, wedge, kap, b)
    lam = rng.uniform(0, 1)
    r3 = outcome(A, p, w, lam * wedge / mu, (1 - lam) * wedge, kap, b)
    ok &= close(r1[0], r2[0]) and close(r1[1], r2[1]) and close(r1[0], r3[0]) \
        and close(r1[3][0], r2[3][0]) and close(r1[3][0], r3[3][0])
    # largest enforceable wedge is kap*mu + b, and the optimum uses t_hat
    t_hat = min(sigma_star(w), kap + b / mu)
    sig, tau = predicted_rule(mu, w, kap, b)
    W_cf, D_cf, _, _ = outcome(A, p, w, sig, tau, kap, b)
    ok &= close(sig * mu + tau, t_hat * mu)
    ok &= close(D_cf, t_hat * (1 - t_hat) * mu ** 2)
# brute force over the whole box, allowing levies above the caps
for w, kap, b in [(2.0, 0.1, 0.1), (3.0, 0.05, 0.2), (6.0, 0.2, 0.05), (1.5, 0.3, 0.3)]:
    sg = np.union1d(np.linspace(0, 0.7, 701), [kap])
    tg = np.union1d(np.linspace(0, 0.9, 901), [b])
    S = sg[:, None]
    T = tg[None, :]
    k = np.maximum(0.0, (1 - np.minimum(S, kap)) * mu - np.minimum(T, b))
    col = np.where(S <= kap, S * mu * k, 0.0) + np.where(T <= b, T * k, 0.0)
    best = (k ** 2 / 2 + w * col).max()
    sig, tau = predicted_rule(mu, w, kap, b)
    ok &= close(best, outcome(A, p, w, sig, tau, kap, b)[0], 1e-6)
check("C5  Prop.2: only the total wedge matters; caps add; D = t(1-t)mu^2", ok)

# ----------------------------------------------------------------------------
# C6. Proposition 3: the two-part rule, brute force over (sigma, tau)
# ----------------------------------------------------------------------------
def grid_W(A, p, w, kap, b, sg, tg):
    """W on the whole (sigma, tau) grid, levies above the caps included."""
    S = sg[:, None, None]
    T = tg[None, :, None]
    AA = A[None, None, :]
    k = np.maximum(0.0, (1 - np.minimum(S, kap)) * AA - np.minimum(T, b))
    col = np.where(S <= kap, S * AA * k, 0.0) + np.where(T <= b, T * k, 0.0)
    return ((k ** 2 / 2 + w * col) * p[None, None, :]).sum(axis=2)


ok = True
worst = 0.0
for kind in ["two", "unif", "skew"]:
    A, p = make_types(kind)
    mu, s2 = moments(A, p)
    for w in [1.3, 2.0, 3.5, 12.0]:
        ss = sigma_star(w)
        for kap in [0.02, 0.25 * ss, 0.6 * ss, 0.95 * ss, 1.4 * ss]:
            for b in [0.03 * mu, 0.3 * mu * ss, 5.0]:
                # the caps themselves are put on the grid: the optimum sits on them
                hs, ht = 0.6 / 600, 0.6 * mu / 600
                sg = np.union1d(np.linspace(0, 0.6, 601), [kap])
                tg = np.union1d(np.linspace(0, 0.6 * mu, 601), [min(b, 0.6 * mu)])
                Wm = grid_W(A, p, w, kap, b, sg, tg)
                i, j = np.unravel_index(int(np.argmax(Wm)), Wm.shape)
                sig, tau = predicted_rule(mu, w, kap, b)
                W_cf, D_cf, _, k_cf = outcome(A, p, w, sig, tau, kap, b)
                # the grid cannot beat the closed form, and comes as close to it
                # as the grid spacing allows (the objective is quadratic, so the
                # shortfall is bounded by its curvature times the spacing squared)
                q = 2 * w - 1
                tol = q / 2 * ((mu**2 + s2) * hs**2 + 2 * mu * hs * ht + ht**2)
                ok &= Wm[i, j] <= W_cf + 1e-9
                ok &= W_cf - Wm[i, j] <= tol
                worst = max(worst, abs(sg[i] - sig), abs(tg[j] - tau) / mu)
                ok &= abs(sg[i] - sig) <= 2 * hs and abs(tg[j] - tau) <= 2 * ht
                ok &= np.all(k_cf > 0)                      # every capturer stays active
                # closed forms
                x = min(1.0, kap / ss)
                gap = mu * (ss - min(kap, ss))
                z = 1.0 if gap <= 0 else min(1.0, b / gap)
                G_cf = gamma_star(w) * ((mu**2 + s2) * e(x) + mu**2 * (1 - x) ** 2 * e(z))
                base = float((A**2 / 2 * p).sum())
                ok &= close(W_cf - base, G_cf)
                if z == 1.0 and kap < ss:
                    ok &= close(D_cf, ss * (1 - ss) * mu**2 + kap * (1 - kap) * s2)
                    ok &= close(W_cf - base, gamma_star(w) * (mu**2 + e(x) * s2))
                    # loss against full enforcement
                    ok &= close(gamma_star(w) * (mu**2 + s2) - (W_cf - base),
                                gamma_star(w) * s2 * (1 - x) ** 2)
check("C6  Prop.3: sigma = min(sigma*,kappa), tau = min(b, mu(sigma*-kappa)); "
      "closed forms for gain and dividend", ok, f"max arg error {worst:.1e}")

# exact KKT check: at the predicted rule no feasible direction improves
ok = True
for _ in range(3000):
    n = int(rng.integers(2, 6))
    A = rng.uniform(0.8, 1.6, size=n)
    p = np.full(n, 1.0 / n)
    mu, s2 = moments(A, p)
    w = rng.uniform(1.05, 10)
    ss = sigma_star(w)
    kap = rng.uniform(0.0, 1.3) * ss
    b = rng.uniform(0.0, 0.7) * mu
    sig, tau = predicted_rule(mu, w, kap, b)
    q = 2 * w - 1
    dS = q * ((ss - sig) * (mu**2 + s2) - tau * mu)
    dT = q * ((ss - sig) * mu - tau)
    ok &= dS >= -1e-9 and dT >= -1e-9          # gradient points out of the box
    ok &= (sig >= min(kap, ss) - 1e-12) and (tau >= min(b, max(0, mu * (ss - kap))) - 1e-12)
    if sig < kap - 1e-12:
        ok &= abs(dS) < 1e-9
    if tau < b - 1e-12 and tau > 1e-12:
        ok &= abs(dT) < 1e-9
check("C6b Prop.3: KKT conditions hold at the two-part rule (3000 draws)", ok)

# ----------------------------------------------------------------------------
# C7. Corollary 1: if the rule can bind at one point only
# ----------------------------------------------------------------------------
ok = True
for kind in ["homog", "two", "unif", "skew"]:
    A, p = make_types(kind)
    mu, s2 = moments(A, p)
    cv2 = s2 / mu**2
    base = float((A**2 / 2 * p).sum())
    for _ in range(400):
        w = rng.uniform(1.1, 9)
        ss = sigma_star(w)
        kap = rng.uniform(0.0, 1.3) * ss
        b = rng.uniform(0.0, 1.3) * mu * ss
        x, y = min(1.0, kap / ss), min(1.0, b / (mu * ss))
        G_out = outcome(A, p, w, min(ss, kap), 0.0, kap, 1e9)[0] - base
        G_in = outcome(A, p, w, 0.0, min(b, ss * mu), 1e9, b)[0] - base
        ok &= close(G_out, gamma_star(w) * (mu**2 + s2) * e(x))
        ok &= close(G_in, gamma_star(w) * mu**2 * e(y))
        if abs(e(y) - (1 + cv2) * e(x)) > 1e-9:
            ok &= (G_in > G_out) == (e(y) > (1 + cv2) * e(x))
        # threshold when the bottleneck is fully enforceable
        cv = math.sqrt(cv2)
        xbar = 1 - cv / math.sqrt(1 + cv2)
        G_in1 = gamma_star(w) * mu**2
        if abs(x - xbar) > 1e-9 and x < 1:
            ok &= (G_in1 > G_out) == (x < xbar)
check("C7  Cor.1: bottleneck beats output iff e(y) > (1+cv^2) e(x); "
      "threshold 1 - cv/sqrt(1+cv^2)", ok)
check("C7b figure: crossing at kappa/sigma* = 0.4 when cv = 0.75",
      close(1 - 0.75 / math.sqrt(1 + 0.75**2), 0.4))

# ----------------------------------------------------------------------------
# C8. Assumption: A_min >= mu/2 keeps every capturer active at the optimum
# ----------------------------------------------------------------------------
ok = True
for _ in range(20000):
    mu = rng.uniform(0.5, 3)
    Amin = mu / 2
    w = rng.uniform(1.0001, 1e3)
    ss = sigma_star(w)
    kap = rng.uniform(0, 1)
    b = rng.uniform(0, 3)
    sig, tau = predicted_rule(mu, w, kap, b)
    ok &= (1 - sig) * Amin - tau > 0
check("C8  A_min >= mu/2 implies k > 0 for all types under the optimal rule", ok)

# ----------------------------------------------------------------------------
# C9. Footnote: convex bypass cost kappa h^2/2 per unit; collected share <= kappa/4
# ----------------------------------------------------------------------------
ok = True
hgrid = np.linspace(0, 1, 200001)
for _ in range(200):
    kap = rng.uniform(0.05, 1.0)
    sig = rng.uniform(0.0, kap)
    pay = -(1 - hgrid) * sig - kap * hgrid**2 / 2      # per unit of output
    h_bf = hgrid[int(np.argmax(pay))]
    ok &= abs(h_bf - sig / kap) < 1e-4
    sg = np.linspace(0, kap, 20001)
    col = sg * (1 - sg / kap)
    ok &= close(col.max(), kap / 4, 1e-6) and abs(sg[int(np.argmax(col))] - kap / 2) < 1e-3
check("C9  convex bypass: h = sigma/kappa, collected share sigma(1-sigma/kappa) <= kappa/4", ok)

# ----------------------------------------------------------------------------
# C10. Proposition 4: a common floor adds to the bypass cost
# ----------------------------------------------------------------------------
ok = True
for _ in range(5000):
    sig, phi, kap = rng.uniform(0, 1, size=3)
    stay = 1 - sig                      # net return per unit if it complies
    move = 1 - phi - kap                # relocates, pays the floor elsewhere
    if abs(stay - move) > 1e-9:
        ok &= (stay > move) == (sig < phi + kap)
check("C10 Prop.4: capturer complies iff sigma <= phi + kappa", ok)

# ----------------------------------------------------------------------------
# C11. Proposition 5: the owner of the bottleneck (identical capturers)
# ----------------------------------------------------------------------------
ok = True
for mu in [0.8, 1.0, 1.7]:
    mg = np.linspace(0, mu, 400001)
    # (i) no rule: monopoly price mu/2, revenue mu^2/4
    rev = mg * (mu - mg)
    m_bf = mg[int(np.argmax(rev))]
    ok &= abs(m_bf - mu / 2) < 1e-5 and close(rev.max(), mu**2 / 4)
    # recipients' own bottleneck levy: maximise tau (mu - tau) -> the same number
    ok &= close((mg * (mu - mg)).max(), mu**2 / 4)
    # and it is the limit of the setter's levy sigma*(w) mu as w -> infinity
    ok &= close(sigma_star(1e12) * mu, mu / 2)
    # (ii) levy tau on top: m = (mu - tau)/2, D = tau (mu - tau)/2 <= mu^2/8
    for tau in np.linspace(0, 0.9 * mu, 10):
        revB = mg * np.maximum(0.0, mu - tau - mg)
        ok &= abs(mg[int(np.argmax(revB))] - (mu - tau) / 2) < 1e-5
    tg = np.linspace(0, mu, 400001)
    Dg = tg * (mu - tg) / 2
    ok &= close(Dg.max(), mu**2 / 8) and abs(tg[int(np.argmax(Dg))] - mu / 2) < 1e-5
    for w in [1.0, 1.2, 1.5, 1.6, 2.0, 5.0, 100.0]:
        k = (mu - tg) / 2
        obj = k**2 / 2 + k * k + w * tg * k            # capturer + owner + w * dividend
        t_bf = tg[int(np.argmax(obj))]
        t_cf = mu * (2 * w - 3) / (4 * w - 3) if w > 1.5 else 0.0
        ok &= abs(t_bf - t_cf) < 1e-5
    # (iii) a share rho of the owner's revenue leaves its price unchanged
    for rho in [0.0, 0.2, 0.5, 0.9]:
        for tau in [0.0, 0.3 * mu]:
            revB = (1 - rho) * mg * np.maximum(0.0, mu - tau - mg)
            ok &= abs(mg[int(np.argmax(revB))] - (mu - tau) / 2) < 1e-5
check("C11 Prop.5: owner charges mu/2 and earns mu^2/4; levy on top yields at most "
      "mu^2/8; tau = mu(2w-3)/(4w-3); revenue share is neutral", ok)

# the owner's toll equals the recipients' entry in Table 1 of the companion paper
check("C11b Prop.5(i): owner's revenue = recipients' dividend A^2/4 of the companion paper",
      all(close((0.5 * A_) * (A_ - 0.5 * A_), A_**2 / 4) for A_ in [0.7, 1.0, 2.3]))

# ----------------------------------------------------------------------------
# C12. Numbers quoted in the text and in Figure 1
# ----------------------------------------------------------------------------
cv = 0.75
share_in = 1 / (1 + cv**2)
ok = close(share_in, 0.64)
ok &= close((1 + cv**2 * e(0.4)) / (1 + cv**2), 0.64 + 0.36 * 0.64)
ok &= close(e(0.4), 0.64)                                 # the two single-point rules tie
ok &= close(1 - 1 / math.sqrt(2), 0.2929, 1e-3)           # cv = 1
# worked example in Section 3.3: omega = 2, cv = 0.75, kappa = 0.1
ss_ex = sigma_star(2.0)
x_ex = 0.1 / ss_ex
ok &= close(ss_ex, 1 / 3) and close(x_ex, 0.3)
ok &= round(100 * e(x_ex)) == 51                           # output point alone
ok &= round(100 / (1 + cv**2)) == 64                       # bottleneck alone
ok &= round(100 * (1 + cv**2 * e(x_ex)) / (1 + cv**2)) == 82   # two-part rule
# Alaska 2025: paid 1,000 against a formula of about 3,900 -> "about a quarter"
ok &= abs(1000 / 3900 - 0.25) < 0.01
# royalties: 28,000 -> 2,000 ETH per week
ok &= 1 - 2000 / 28000 > 0.9
check("C12 figure, worked example and other numbers quoted in the text", ok)

# ----------------------------------------------------------------------------
width = max(len(n) for n, _, _ in RESULTS)
failed = 0
for name, ok, detail in RESULTS:
    print(f"{'PASS' if ok else 'FAIL'}  {name.ljust(width)}  {detail}")
    failed += (not ok)
print(f"\n{len(RESULTS) - failed}/{len(RESULTS)} checks passed")
sys.exit(1 if failed else 0)
