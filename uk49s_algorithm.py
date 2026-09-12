#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Бектест алгоритму UK49s на основі ниток — версія 2.
База: 123.py (структура груп, GroupState, tie-breaking, гіпергеометрика).

Зміни відносно 123.py:
  1. Прибрано СТАТИЧНІ жорстко зашиті правила (C3-K10, C2-C6, K6-R7
     назавжди). Замість цього — ЖИВА, КОВЗНА ПЕРЕКАЛІБРОВКА: кожні
     RECALIB_STEP тиражів заново шукаються найсильніші опозитні пари
     на вікні останніх ROLLING WINDOW тиражів. Розмір цього вікна
     сам обирається адаптивно з CANDIDATE_WINDOWS за принципом
     моторів A/Б (яке вікно давало кращий результат на нещодавньому
     минулому — те й використовується).
  2. C3_BIAS_WEIGHT за замовчуванням змінено з 2.5 на 1.0 — 2.5
     давало кращий P(k>=3), але гірший P(k>=4) і не було оптимальним
     на чесній другій половині даних (train/test перевірка).
  3. Прибрано CALIBRATION_WINDOW / CALIBRATION_PERCENTILE (динамічний
     поріг товщини) — окрема, не пов'язана й не перевірена гілка,
     плутала з основною ідеєю. Поріг "гарячого пострілу" завжди
     фіксований = 3.

Працює без зовнішніх бібліотек (тільки стандартний Python).
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
#  НАЛАШТУВАННЯ (ЗМІНЮЙТЕ ТУТ)
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "Uk49s_master_2021_2026.csv")

N_BACKTEST = 900          # кількість останніх тиражів для бектесту
                          # (використовується лише якщо BACKTEST_ANCHOR_DATE=None)
TOP_N = 8                # скільки чисел видавати в прогнозі

# --- Фіксована точка відліку бектесту (для відтворюваності) ---
# Проблема: "останні 800 тиражів" щодня зсувається вперед, бо щодня
# додаються нові тиражі — тому той самий N_BACKTEST=800 дає трохи
# інший результат кожного дня (перевірено: розкид не драматичний,
# 1.09-1.13 середньо на глибинах 700-880, але все ж не ідентичний).
# Щоб порівнювати результати різних днів чесно "яблуко до яблука",
# можна зафіксувати кінець бектесту на конкретній даті замість
# "останні N тиражів від сьогодні". Якщо BACKTEST_ANCHOR_DATE=None —
# використовується старий спосіб (N_BACKTEST від кінця файлу).
BACKTEST_ANCHOR_DATE = None   # напр. "2026-09-04", або None

# --- Фільтр нового режиму (з 27.01.2026) ---
USE_NEW_MODE_ONLY = True
NEW_MODE_START = "2026-01-27"

# --- Tie-breaking ---
TIE_BREAKER = 'last_thickness'   # 'last_thickness', 'random', 'number'

# --- Зсув ваги в бік C3 ---
# 0.0 = без зсуву. 1.0-1.5 = помірний, підтверджений на train/test
# зсув (кращий баланс P(k>=3) і P(k>=4), ніж 2.5).
C3_BIAS_WEIGHT = 1.5

# --- Живий прогноз / forward-test ---
SLOW_WINDOW = 100         # повільне вікно для монітора зсуву балансу
                          # (окремо від швидкого RECALIB_WINDOW=10)
SHOW_LAST_N = 10          # показати покроковий результат по останніх
                          # N тиражах (0/1/2/3... влучань на кожен)

# Перевірено емпірично (кілька прогонів з різними вікнами): 10 —
# найстабільніше й найкраще вікно перекалібровки. Адаптивний вибір
# між кількома розмірами (10/20/30/50) не додав нічого понад просте
# фіксоване вікно=10 — тому спрощено до одного фіксованого значення.
RECALIB_WINDOW = 10     # розмір вікна для пошуку пар щоразу заново
LOOKBACK = 100           # (лишається для сумісності, не використовується
                         # напряму при фіксованому вікні)
