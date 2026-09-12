"""
research_utils.py — бібліотека повторюваних функцій дослідження UK49s.
Мета: перевірка нової гіпотези за 2-3 рядки, без переписування коду.

Приклад використання:
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
#  ЗАВАНТАЖЕННЯ ДАНИХ
# ============================================================

def load_draws(csv_path, start_date="2026-01-27", end_date=None):
    """Повертає (draws, dates) — списки тиражів (list[int]) і дат
    (str), відфільтровані за датою нового режиму."""
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
#  ГРУПИ (K, R, C) — стандартна сітка 7×7
# ============================================================

def build_groups():
    """Повертає dict {назва: set(числа)} для K1-K10, R1-R7, C1-C7."""
    K = {f"K{i}": set(range((i - 1) * 5 + 1, i * 5 + 1)) for i in range(1, 10)}
    K["K10"] = set(range(46, 50))
    R = {f"R{r}": set(n for n in range(1, 50) if (n - 1) // 7 + 1 == r) for r in range(1, 8)}
    C = {f"C{c}": set(n for n in range(1, 50) if (n - 1) % 7 + 1 == c) for c in range(1, 8)}
    return {**K, **R, **C}


# ============================================================
#  БАЗОВІ ІНДИКАТОРИ
# ============================================================

def hit_series(draws, members):
    """0/1 ряд: чи є хоч 1 число групи в кожному тиражі."""
    return [1 if (set(d) & members) else 0 for d in draws]


def thickness_series(draws, members):
    """Товщина (0-7) групи в кожному тиражі."""
    return [len(set(d) & members) for d in draws]


def state_streak(draws, t, members):
    """Поточний безперервний ланцюжок (сума товщини) до і включно
    з тиражем t, назад у часі."""
    total = 0
    tt = t
    while tt >= 0 and (set(draws[tt]) & members):
        total += len(set(draws[tt]) & members)
        tt -= 1
    return total


def just_ended_saturated(draws, t, members):
    """Чи тираж t сам щойно завершив насичену серію (streak
    перервався на t, і сума попереднього ланцюжка >= розміру групи)."""
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
    """Список серій (list of list[int] індексів тиражів) для групи."""
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
    """Частка серій, що досягають повного насичення (сума >= розмір)."""
    size = len(members)
    thick = thickness_series(draws, members)
    series = series_list(draws, members)
    if not series:
        return 0.0
    sat = sum(1 for s in series if sum(thick[t] for t in s) >= size)
    return sat / len(series)


# ============================================================
#  ПЕРЕВІРКА ГІПОТЕЗ: ЧЕТВЕРТИНИ, TRAIN/TEST, ЗНАЧУЩІСТЬ
# ============================================================

def conditional_diff(draws, x_members, y_members):
    """(hit-rate Y коли X=0) - (hit-rate Y коли X>=1), у п.п.
    Це і є стандартна перевірка "X->Y" з довідки."""
    x_hit = hit_series(draws, x_members)
    y_hit = hit_series(draws, y_members)
    z = [y for x, y in zip(x_hit, y_hit) if x == 0]
    a = [y for x, y in zip(x_hit, y_hit) if x == 1]
    if not z or not a:
        return None
    return (sum(z) / len(z) - sum(a) / len(a)) * 100


def quarter_check(draws, x_members, y_members, n_quarters=4):
    """conditional_diff окремо в кожній із n_quarters рівних
    частин часового ряду. Повертає list значень (None якщо
    недостатньо даних у частині)."""
    n = len(draws)
    q = n // n_quarters
    out = []
    for i in range(n_quarters):
        s = i * q
        e = (i + 1) * q if i < n_quarters - 1 else n
        out.append(conditional_diff(draws[s:e], x_members, y_members))
    return out


def train_test_check(draws, x_members, y_members):
    """conditional_diff на першій і другій половині даних.
    Повертає (train_diff, test_diff) — якщо знаки різні, це
    ознака шуму, не реального зв'язку."""
    n = len(draws)
    split = n // 2
    return (conditional_diff(draws[:split], x_members, y_members),
            conditional_diff(draws[split:], x_members, y_members))


def binom_pvalue(successes, trials, expected_p):
    """p-value одностороннього біноміального тесту (успіхів
    більше, ніж очікувано). Без scipy — власна реалізація."""
    from math import comb
    p_val = sum(comb(trials, k) * expected_p ** k * (1 - expected_p) ** (trials - k)
                for k in range(successes, trials + 1))
    return p_val


def theoretical_hitrate(group_size, draw_size=6, total=49):
    """P(хоч 1 число групи є в тиражі) — точна гіпергеометрика."""
    from math import comb
    p_zero = comb(total - group_size, draw_size) / comb(total, draw_size)
    return 1 - p_zero


# ============================================================
#  ОЦІНКА ПРОГНОЗУЮЧИХ НАБОРІВ ЧИСЕЛ ЧЕРЕЗ P(>=3)/P(>=4)/P(>=5)
#  (уточнено 2026-09-11, за наслідками циклів #56-#58): для будь-
#  якої гіпотези, що оцінює алгоритм/"мотор"/ядро+доповнення проти
#  фактичного тиражу, СЕРЕДНЯ кількість влучань — НЕПРАВИЛЬНА основна
#  метрика (змішує 0/1/2, які не мають цінності, з 3+/4+/5+, які і є
#  метою). Використовуй ЦІ функції як основний stat_fn.
# ============================================================

