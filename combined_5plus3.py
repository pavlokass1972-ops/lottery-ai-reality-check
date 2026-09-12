"""
combined_5plus3.py

Combined prediction algorithm: a 5-number "core" from the thread-based
scoring model (uk49s_algorithm.py) plus a 3-number "complement" from an
independent analog-search method (finds historical windows whose
"hot 8" numbers closely match the numbers in the most recent draw,
then pools the numbers that appeared shortly around those analog
points). The two components come from methodologically independent
sources of signal, which is the point: their errors don't correlate.

Usage:
    python combined_5plus3.py
"""

import csv
import importlib.util
import os
from collections import Counter
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE_DIR, "..", "data", "Uk49s_master_2021_2026.csv")
ALGO_PATH = os.path.join(BASE_DIR, "uk49s_algorithm.py")

# Load the thread-based algorithm as a module (without running its main())
spec = importlib.util.spec_from_file_location("nitky", ALGO_PATH)
nitky = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nitky)

NEW_MODE_START = "2026-01-27"
BACKTEST_DEPTH = 200

# Analog-search parameters
HOT_WINDOW = 20          # rolling window used to build each historical "hot 8"
MATCH_THRESHOLD = 5      # min overlap between control draw and a historical hot-8
ANALOG_BEFORE = 10       # draws included before each matched analog point
ANALOG_AFTER = 3         # draws included after each matched analog point

CORE_N = 5
COMPLEMENT_N = 3
SHOW_LAST_N = 20