RECALIB_STEP = 100      # як часто (раз на скільки тиражів) шукати нові правила
N_TOP_PAIRS = 4# максимум пар, що можуть пройти поріг одночасно
                          # (підтверджено емпірично як краще за 2 і 4)
CORR_THRESHOLD = 0.95    # "округлення" — пара враховується лише якщо
                          # |кореляція| > цей поріг; слабші сигнали
                          # відкидаються повністю (може лишити 0 пар
                          # на якийсь відрізок — це нормально і
                          # навмисно: перевірено на бектесті, що
                          # "нічого не ставити" краще за "поставити
                          # на слабкий, невпевнений сигнал").
HOT_THRESHOLD_FIXED = 3  # поріг "гарячого пострілу" (товщина в 1 тиражі)

# ============================================================
#  ГРУПИ (K, R, C) — НЕ ЗМІНЮВАТИ
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
# пари груп, що НЕ перетинаються фізично (щоб не переплутати з артефактом підмножини)
DISJOINT_PAIRS = [(g1, g2) for g1, g2 in combinations(GROUP_NAMES, 2)
                   if not (GROUP_SET[g1] & GROUP_SET[g2])]

# ============================================================
#  КЛАС СТАНУ ГРУПИ
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
#  ЖИВА ПЕРЕКАЛІБРОВКА ПРАВИЛ
# ============================================================

def hit_series(gname, draws_slice):
    """0/1 ряд: чи є хоч 1 число групи в кожному тиражі зрізу."""
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
    """Знайти найсильніші НЕГАТИВНО корельовані (опозитні) пари груп
    на заданому зрізі тиражів, "округлюючи" (відкидаючи) усе слабше
    за `threshold`. Повертає список (X, Y) обома напрямками: якщо
    X=0 -> бонус Y. Може повернути порожній список — це навмисно:
    коли жоден сигнал не досяг порогу впевненості, краще нічого не
    ставити, ніж покладатись на слабку, невпевнену пару."""
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
        if corr < -threshold:   # "округлення": лишаємо тільки впевнено негативні
            pair_corrs.append((g1, g2, corr))

    pair_corrs.sort(key=lambda x: x[2])  # найнегативніші перші
    pairs = []
    for g1, g2, c in pair_corrs[:n_top]:
        pairs.append((g1, g2))
        pairs.append((g2, g1))
    return pairs


def evaluate_window_choice(draws_sets, end_idx, window, lookback, pool=TOP_N):
    """Ретроспективно перевірити: якби перекалібровувались щоразу
    вікном `window` протягом останніх `lookback` тиражів (закінчуючи
    на end_idx), який середній хіт-рейт це дало б? Використовується
    для адаптивного вибору розміру вікна (як мотори A/Б)."""
    start = max(window, end_idx - lookback)
    if end_idx - start < window:
        return 0.0, 0
    states = {g: GroupState(GROUP_SIZE[g]) for g in GROUP_NAMES}
    # прогріваємо стан від початку історії до start (без запису хітів)
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
#  ПОВІЛЬНИЙ МОНІТОР ЗСУВУ БАЛАНСУ (окремо від швидкого вікна=10)
# ============================================================
#  Швидке вікно (RECALIB_WINDOW=10) ловить миттєвий стан, але не
#  показує сам факт, що сила конкретної пари системно зростає чи
#  спадає протягом місяців (див. довідку: C3-K10 послабшала в
#  квітні 2026, C2-C6 різко посилилась у липні-серпні 2026). Ця
#  функція рахує ту саму умовну різницю (X=0 -> бонус Y), але на
#  повільному вікні (SLOW_WINDOW=100) і порівнює з попереднім таким
#  самим вікном, щоб показати НАПРЯМОК зміни сили правила в часі.

def conditional_diff(x_gname, y_gname, draws_sets):
    x_hit = hit_series(x_gname, draws_sets)
    y_hit = hit_series(y_gname, draws_sets)
    z_vals = [y for x, y in zip(x_hit, y_hit) if x == 0]
    a_vals = [y for x, y in zip(x_hit, y_hit) if x == 1]
    if not z_vals or not a_vals:
        return None
    return (sum(z_vals) / len(z_vals) - sum(a_vals) / len(a_vals)) * 100


