"""
research_utils.py — a library of reusable functions for the UK49s
research project.
Goal: test a new hypothesis in 2-3 lines, without rewriting boilerplate.

Example usage:
    from research_utils import *
    draws, dates = load_draws("Uk49s_master_2021_2026.csv")
    groups = build_groups()
    diffs = quarter_check(draws, groups['C3'], groups['K10'])
    d, p = train_test_check(draws, groups['C3'], groups['K10'])
"""

import csv
import math
import random
from datetime import datetime
from collections import Counter
from itertools import combinations


# ============================================================
#  DATA LOADING
# ============================================================

def load_draws(csv_path, start_date="2026-01-27", end_date=None):
    """Returns (draws, dates) — lists of draws (list[int]) and dates
    (str), filtered to the current regime's start date."""
    start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
    end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
    draws, dates = [], []
    with open(csv_path, encoding="utf-8") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) < 7:
                continue
            d = datetime.strptime(row[0].strip(), "%Y-%m-%d")
            if start and d < start:
                continue
            if end and d > end:
                continue
            draws.append([int(x) for x in row[1:7]])
            dates.append(row[0].strip())
    return draws, dates


# ============================================================
#  GROUPS (K, R, C) — the standard 7×7 grid
# ============================================================

def build_groups():
    """Returns dict {name: set(numbers)} for K1-K10, R1-R7, C1-C7."""
    K = {f"K{i}": set(range((i - 1) * 5 + 1, i * 5 + 1)) for i in range(1, 10)}
    K["K10"] = set(range(46, 50))
    R = {f"R{r}": set(n for n in range(1, 50) if (n - 1) // 7 + 1 == r) for r in range(1, 8)}
    C = {f"C{c}": set(n for n in range(1, 50) if (n - 1) % 7 + 1 == c) for c in range(1, 8)}
    return {**K, **R, **C}


# ============================================================
#  BASIC INDICATORS
# ============================================================

def hit_series(draws, members):
    """0/1 series: whether at least 1 group member appears in each draw."""
    return [1 if (set(d) & members) else 0 for d in draws]


def thickness_series(draws, members):
    """Group thickness (0-7) in each draw."""
    return [len(set(d) & members) for d in draws]


def state_streak(draws, t, members):
    """Current unbroken streak (sum of thickness) up to and including
    draw t, counted backward in time."""
    total = 0
    tt = t
    while tt >= 0 and (set(draws[tt]) & members):
        total += len(set(draws[tt]) & members)
        tt -= 1
    return total


def just_ended_saturated(draws, t, members):
    """Whether draw t itself just ended a saturated streak (the streak
    broke at t, and the sum of the preceding streak >= group size)."""
    if t == 0 or (set(draws[t]) & members):
        return False
    size = len(members)
    tt = t - 1
    total = 0
    while tt >= 0 and (set(draws[tt]) & members):
        total += len(set(draws[tt]) & members)
        tt -= 1
    return total >= size


def series_list(draws, members):
    """List of streaks (list of list[int] draw indices) for a group."""
    thick = thickness_series(draws, members)
    cur, out = [], []
    for t, th in enumerate(thick):
        if th >= 1:
            cur.append(t)
        else:
            if cur:
                out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def saturation_rate(draws, members):
    """Fraction of streaks that reach full saturation (sum >= group size)."""
    size = len(members)
    thick = thickness_series(draws, members)
    series = series_list(draws, members)
    if not series:
        return 0.0
    sat = sum(1 for s in series if sum(thick[t] for t in s) >= size)
    return sat / len(series)


# ============================================================
#  HYPOTHESIS TESTING: QUARTERS, TRAIN/TEST, SIGNIFICANCE
# ============================================================

def conditional_diff(draws, x_members, y_members):
    """(hit-rate of Y when X=0) - (hit-rate of Y when X>=1), in
    percentage points. This is the project's standard "X->Y" check."""
    x_hit = hit_series(draws, x_members)
    y_hit = hit_series(draws, y_members)
    z = [y for x, y in zip(x_hit, y_hit) if x == 0]
    a = [y for x, y in zip(x_hit, y_hit) if x == 1]
    if not z or not a:
        return None
    return (sum(z) / len(z) - sum(a) / len(a)) * 100


def quarter_check(draws, x_members, y_members, n_quarters=4):
    """conditional_diff computed separately in each of n_quarters
    equal parts of the time series. Returns a list of values (None
    if a part doesn't have enough data)."""
    n = len(draws)
    q = n // n_quarters
    out = []
    for i in range(n_quarters):
        s = i * q
        e = (i + 1) * q if i < n_quarters - 1 else n
        out.append(conditional_diff(draws[s:e], x_members, y_members))
    return out


def train_test_check(draws, x_members, y_members):
    """conditional_diff on the first and second half of the data.
    Returns (train_diff, test_diff) — if the signs differ, that's a
    sign of noise, not a real relationship."""
    n = len(draws)
    split = n // 2
    return (conditional_diff(draws[:split], x_members, y_members),
            conditional_diff(draws[split:], x_members, y_members))


def binom_pvalue(successes, trials, expected_p):
    """p-value of a one-sided binomial test (more successes than
    expected). No scipy dependency — implemented directly."""
    from math import comb
    p_val = sum(comb(trials, k) * expected_p ** k * (1 - expected_p) ** (trials - k)
                for k in range(successes, trials + 1))
    return p_val


def theoretical_hitrate(group_size, draw_size=6, total=49):
    """P(at least 1 group member appears in a draw) — exact
    hypergeometric calculation."""
    from math import comb
    p_zero = comb(total - group_size, draw_size) / comb(total, draw_size)
    return 1 - p_zero


# ============================================================
#  EVALUATING PREDICTION POOLS VIA P(>=3)/P(>=4)/P(>=5)
#  (clarified 2026-09-11, following cycles #56-#58): for ANY
#  hypothesis that evaluates an algorithm/"motor"/core+complement
#  against the actual draw, the MEAN hit count is the WRONG primary
#  metric — it mixes 0/1/2 hits (which have no value) with 3+/4+/5+
#  hits (which are the actual goal). Use THESE functions as the
#  primary stat_fn instead.
# ============================================================

def theoretical_p_ge(K, k_min, draw_size=6, total=49):
    """Exact hypergeometric P(hits >= k_min) for a prediction pool of
    size K against a draw of draw_size out of total.
    Example: theoretical_p_ge(8, 4) -> the exact P(>=4) for an
    8-number prediction pool — the theoretical baseline for comparison."""
    from math import comb
    return sum(comb(K, j) * comb(total - K, draw_size - j) / comb(total, draw_size)
               for j in range(k_min, draw_size + 1) if j <= K)


def empirical_p_ge(predicted_sets, actual_sets, k_min):
    """Empirical fraction of draws where |predicted ∩ actual| >= k_min.
    predicted_sets, actual_sets — lists of set() of equal length
    (one prediction and one actual result per tested draw)."""
    n = len(predicted_sets)
    if n == 0:
        return None
    hits = [len(p & a) for p, a in zip(predicted_sets, actual_sets)]
    return sum(1 for h in hits if h >= k_min) / n


def predictor_null_check(predicted_sets, K, k_min, n_trials=300, seed=None,
                          total=49, draw_size=6):
    """A null model specifically for P(>=k_min): the predicted sets
    (already generated by the algorithm) stay FIXED, and a random
    draw is simulated instead of the real one. Returns a dict in the
    same format as null_model_check() (real_value, p_value_two_sided,
    percentile, verdict), but the statistic is the P(>=k_min)
    fraction, not the mean."""
    import random
    n = len(predicted_sets)
    rng = random.Random(seed)
    real_hits = None  # computed below only if actual_sets are supplied
                        # externally — this function expects the caller
                        # to compute real_value via
                        # empirical_p_ge(predicted, actual, k_min)
    null_values = []
    for _ in range(n_trials):
        sim_actuals = [set(rng.sample(range(1, total + 1), draw_size)) for _ in range(n)]
        v = empirical_p_ge(predicted_sets, sim_actuals, k_min)
        null_values.append(v)
    null_values.sort()
    return null_values  # sorted list, for comparison against the real value


# ============================================================
#  OPPOSITE-PAIR SEARCH (same as in the live algorithm, with a threshold)
# ============================================================

def rolling_mean(series, window):
    out = [None] * len(series)
    acc = 0
    for i, v in enumerate(series):
        acc += v
        if i >= window:
            acc -= series[i - window]
        if i >= window - 1:
            out[i] = acc / window
    return out


def find_opposite_pairs(draws, groups, threshold=0.92, max_pairs=3, corr_window=None):
    """Find group pairs whose correlation is stronger than -threshold.
    groups: dict {name: set}. Returns a list of (X, Y) in both
    directions: if X=0 -> bonus for Y."""
    names = list(groups.keys())
    n = len(draws)
    cw = corr_window or max(5, n // 3)
    rolls = {g: rolling_mean(hit_series(draws, groups[g]), cw) for g in names}

    pair_corrs = []
    for g1, g2 in combinations(names, 2):
        if groups[g1] & groups[g2]:
            continue  # structural overlap — skip
        xs, ys = [], []
        for a, b in zip(rolls[g1], rolls[g2]):
            if a is not None and b is not None:
                xs.append(a); ys.append(b)
        if len(xs) < 4:
            continue
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        vx = sum((x - mx) ** 2 for x in xs)
        vy = sum((y - my) ** 2 for y in ys)
        if vx == 0 or vy == 0:
            continue
        corr = cov / math.sqrt(vx * vy)
        if corr == corr and corr < -threshold:
            pair_corrs.append((g1, g2, corr))

    pair_corrs.sort(key=lambda x: x[2])
    pairs = []
    for g1, g2, c in pair_corrs[:max_pairs]:
        pairs.append((g1, g2))
        pairs.append((g2, g1))
    return pairs


# ============================================================
#  MANDATORY NULL MODEL — nothing is considered confirmed without
#  this step. The 2026-09-10 session showed that recurring
#  correlation, Moran's I, lagged cross-correlation — all of these
#  can look "convincing" even on pure noise if not compared against
#  a null model.
# ============================================================

def null_model_check(real_draws, stat_fn, n_trials=200, seed=None,
                      total=49, draw_size=6):
    """Universal check of any statistic against purely random draws
    of the same size.

    real_draws: list of draws (list[int]) — the real data
    stat_fn(draws) -> float: any statistic being computed
        (correlation, hit-rate, variance, anything — the only
        requirement is that the function takes a list of draws and
        returns a single number)
    n_trials: how many random simulations (200-500 is usually enough)

    Returns a dict:
        real_value          — the real value of the statistic
        null_values          — a sorted list of n_trials simulated values
        p_value_two_sided     — fraction of simulations where |null| >= |real| (lower is stronger)
        percentile            — which percentile of the null distribution real_value falls at
        verdict               — 'CONFIRMED' if p<0.05, otherwise 'NOISE-LIKE'

    MUST be called for EVERY new hypothesis based on correlation,
    variance, or any "nice-looking number," before logging a
    conclusion as confirmed.
    """
    n = len(real_draws)
    real_value = stat_fn(real_draws)
    rng = random.Random(seed)
    null_values = []
    for _ in range(n_trials):
        sim = [rng.sample(range(1, total + 1), draw_size) for _ in range(n)]
        try:
            v = stat_fn(sim)
        except Exception:
            continue
        if v is not None:
            null_values.append(v)

    if not null_values:
        return {"real_value": real_value, "null_values": [], "p_value_two_sided": None,
                "percentile": None, "verdict": "INSUFFICIENT_DATA"}

    null_values.sort()
    abs_real = abs(real_value)
    n_exceed = sum(1 for v in null_values if abs(v) >= abs_real)
    p_value = n_exceed / len(null_values)
    below = sum(1 for v in null_values if v < real_value)
    percentile = below / len(null_values) * 100

    verdict = "CONFIRMED" if p_value < 0.05 else "NOISE-LIKE"
    return {
        "real_value": real_value,
        "null_values": null_values,
        "p_value_two_sided": p_value,
        "percentile": percentile,
        "verdict": verdict,
    }


def bonferroni_note(n_hypotheses_this_session, alpha=0.05):
    """How many hypotheses have been tested across the ENTIRE history
    of this automation run — the significance threshold needs to
    shrink proportionally, or sooner or later something will get
    "confirmed" purely by chance (the multiple comparisons problem).
    Use this as a reference threshold when evaluating a p_value from
    null_model_check: if p_value > adjusted_alpha, it's not confirmed,
    even if the raw p_value is < 0.05."""
    adjusted_alpha = alpha / max(1, n_hypotheses_this_session)
    return {
        "n_hypotheses": n_hypotheses_this_session,
        "raw_alpha": alpha,
        "adjusted_alpha": adjusted_alpha,
    }