# ============================================================
# Load data
# ============================================================
start_dt = datetime.strptime(NEW_MODE_START, "%Y-%m-%d")
rows = []
with open(SRC, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        try:
            d = datetime.strptime(r["date"].strip(), "%Y-%m-%d")
            if d < start_dt:
                continue
            nums = [int(float(r[f"n{i}"])) for i in range(1, 7)]
            rows.append((r["date"], nums))
        except Exception:
            continue

n = len(rows)
print(f"Regime from {NEW_MODE_START}: {n} draws ({rows[0][0]} .. {rows[-1][0]})")

# ============================================================
# Build the historical "hot 8" database (one entry per draw index)
# ============================================================
hot_db = []
for i in range(HOT_WINDOW, n):
    window = rows[i - HOT_WINDOW:i]
    pool = Counter()
    for _, nums in window:
        pool.update(nums)
    hot8 = [num for num, _ in pool.most_common(8)]
    hot_db.append({"idx": i, "hot8": hot8})

# ============================================================
# Walk-forward backtest: thread state updated incrementally,
# opposite-pair recalibration on a fixed absolute schedule
# ============================================================
draws_sets = [set(d) for _, d in rows]
states = {name: nitky.GroupState(nitky.GROUP_SIZE[name]) for name in nitky.ALL_GROUPS}

start_ctrl = n - BACKTEST_DEPTH
current_pairs = []
next_recalib_idx = -1
results = []

for i, (date_i, draw_numbers) in enumerate(rows):
    if i >= next_recalib_idx:
        current_pairs = nitky.find_top_pairs(
            draws_sets[max(0, i - nitky.RECALIB_WINDOW):i], nitky.N_TOP_PAIRS)
        next_recalib_idx = i + nitky.RECALIB_STEP

    if i >= start_ctrl:
        # --- core: thread-based score, using history up to i-1 ---
        group_scores = nitky.compute_group_scores(
            states, current_pairs, nitky.HOT_THRESHOLD_FIXED, nitky.C3_BIAS_WEIGHT)
        num_scores = nitky.compute_number_scores(group_scores)
        tie_score = {num: sum(states[g].last_thickness for g in nitky.NUM_TO_GROUPS[num])
                     for num in range(1, 50)}
        core_ranked = sorted(num_scores.items(),
                              key=lambda x: (x[1], -tie_score[x[0]], x[0]), reverse=True)
        core5 = set(num for num, _ in core_ranked[:CORE_N])

        # --- complement: analog search (control = i-1, target = i) ---
        control_idx = i - 1
        complement = []
        if control_idx >= 0:
            ctrl_set = set(rows[control_idx][1])
            candidates = [rec for rec in hot_db
                          if rec["idx"] - ANALOG_BEFORE >= 0
                          and rec["idx"] + ANALOG_AFTER < control_idx]
            matches = [rec for rec in candidates
                       if len(ctrl_set & set(rec["hot8"])) >= MATCH_THRESHOLD]

            pool = Counter()
            for rec in matches:
                a_idx = rec["idx"]
                a_window = rows[a_idx - ANALOG_BEFORE: a_idx + ANALOG_AFTER + 1]
                for _, nums in a_window:
                    pool.update(nums)

            if not pool:
                # fallback when no analog is found: recent window, unfiltered
                for _, nums in rows[max(0, control_idx - HOT_WINDOW):control_idx + 1]:
                    pool.update(nums)

            ranked = [num for num, _ in pool.most_common(49) if num not in core5]
            complement = ranked[:COMPLEMENT_N]

        final8 = core5 | set(complement)
        actual = set(draw_numbers)

        results.append({
            "date": date_i, "idx": i,
            "core5": sorted(core5), "complement": sorted(complement),
            "final8": sorted(final8),
            "hits_core": len(core5 & actual),
            "hits_complement": len(set(complement) & actual),
            "hits_final": len(final8 & actual),
        })

    for gname, nums_set in nitky.GROUP_SET.items():
        drawn_in_group = [x for x in draw_numbers if x in nums_set]
        states[gname].update(len(drawn_in_group), drawn_in_group)

# ============================================================
# Stats
# ============================================================
def hist(key):
    return Counter(r[key] for r in results)


for label, key in [("CORE (5, threads only)", "hits_core"),
                    ("FINAL (8 = core + complement)", "hits_final")]:
    h = hist(key)
    total = len(results)
    print(f"\n=== {label} === (n={total})")
    for k in range(9):
        print(f"  {k} hits: {h.get(k, 0)}")
    print(f"  mean: {sum(r[key] for r in results) / total:.4f}")
    h3 = sum(v for k, v in h.items() if k >= 3)
    print(f"  3+ hits: {h3}/{total} = {h3 / total * 100:.2f}%")


def print_last_n_steps(results, key, label, n=SHOW_LAST_N):
    hits_list = [r[key] for r in results[-n:]]
    print(f"\nLast {len(hits_list)} draws, {label} (hits in order): "
          + ", ".join(str(h) for h in hits_list))


print_last_n_steps(results, "hits_core", "CORE (5)")
print_last_n_steps(results, "hits_final", "FINAL (8)")

with open(os.path.join(BASE_DIR, "combined_5plus3_results.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
    w.writeheader()
    for r in results:
        w.writerow(r)
print(f"\nSaved: combined_5plus3_results.csv")

# ============================================================
# Live forecast for the next, not-yet-drawn draw
# ============================================================
current_pairs = nitky.find_top_pairs(
    draws_sets[max(0, n - nitky.RECALIB_WINDOW):n], nitky.N_TOP_PAIRS)

group_scores = nitky.compute_group_scores(
    states, current_pairs, nitky.HOT_THRESHOLD_FIXED, nitky.C3_BIAS_WEIGHT)
num_scores = nitky.compute_number_scores(group_scores)
tie_score = {num: sum(states[g].last_thickness for g in nitky.NUM_TO_GROUPS[num])
             for num in range(1, 50)}
core_ranked = sorted(num_scores.items(),
                      key=lambda x: (x[1], -tie_score[x[0]], x[0]), reverse=True)
core5_live = set(num for num, _ in core_ranked[:CORE_N])

control_idx_live = n - 1
ctrl_set_live = set(rows[control_idx_live][1])
candidates_live = [rec for rec in hot_db
                    if rec["idx"] - ANALOG_BEFORE >= 0
                    and rec["idx"] + ANALOG_AFTER < control_idx_live]
matches_live = [rec for rec in candidates_live
                if len(ctrl_set_live & set(rec["hot8"])) >= MATCH_THRESHOLD]

pool_live = Counter()
analog_used = bool(matches_live)
for rec in matches_live:
    a_idx = rec["idx"]
    for _, nums in rows[a_idx - ANALOG_BEFORE: a_idx + ANALOG_AFTER + 1]:
        pool_live.update(nums)
if not pool_live:
    for _, nums in rows[max(0, control_idx_live - HOT_WINDOW):control_idx_live + 1]:
        pool_live.update(nums)

ranked_live = [num for num, _ in pool_live.most_common(49) if num not in core5_live]
complement_live = ranked_live[:COMPLEMENT_N]
final8_live = core5_live | set(complement_live)

print("\n" + "=" * 50)
print("LIVE FORECAST (for the next, not-yet-drawn draw)")
print("=" * 50)
print(f"Last known draw: {rows[-1][0]} -> {sorted(rows[-1][1])}")
print(f"Analog found: {'yes, ' + str(len(matches_live)) + ' match(es)' if analog_used else 'no (fallback: recent window)'}")
print(f"Core (threads, 5):     {sorted(core5_live)}")
print(f"Complement (3):        {sorted(complement_live)}")
print(f"FINAL POOL (8):        {sorted(final8_live)}")