def slow_balance_monitor(draws_sets, end_idx, pairs_to_watch, slow_window=SLOW_WINDOW):
    """Для кожної пари (X,Y) з pairs_to_watch: порахувати силу
    правила X->Y на двох послідовних повільних вікнах (щойно
    минулому і тому, що перед ним), і показати напрямок зміни."""
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
#  СКОРИНГ
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
#  БЕКТЕСТ З ЖИВОЮ ПЕРЕКАЛІБРОВКОЮ
# ============================================================

def run_backtest(draws, n_backtest, top_n, tie_breaker, c3_bias):
    total = len(draws)
    eval_start = total - n_backtest
    if eval_start < 0:
        raise ValueError("n_backtest більше за кількість тиражів")

    draws_sets = [set(d) for d in draws]
    states = {name: GroupState(GROUP_SIZE[name]) for name in ALL_GROUPS}
    hit_counts = []
    windows_used = []
    details = []  # (індекс, фактичний тираж, прогнозований пул, к-сть влучань)

    current_window = RECALIB_WINDOW
    current_pairs = []
    next_recalib_idx = -1

    for i, draw_numbers in enumerate(draws):
        # --- перекалібровка пар — ЗАВЖДИ на абсолютному розкладі (0, RECALIB_STEP, 2*RECALIB_STEP, ...)
        # ВАЖЛИВО: винесено з-під "if i >= eval_start", щоб розклад перекалібровок
        # не залежав від n_backtest. Інакше для тих самих останніх тиражів
        # current_pairs (а отже й прогноз) відрізнявся б залежно від того,
        # яку глибину бектесту (n_backtest) вибрали — та сама помилка, що
        # була знайдена й виправлена в step3_combined.py.
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
    print(f"\n--- Покроковий результат по останніх {min(n, len(details))} тиражах ---")
    for idx, actual, predicted, hits in details[-n:]:
        matched = sorted(set(actual) & set(predicted))
        print(f"  #{idx}: тираж={actual} | прогноз={predicted} | влучило={matched} ({hits})")


# ============================================================
#  СТАТИСТИКА ТА ВИВІД
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
    print(f"Оцінено тиражів: {total_draws_eval}")
    print(f"Середня кількість влучань: {sum(hit_counts)/total_draws_eval:.4f}")

    from collections import Counter
    bins = Counter(hit_counts)
    print("\nРозподіл влучань:")
    for k in range(max(bins.keys(), default=0) + 1):
        print(f"  {k} влучань: {bins.get(k, 0)}")


def print_last_n_steps(details, n=20):
    hits_list = [d[3] for d in details[-100:]]
    print(f"\nОстанні {len(hits_list)} тиражів (влучання по порядку): " + ", ".join(str(h) for h in hits_list))



# ============================================================
#  ЖИВИЙ ПРОГНОЗ (forward-test — прогноз на НАСТУПНИЙ, ще не
#  відомий тираж, замість бектесту на минулому)
# ============================================================

# Пари, за якими стежить повільний монітор (базові підтверджені +
# нові з довідки, що варто тримати в полі зору)
WATCH_PAIRS = [('C3', 'K10'), ('C2', 'C6'), ('K6', 'R7')]

