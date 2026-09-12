#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UK49s thread-based algorithm backtest — version 2.
Base: 123.py (group structure, GroupState, tie-breaking, hypergeometrics).

Changes relative to 123.py:
  1. Removed the STATIC hardcoded rules (C3-K10, C2-C6, K6-R7 forever).
     Replaced with LIVE, ROLLING RECALIBRATION: every RECALIB_STEP
     draws, the strongest opposite pairs are re-searched on a window
     of the last ROLLING WINDOW draws. The size of this window is
     itself chosen adaptively from CANDIDATE_WINDOWS using the same
     principle as the "Motor A/B" experiments (whichever window gave
     the better result on the recent past is the one used).
  2. C3_BIAS_WEIGHT default changed from 2.5 to 1.0 — 2.5 gave a
     better P(k>=3) but a worse P(k>=4), and was not optimal on a
     genuinely held-out second half of the data (train/test check).
  3. Removed CALIBRATION_WINDOW / CALIBRATION_PERCENTILE (a dynamic
     thickness threshold) — a separate, unrelated, unverified branch
     that confused the main idea. The "hot shot" threshold is always
     fixed at 3.

Runs with no external dependencies (standard Python only).
"""

import csv
import os
import sys
import math
import random
from datetime import datetime
from collections import defaultdict
from itertools import combinations

# ============================================================
#  SETTINGS (EDIT HERE)
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "Uk49s_master_2021_2026.csv")

N_BACKTEST = 900          # number of most recent draws to backtest
                          # (used only if BACKTEST_ANCHOR_DATE=None)
TOP_N = 8                # how many numbers to output in the prediction

# --- Fixed backtest anchor point (for reproducibility) ---
# Problem: "the last 800 draws" shifts forward every day, since new
# draws get added daily — so the same N_BACKTEST=800 gives a slightly
# different result each day (checked: the spread isn't dramatic,
# 1.09-1.13 average at depths 700-880, but still not identical).
# To compare results across different days fairly, apples-to-apples,
# the backtest end date can be pinned to a specific date instead of
# "the last N draws from today." If BACKTEST_ANCHOR_DATE=None, the
# old approach is used (N_BACKTEST counted back from the end of the
# file).
BACKTEST_ANCHOR_DATE = None   # e.g. "2026-09-04", or None

# --- New-regime filter (from 2026-01-27) ---
USE_NEW_MODE_ONLY = True
NEW_MODE_START = "2026-01-27"

# --- Tie-breaking ---
TIE_BREAKER = 'last_thickness'   # 'last_thickness', 'random', 'number'

# --- Bias weight toward C3 ---
# 0.0 = no bias. 1.0-1.5 = a moderate bias, confirmed on train/test
# (a better balance of P(k>=3) and P(k>=4) than 2.5).
C3_BIAS_WEIGHT = 1.5

# --- Live forecast / forward test ---
SLOW_WINDOW = 100         # slow window for the balance-shift monitor
                          # (separate from the fast RECALIB_WINDOW=10)
SHOW_LAST_N = 10          # show a step-by-step result for the last
                          # N draws (0/1/2/3... hits for each)

# Verified empirically (several runs with different windows): 10 is
# the most stable and best recalibration window. Adaptively choosing
# among several sizes (10/20/30/50) added nothing over a simple fixed
# window of 10 — so this was simplified to one fixed value.
RECALIB_WINDOW = 10     # window size for re-searching pairs each time
LOOKBACK = 100           # (kept for compatibility, not used directly
                         # with a fixed window)
RECALIB_STEP = 100      # how often (once every how many draws) to search for new rules
N_TOP_PAIRS = 4 # maximum number of pairs allowed to pass the threshold at once
                          # (confirmed empirically as better than 2 or 4)
CORR_THRESHOLD = 0.95    # a "rounding" threshold — a pair only counts
                          # if |correlation| exceeds this; weaker
                          # signals are discarded entirely (this can
                          # leave 0 pairs for some stretch — that's
                          # expected and intentional: backtesting
                          # confirmed that "bet on nothing" beats
                          # "bet on a weak, uncertain signal").
HOT_THRESHOLD_FIXED = 3  # "hot shot" threshold (thickness in 1 draw)

# ============================================================
#  GROUPS (K, R, C) — DO NOT CHANGE
# ============================================================

K_GROUPS = {
    'K1': list(range(1, 6)), 'K2': list(range(6, 11)), 'K3': list(range(11, 16)),
    'K4': list(range(16, 21)), 'K5': list(range(21, 26)), 'K6': list(range(26, 31)),
    'K7': list(range(31, 36)), 'K8': list(range(36, 41)), 'K9': list(range(41, 46)),
    'K10': list(range(46, 50)),
}
R_GROUPS = {f'R{r+1}': list(range(r*7+1, (r+1)*7+1)) for r in range(7)}
C_GROUPS = {f'C{c+1}': list(range(c+1, 50, 7)) for c in range(7)}
ALL_GROUPS = {**K_GROUPS, **R_GROUPS, **C_GROUPS}
GROUP_SIZE = {name: len(nums) for name, nums in ALL_GROUPS.items()}
GROUP_SET = {name: set(nums) for name, nums in ALL_GROUPS.items()}
NUM_TO_GROUPS = defaultdict(list)
for gname, nums in ALL_GROUPS.items():
    for n in nums:
        NUM_TO_GROUPS[n].append(gname)
GROUP_NAMES = list(ALL_GROUPS.keys())
# pairs of groups that do NOT physically overlap (to avoid confusing a
# result with a subset artifact)
DISJOINT_PAIRS = [(g1, g2) for g1, g2 in combinations(GROUP_NAMES, 2)
                   if not (GROUP_SET[g1] & GROUP_SET[g2])]

# ============================================================
#  GROUP STATE CLASS
# ============================================================

class GroupState:
    def __init__(self, size):
        self.size = size
        self.streak = 0
        self.cum_sum = 0
        self.seen = set()
        self.last_thickness = 0
        self.ended_saturated = False

    def update(self, thickness, drawn_numbers):
        self.last_thickness = thickness
        if thickness > 0:
            self.streak += 1
            self.cum_sum += thickness
            self.seen.update(drawn_numbers)
            self.ended_saturated = False
        else:
            if self.streak > 0:
                self.ended_saturated = (self.cum_sum >= self.size)
                self.streak = 0
                self.cum_sum = 0
                self.seen.clear()
            else:
                self.ended_saturated = False

    @property
    def is_active(self):
        return self.streak > 0


# ============================================================
#  LIVE RULE RECALIBRATION
# ============================================================

def hit_series(gname, draws_slice):
    """0/1 series: whether at least 1 group member appears in each
    draw of the slice."""
    s = GROUP_SET[gname]
    return [1 if (s & draws_slice[i]) else 0 for i in range(len(draws_slice))]


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


def find_top_pairs(calib_draws_sets, n_top=N_TOP_PAIRS, threshold=CORR_THRESHOLD):
    """Find the strongest NEGATIVELY correlated (opposite) group pairs
    on the given slice of draws, "rounding off" (discarding) anything
    weaker than `threshold`. Returns a list of (X, Y) in both
    directions: if X=0 -> bonus for Y. May return an empty list — this
    is intentional: when no signal reaches the confidence threshold,
    it's better to bet on nothing than to rely on a weak, uncertain
    pair."""
    corr_win = max(5, len(calib_draws_sets) // 3)
    rolls = {g: rolling_mean(hit_series(g, calib_draws_sets), corr_win) for g in GROUP_NAMES}

    pair_corrs = []
    for g1, g2 in DISJOINT_PAIRS:
        r1, r2 = rolls[g1], rolls[g2]
        xs, ys = [], []
        for a, b in zip(r1, r2):
            if a is not None and b is not None:
                xs.append(a); ys.append(b)
        if len(xs) < 4:
            continue
        mx = sum(xs) / len(xs); my = sum(ys) / len(ys)
        cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        vx = sum((x - mx) ** 2 for x in xs); vy = sum((y - my) ** 2 for y in ys)
        if vx == 0 or vy == 0:
            continue
        corr = cov / math.sqrt(vx * vy)
        if corr != corr:  # NaN guard
            continue
        if corr < -threshold:   # "rounding": keep only confidently negative
            pair_corrs.append((g1, g2, corr))

    pair_corrs.sort(key=lambda x: x[2])  # most negative first
    pairs = []
    for g1, g2, c in pair_corrs[:n_top]:
        pairs.append((g1, g2))
        pairs.append((g2, g1))
    return pairs


def evaluate_window_choice(draws_sets, end_idx, window, lookback, pool=TOP_N):
    """Retrospectively check: if recalibration had used window `window`
    throughout the last `lookback` draws (ending at end_idx), what
    average hit-rate would that have given? Used for adaptively
    choosing the window size (as in the Motor A/B experiments)."""
    start = max(window, end_idx - lookback)
    if end_idx - start < window:
        return 0.0, 0
    states = {g: GroupState(GROUP_SIZE[g]) for g in GROUP_NAMES}
    # warm up the state from the start of history up to `start` (without recording hits)
    for i in range(0, start):
        for g in GROUP_NAMES:
            draw_in_g = [x for x in draws_sets[i] if x in GROUP_SET[g]]
            states[g].update(len(draw_in_g), draw_in_g)

    hits = []
    t = start
    pairs = find_top_pairs(draws_sets[max(0, t - window):t], N_TOP_PAIRS)
    next_recalib = t + window
    for i in range(start, end_idx):
        if i >= next_recalib:
            pairs = find_top_pairs(draws_sets[max(0, i - window):i], N_TOP_PAIRS)
            next_recalib = i + window
        group_scores = compute_group_scores(states, pairs, HOT_THRESHOLD_FIXED, 0.0)
        num_scores = compute_number_scores(group_scores)
        top = sorted(num_scores.items(), key=lambda x: (x[1], x[0]), reverse=True)[:pool]
        predicted = set(n for n, _ in top)
        hits.append(len(predicted & draws_sets[i]))
        for g in GROUP_NAMES:
            draw_in_g = [x for x in draws_sets[i] if x in GROUP_SET[g]]
            states[g].update(len(draw_in_g), draw_in_g)
    return (sum(hits) / len(hits) if hits else 0.0), len(hits)


def choose_best_window(draws_sets, end_idx, candidate_windows, lookback):
    best_w, best_perf = candidate_windows[0], -1.0
    for w in candidate_windows:
        perf, n = evaluate_window_choice(draws_sets, end_idx, w, lookback)
        if n > 0 and perf > best_perf:
            best_perf, best_w = perf, w
    return best_w


# ============================================================
#  SLOW BALANCE-SHIFT MONITOR (separate from the fast window=10)
# ============================================================
#  The fast window (RECALIB_WINDOW=10) catches the instantaneous
#  state, but doesn't show the fact that a specific pair's strength
#  is systematically rising or falling over months (see the reference
#  doc: C3-K10 weakened in April 2026, C2-C6 sharply strengthened in
#  July-August 2026). This function computes the same conditional
#  difference (X=0 -> bonus for Y), but on a slow window
#  (SLOW_WINDOW=100), and compares it to the previous such window, to
#  show the DIRECTION of change in the rule's strength over time.

def conditional_diff(x_gname, y_gname, draws_sets):
    x_hit = hit_series(x_gname, draws_sets)
    y_hit = hit_series(y_gname, draws_sets)
    z_vals = [y for x, y in zip(x_hit, y_hit) if x == 0]
    a_vals = [y for x, y in zip(x_hit, y_hit) if x == 1]
    if not z_vals or not a_vals:
        return None
    return (sum(z_vals) / len(z_vals) - sum(a_vals) / len(a_vals)) * 100


def slow_balance_monitor(draws_sets, end_idx, pairs_to_watch, slow_window=SLOW_WINDOW):
    """For each pair (X,Y) in pairs_to_watch: compute the strength of
    the rule X->Y on two consecutive slow windows (the one just past,
    and the one before it), and show the direction of change."""
    results = []
    recent_start = max(0, end_idx - slow_window)
    prior_start = max(0, end_idx - 2 * slow_window)
    recent_slice = draws_sets[recent_start:end_idx]
    prior_slice = draws_sets[prior_start:recent_start]
    for x, y in pairs_to_watch:
        recent_val = conditional_diff(x, y, recent_slice) if len(recent_slice) >= 20 else None
        prior_val = conditional_diff(x, y, prior_slice) if len(prior_slice) >= 20 else None
        trend = None
        if recent_val is not None and prior_val is not None:
            trend = recent_val - prior_val
        results.append((x, y, prior_val, recent_val, trend))
    return results


# ============================================================
#  SCORING
# ============================================================

def compute_group_scores(states, pairs, hot_threshold, c3_bias):
    scores = defaultdict(int)
    for x, y in pairs:
        if not states[x].is_active:
            scores[y] += 1
    for name, st in states.items():
        if st.last_thickness >= hot_threshold:
            scores[name] += 1
    for name, st in states.items():
        if st.ended_saturated:
            scores[name] -= 1
    if c3_bias != 0.0:
        scores['C3'] += c3_bias
    return scores


def compute_number_scores(group_scores):
    return {n: sum(group_scores.get(g, 0) for g in NUM_TO_GROUPS[n]) for n in range(1, 50)}


# ============================================================
#  BACKTEST WITH LIVE RECALIBRATION
# ============================================================

def run_backtest(draws, n_backtest, top_n, tie_breaker, c3_bias):
    total = len(draws)
    eval_start = total - n_backtest
    if eval_start < 0:
        raise ValueError("n_backtest is larger than the number of draws")

    draws_sets = [set(d) for d in draws]
    states = {name: GroupState(GROUP_SIZE[name]) for name in ALL_GROUPS}
    hit_counts = []
    windows_used = []
    details = []  # (index, actual draw, predicted pool, hit count)

    current_window = RECALIB_WINDOW
    current_pairs = []
    next_recalib_idx = -1

    for i, draw_numbers in enumerate(draws):
        # --- pair recalibration — ALWAYS on an absolute schedule (0, RECALIB_STEP, 2*RECALIB_STEP, ...)
        # IMPORTANT: pulled out from under "if i >= eval_start" so that the
        # recalibration schedule doesn't depend on n_backtest. Otherwise, for
        # the same final draws, current_pairs (and hence the prediction)
        # would differ depending on which backtest depth (n_backtest) was
        # chosen — the same bug that was found and fixed in
        # step3_combined.py.
        if i >= next_recalib_idx:
            current_pairs = find_top_pairs(draws_sets[max(0, i - current_window):i], N_TOP_PAIRS)
            next_recalib_idx = i + RECALIB_STEP
            if i >= eval_start:
                windows_used.append(current_window)

        if i >= eval_start:
            group_scores = compute_group_scores(states, current_pairs, HOT_THRESHOLD_FIXED, c3_bias)
            num_scores = compute_number_scores(group_scores)

            if tie_breaker == 'last_thickness':
                tie_score = {n: sum(states[g].last_thickness for g in NUM_TO_GROUPS[n]) for n in range(1, 50)}
                top_numbers = sorted(num_scores.items(), key=lambda x: (x[1], -tie_score[x[0]], x[0]), reverse=True)[:top_n]
            elif tie_breaker == 'random':
                top_numbers = sorted(num_scores.items(), key=lambda x: (x[1], random.random()), reverse=True)[:top_n]
            else:
                top_numbers = sorted(num_scores.items(), key=lambda x: (x[1], x[0]), reverse=True)[:top_n]

            predicted = set(num for num, _ in top_numbers)
            hits = len(predicted.intersection(set(draw_numbers)))
            hit_counts.append(hits)
            details.append((i, sorted(draw_numbers), sorted(predicted), hits))

        for gname, nums_set in GROUP_SET.items():
            drawn_in_group = [x for x in draw_numbers if x in nums_set]
            states[gname].update(len(drawn_in_group), drawn_in_group)

    return hit_counts, windows_used, details


def print_last_n_steps(details, n=20):
    print(f"\n--- Step-by-step result for the last {min(n, len(details))} draws ---")
    for idx, actual, predicted, hits in details[-n:]:
        matched = sorted(set(actual) & set(predicted))
        print(f"  #{idx}: draw={actual} | predicted={predicted} | matched={matched} ({hits})")


# ============================================================
#  STATISTICS AND OUTPUT
# ============================================================

def comb(n, k):
    if k < 0 or k > n:
        return 0
    return math.comb(n, k)


def hypergeom_pmf(N, K, n, k):
    return comb(K, k) * comb(N - K, n - k) / comb(N, n)


def theoretical_distribution(total_draws, pool_size=8, draw_size=6, N=49):
    return {k: hypergeom_pmf(N, pool_size, draw_size, k) * total_draws for k in range(draw_size + 1)}


def print_results(hit_counts, windows_used, total_draws_eval, top_n=8, c3_bias=0.0):
    print(f"Draws evaluated: {total_draws_eval}")
    print(f"Average hit count: {sum(hit_counts)/total_draws_eval:.4f}")

    from collections import Counter
    bins = Counter(hit_counts)
    print("\nHit distribution:")
    for k in range(max(bins.keys(), default=0) + 1):
        print(f"  {k} hits: {bins.get(k, 0)}")


def print_last_n_steps(details, n=20):
    hits_list = [d[3] for d in details[-100:]]
    print(f"\nLast {len(hits_list)} draws (hits in order): " + ", ".join(str(h) for h in hits_list))



# ============================================================
#  LIVE FORECAST (forward test — a prediction for the NEXT, not-yet-
#  known draw, instead of a backtest on the past)
# ============================================================

# Pairs watched by the slow monitor (baseline confirmed pairs + new
# ones from the reference doc worth keeping an eye on)
WATCH_PAIRS = [('C3', 'K10'), ('C2', 'C6'), ('K6', 'R7')]

def live_forecast(draws, top_n, tie_breaker, c3_bias):
    draws_sets = [set(d) for d in draws]
    N = len(draws)
    states = {name: GroupState(GROUP_SIZE[name]) for name in ALL_GROUPS}
    for draw_numbers in draws:
        for gname, nums_set in GROUP_SET.items():
            drawn_in_group = [x for x in draw_numbers if x in nums_set]
            states[gname].update(len(drawn_in_group), drawn_in_group)

    # fast recalibration (as in the backtest) — on the last RECALIB_WINDOW
    pairs = find_top_pairs(draws_sets[max(0, N - RECALIB_WINDOW):N], N_TOP_PAIRS)
    group_scores = compute_group_scores(states, pairs, HOT_THRESHOLD_FIXED, c3_bias)
    num_scores = compute_number_scores(group_scores)

    if tie_breaker == 'last_thickness':
        tie_score = {n: sum(states[g].last_thickness for g in NUM_TO_GROUPS[n]) for n in range(1, 50)}
        top_numbers = sorted(num_scores.items(), key=lambda x: (x[1], -tie_score[x[0]], x[0]), reverse=True)[:top_n]
    else:
        top_numbers = sorted(num_scores.items(), key=lambda x: (x[1], x[0]), reverse=True)[:top_n]

    predicted = sorted(n for n, _ in top_numbers)

    print(f"Fast rules (window={RECALIB_WINDOW}): {pairs[:len(pairs)//2] if pairs else '(none found)'}")
    print(f"PREDICTION POOL ({top_n} numbers): {predicted}")

    print(f"\nSlow balance monitor (window={SLOW_WINDOW}, current vs. previous):")
    monitor = slow_balance_monitor(draws_sets, N, WATCH_PAIRS, SLOW_WINDOW)
    for x, y, prior, recent, trend in monitor:
        if trend is None:
            print(f"  {x}->{y}: not enough data to compare")
            continue
        arrow = "strengthening" if trend > 2 else ("weakening" if trend < -2 else "stable")
        print(f"  {x}->{y}: previous window={prior:+.1f}pp, current={recent:+.1f}pp, "
              f"change={trend:+.1f}pp ({arrow})")

    return predicted


# ============================================================
#  CSV READING
# ============================================================

def read_csv(filename, filter_new_mode=False, start_date_str=None, end_date_str=None):
    draws = []
    start_date = None
    end_date = None
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        except Exception:
            print(f"Warning: could not parse date {start_date_str}, filter disabled.")
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except Exception:
            print(f"Warning: could not parse end date {end_date_str}.")

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if len(row) >= 7:
                    date_str = row[0].strip()
                    try:
                        nums = [int(x) for x in row[1:7]]
                    except ValueError:
                        continue
                    try:
                        d = datetime.strptime(date_str, "%Y-%m-%d")
                    except Exception:
                        continue
                    if filter_new_mode and start_date and d < start_date:
                        continue
                    if end_date and d > end_date:
                        continue
                    draws.append(nums)
    except FileNotFoundError:
        print(f"Error: file '{filename}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    if not draws:
        print("Warning: no draws were read. Check the file format.")
    return draws


# ============================================================
#  MAIN
# ============================================================

def main():
    draws_full = read_csv(CSV_FILE, USE_NEW_MODE_ONLY, NEW_MODE_START)
    if not draws_full:
        return

    if BACKTEST_ANCHOR_DATE:
        # trims only the END (for reproducibility across days) — the
        # start is always 2026-01-27; training/calibration data isn't trimmed
        draws_bt = read_csv(CSV_FILE, USE_NEW_MODE_ONLY, NEW_MODE_START, BACKTEST_ANCHOR_DATE)
        print(f"Backtest pinned to date <= {BACKTEST_ANCHOR_DATE} ({len(draws_bt)} draws, "
              f"training from {NEW_MODE_START})")
    else:
        draws_bt = draws_full

    # --- 1. BACKTEST ---
    print("=== BACKTEST ===")
    n_backtest = min(N_BACKTEST, len(draws_bt))
    hit_counts, windows_used, details = run_backtest(draws_bt, n_backtest, TOP_N, TIE_BREAKER, C3_BIAS_WEIGHT)
    print_results(hit_counts, windows_used, len(hit_counts), TOP_N, C3_BIAS_WEIGHT)
    print_last_n_steps(details, SHOW_LAST_N)

    # --- 2. LIVE FORECAST (always on the full, most recent data) ---
    print("\n=== LIVE FORECAST ===")
    live_forecast(draws_full, TOP_N, TIE_BREAKER, C3_BIAS_WEIGHT)


if __name__ == '__main__':
    main()
