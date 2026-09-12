"""
heuristic_baselines.py

Two common "under the hood" approaches that many GitHub lottery
predictors reduce to in practice: a rolling-window frequency
("hot numbers") heuristic, and a first-order Markov chain on
transition frequencies. Evaluated with the same walk-forward
P(>=3)/P(>=4) protocol as everything else in this project.

Usage:
    python heuristic_baselines.py
"""

import csv
import os
from collections import Counter, defaultdict

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "Uk49s_master_2021_2026.csv")
TOP_N = 8
NEW_MODE_START = "2026-01-27"


def load_draws(path, start_date=None):
    draws, dates = [], []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if not row:
                continue
            date_str = row[0]
            if start_date and date_str < start_date:
                continue
            draws.append(tuple(int(x) for x in row[1:7]))
            dates.append(date_str)
    return draws, dates


def predict_hot(draws, t, window=200):
    hist = draws[max(0, t - window):t]
    c = Counter()
    for d in hist:
        for num in d:
            c[num] += 1
    return [num for num, _ in c.most_common(TOP_N)]


def predict_markov(draws, t, window=400):
    trans = defaultdict(lambda: defaultdict(int))
    hist = draws[max(0, t - window):t]
    for i in range(1, len(hist)):
        for prev_num in hist[i - 1]:
            for cur_num in hist[i]:
                trans[prev_num][cur_num] += 1
    last_draw = draws[t - 1]
    scores = defaultdict(float)
    for prev_num in last_draw:
        for cur_num, cnt in trans[prev_num].items():
            scores[cur_num] += cnt
    if not scores:
        return list(range(1, TOP_N + 1))
    return sorted(scores, key=scores.get, reverse=True)[:TOP_N]


def evaluate(name, draws, predict_fn, test_start):
    hit_counts = []
    for t in range(test_start, len(draws)):
        pred = predict_fn(draws, t)
        actual = set(draws[t])
        hit_counts.append(len(set(pred) & actual))
    n = len(hit_counts)
    p3 = sum(1 for h in hit_counts if h >= 3) / n
    p4 = sum(1 for h in hit_counts if h >= 4) / n
    avg = sum(hit_counts) / n
    print(f"{name}: n={n}, avg={avg:.4f}, P(>=3)={p3:.4f}, P(>=4)={p4:.4f}")
    return hit_counts


def main():
    draws, dates = load_draws(CSV_PATH, start_date=NEW_MODE_START)
    n = len(draws)
    split_idx = 10 + int(0.75 * (n - 10))  # match the LSTM script's test window

    evaluate("Hot numbers (200-draw window)", draws, predict_hot, split_idx)
    evaluate("First-order Markov chain (400-draw window)", draws, predict_markov, split_idx)
    print("\nTheoretical random baseline: avg=0.9796, P(>=3)=0.0217, P(>=4)=0.0014")


if __name__ == "__main__":
    main()