def live_forecast(draws, top_n, tie_breaker, c3_bias):
    draws_sets = [set(d) for d in draws]
    N = len(draws)
    states = {name: GroupState(GROUP_SIZE[name]) for name in ALL_GROUPS}
    for draw_numbers in draws:
        for gname, nums_set in GROUP_SET.items():
            drawn_in_group = [x for x in draw_numbers if x in nums_set]
            states[gname].update(len(drawn_in_group), drawn_in_group)

    # швидка перекалібровка (як у бектесті) — на останньому RECALIB_WINDOW
    pairs = find_top_pairs(draws_sets[max(0, N - RECALIB_WINDOW):N], N_TOP_PAIRS)
    group_scores = compute_group_scores(states, pairs, HOT_THRESHOLD_FIXED, c3_bias)
    num_scores = compute_number_scores(group_scores)

    if tie_breaker == 'last_thickness':
        tie_score = {n: sum(states[g].last_thickness for g in NUM_TO_GROUPS[n]) for n in range(1, 50)}
        top_numbers = sorted(num_scores.items(), key=lambda x: (x[1], -tie_score[x[0]], x[0]), reverse=True)[:top_n]
    else:
        top_numbers = sorted(num_scores.items(), key=lambda x: (x[1], x[0]), reverse=True)[:top_n]

    predicted = sorted(n for n, _ in top_numbers)

    print(f"Швидкі правила (вікно={RECALIB_WINDOW}): {pairs[:len(pairs)//2] if pairs else '(не знайдено)'}")
    print(f"ПРОГНОЗНИЙ ПУЛ ({top_n} чисел): {predicted}")

    print(f"\nПовільний монітор балансу (вікно={SLOW_WINDOW}, поточне vs попереднє):")
    monitor = slow_balance_monitor(draws_sets, N, WATCH_PAIRS, SLOW_WINDOW)
    for x, y, prior, recent, trend in monitor:
        if trend is None:
            print(f"  {x}->{y}: недостатньо даних для порівняння")
            continue
        arrow = "посилюється" if trend > 2 else ("слабшає" if trend < -2 else "стабільно")
        print(f"  {x}->{y}: попереднє вікно={prior:+.1f}п.п., поточне={recent:+.1f}п.п., "
              f"зміна={trend:+.1f}п.п. ({arrow})")

    return predicted


# ============================================================
#  ЧИТАННЯ CSV
# ============================================================

def read_csv(filename, filter_new_mode=False, start_date_str=None, end_date_str=None):
    draws = []
    start_date = None
    end_date = None
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        except Exception:
            print(f"Попередження: не вдалося розпарсити дату {start_date_str}, фільтр вимкнено.")
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        except Exception:
            print(f"Попередження: не вдалося розпарсити кінцеву дату {end_date_str}.")

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
        print(f"Помилка: файл '{filename}' не знайдено.")
        sys.exit(1)
    except Exception as e:
        print(f"Помилка читання файлу: {e}")
        sys.exit(1)

    if not draws:
        print("Увага: не прочитано жодного тиражу. Перевірте формат файлу.")
    return draws


# ============================================================
#  ГОЛОВНА
# ============================================================

def main():
    draws_full = read_csv(CSV_FILE, USE_NEW_MODE_ONLY, NEW_MODE_START)
    if not draws_full:
        return

    if BACKTEST_ANCHOR_DATE:
        # обрізає лише КІНЕЦЬ (для відтворюваності між днями) — початок
        # завжди 27.01.2026, тренування/калібрування не обрізається
        draws_bt = read_csv(CSV_FILE, USE_NEW_MODE_ONLY, NEW_MODE_START, BACKTEST_ANCHOR_DATE)
        print(f"Бектест зафіксовано на даті <= {BACKTEST_ANCHOR_DATE} ({len(draws_bt)} тиражів, "
              f"тренування з {NEW_MODE_START})")
    else:
        draws_bt = draws_full

    # --- 1. БЕКТЕСТ ---
    print("=== БЕКТЕСТ ===")
    n_backtest = min(N_BACKTEST, len(draws_bt))
    hit_counts, windows_used, details = run_backtest(draws_bt, n_backtest, TOP_N, TIE_BREAKER, C3_BIAS_WEIGHT)
    print_results(hit_counts, windows_used, len(hit_counts), TOP_N, C3_BIAS_WEIGHT)
    print_last_n_steps(details, SHOW_LAST_N)

    # --- 2. ЖИВИЙ ПРОГНОЗ (завжди на повних, найсвіжіших даних) ---
    print("\n=== ЖИВИЙ ПРОГНОЗ ===")
    live_forecast(draws_full, TOP_N, TIE_BREAKER, C3_BIAS_WEIGHT)


if __name__ == '__main__':
    main()
