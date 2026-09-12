"""
lstm_baseline.py

A faithful reimplementation of the Embedding->LSTM->Dense(sigmoid)
architecture used by the most common "AI lottery predictor" repos on
GitHub (verified against the published source of one such project's
sibling repo). Trains on this dataset, evaluates with a 75/25
train/test split, and reports the same P(>=3) / P(>=4) metrics used
throughout this project.

Usage:
    pip install numpy tensorflow
    python lstm_baseline.py

Requires: numpy, tensorflow (tested with tensorflow-cpu 2.x)
"""

import numpy as np
from tensorflow import keras
from keras import layers
import csv
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "Uk49s_master_2021_2026.csv")
SEQ_LEN = 10
TOP_N = 8
NEW_MODE_START = "2026-01-27"  # set to None to use the full file


def load_draws(path, start_date=None):
    draws, dates = [], []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if not row:
                continue
            date_str = row[0]
            if start_date and date_str < start_date:
                continue
            nums = tuple(int(x) for x in row[1:7])
            draws.append(nums)
            dates.append(date_str)
    return draws, dates


def to_multihot(draw):
    v = np.zeros(50, dtype=np.float32)
    for num in draw:
        v[num] = 1.0
    return v[1:]  # numbers 1..49


def main():
    draws, dates = load_draws(CSV_PATH, start_date=NEW_MODE_START)
    n = len(draws)
    print(f"Loaded {n} draws")

    X_all = np.array([to_multihot(d) for d in draws])
    sequences = np.array([X_all[i:i + SEQ_LEN] for i in range(len(X_all) - SEQ_LEN)])
    targets = X_all[SEQ_LEN:]

    split = int(0.75 * len(sequences))
    X_train, y_train = sequences[:split], targets[:split]
    X_test, y_test = sequences[split:], targets[split:]
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    model = keras.Sequential([
        layers.Input(shape=(SEQ_LEN, 49)),
        layers.LSTM(64, dropout=0.2),
        layers.Dense(64, activation="relu"),
        layers.Dense(49, activation="sigmoid"),
    ])
    model.compile(optimizer="adam", loss="binary_crossentropy")
    model.fit(X_train, y_train, epochs=40, batch_size=32, validation_split=0.1, verbose=0)

    preds = model.predict(X_test, verbose=0)
    hit_counts = []
    for i in range(len(preds)):
        top_idx = np.argsort(preds[i])[-TOP_N:]
        predicted = set(top_idx + 1)
        actual = set(np.where(y_test[i] == 1)[0] + 1)
        hit_counts.append(len(predicted & actual))
    hit_counts = np.array(hit_counts)

    print(f"\nLSTM results on {len(hit_counts)} held-out draws:")
    print(f"  avg hits    = {hit_counts.mean():.4f}")
    print(f"  P(>=3 hits) = {(hit_counts >= 3).mean():.4f}")
    print(f"  P(>=4 hits) = {(hit_counts >= 4).mean():.4f}")
    print(f"  theoretical random baseline: avg=0.9796, P(>=3)=0.0217, P(>=4)=0.0014")


if __name__ == "__main__":
    main()