def theoretical_p_ge(K, k_min, draw_size=6, total=49):
    """Точна гіпергеометрична P(влучень >= k_min) для прогнозу
    розміру K проти тиражу draw_size з total.
    Приклад: theoretical_p_ge(8, 4) -> точна P(>=4) для 8-числового
    прогнозу — теоретичний еталон для порівняння."""
    from math import comb
    return sum(comb(K, j) * comb(total - K, draw_size - j) / comb(total, draw_size)
               for j in range(k_min, draw_size + 1) if j <= K)


def empirical_p_ge(predicted_sets, actual_sets, k_min):
    """Емпірична частка тиражів, де |predicted ∩ actual| >= k_min.
    predicted_sets, actual_sets — списки set() однакової довжини
    (по одному прогнозу й факту на кожен протестований тираж)."""
    n = len(predicted_sets)
    if n == 0:
        return None
    hits = [len(p & a) for p, a in zip(predicted_sets, actual_sets)]
    return sum(1 for h in hits if h >= k_min) / n


def predictor_null_check(predicted_sets, K, k_min, n_trials=300, seed=None,
                          total=49, draw_size=6):
    """Нуль-модель САМЕ для P(>=k_min): прогнозовані набори (вже
    згенеровані алгоритмом) залишаються ФІКСОВАНИМИ, симулюється
    випадковий тираж замість реального. Повертає dict у тому ж
    форматі, що й null_model_check() (real_value, p_value_two_sided,
    percentile, verdict), але статистика — саме частка P(>=k_min),
    не середнє."""
    import random
    n = len(predicted_sets)
    rng = random.Random(seed)
    real_hits = None  # рахується нижче, якщо actual_sets передані ззовні -
                        # ця функція очікує, що real_value рахує викликач
                        # через empirical_p_ge(predicted, actual, k_min)
    null_values = []
    for _ in range(n_trials):
        sim_actuals = [set(rng.sample(range(1, total + 1), draw_size)) for _ in range(n)]
        v = empirical_p_ge(predicted_sets, sim_actuals, k_min)
        null_values.append(v)
    null_values.sort()
    return null_values  # відсортований список для подальшого порівняння з real


# ============================================================
#  ПОШУК ОПОЗИТНИХ ПАР (як у живому алгоритмі, з порогом)
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
    """Знайти пари груп з кореляцією сильнішою за -threshold.
    groups: dict {назва: set}. Повертає list (X, Y) обома
    напрямками: якщо X=0 -> бонус Y."""
    names = list(groups.keys())
    n = len(draws)
    cw = corr_window or max(5, n // 3)
    rolls = {g: rolling_mean(hit_series(draws, groups[g]), cw) for g in names}

    pair_corrs = []
    for g1, g2 in combinations(names, 2):
        if groups[g1] & groups[g2]:
            continue  # структурний перетин — пропустити
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
#  ОБОВ'ЯЗКОВА НУЛЬ-МОДЕЛЬ — без цього кроку НІЧОГО не вважається
#  підтвердженим. Сесія 2026-09-10 показала: рекурентна кореляція,
#  Moran's I, крос-кореляція на лагах — усе це дає "переконливі"
#  значення навіть на чистому шумі, якщо не порівняти з нуль-моделлю.
# ============================================================

def null_model_check(real_draws, stat_fn, n_trials=200, seed=None,
                      total=49, draw_size=6):
    """Універсальна перевірка будь-якої статистики проти чисто
    випадкових тиражів того самого розміру.

    real_draws: список тиражів (list[int]) — реальні дані
    stat_fn(draws) -> float: будь-яка статистика, яку рахуємо
        (кореляція, hit-rate, дисперсія, що завгодно — головне,
        щоб функція приймала список тиражів і повертала одне число)
    n_trials: скільки випадкових симуляцій (200-500 достатньо)

    Повертає dict:
        real_value        — реальне значення статистики
        null_values        — відсортований список n_trials симульованих значень
        p_value_two_sided   — частка симуляцій, де |null| >= |real| (чим менше, тим краще)
        percentile          — на якому перцентилі нуль-розподілу лежить real_value
        verdict             — 'CONFIRMED' якщо p<0.05, інакше 'NOISE-LIKE'

    ОБОВ'ЯЗКОВО викликати цю функцію для КОЖНОЇ нової гіпотези, що
    базується на кореляції, дисперсії, чи будь-якій "красивій цифрі",
    перш ніж записувати висновок у лог як підтверджений.
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
    """Скільки гіпотез вже перевірено ЗА ВСЮ ІСТОРІЮ автоматизації —
    поріг значущості треба звужувати пропорційно, інакше рано чи
    пізно щось "підтвердиться" просто випадково (multiple comparisons).
    Використовувати як довідковий поріг при оцінці p_value з
    null_model_check: якщо p_value > adjusted_alpha — не підтверджено,
    навіть якщо p_value < 0.05 у сирому вигляді."""
    adjusted_alpha = alpha / max(1, n_hypotheses_this_session)
    return {
        "n_hypotheses": n_hypotheses_this_session,
        "raw_alpha": alpha,
        "adjusted_alpha": adjusted_alpha,
    }
