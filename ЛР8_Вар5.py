"""
Лабораторная работа № 8. Вариант 5.
Задача о рюкзаке 0/1: два жадных критерия (удельная ценность
и минимальный вес) против точного решения (ДП).
N = 25, W = 150. Доп. задание Ж5 — сравнение времени при росте N.
"""
import random
import statistics
import time


# ==================== Точное решение (ДП) ====================

def knapsack_dp(weights, values, capacity):
    """Точное решение 0/1-рюкзака. Возвращает (ценность, состав)."""
    n = len(weights)
    D_full = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        wi, vi = weights[i - 1], values[i - 1]
        for w in range(capacity + 1):
            D_full[i][w] = D_full[i - 1][w]
            if wi <= w and D_full[i - 1][w - wi] + vi > D_full[i][w]:
                D_full[i][w] = D_full[i - 1][w - wi] + vi
    chosen, w = [], capacity
    for i in range(n, 0, -1):
        if D_full[i][w] != D_full[i - 1][w]:
            chosen.append(i - 1)
            w -= weights[i - 1]
    return D_full[n][capacity], sorted(chosen)


def knapsack_dp_value_only(weights, values, capacity):
    """Только значение оптимума (для Ж5 — быстрее по памяти)."""
    D = [0] * (capacity + 1)
    for wi, vi in zip(weights, values):
        for w in range(capacity, wi - 1, -1):
            if D[w - wi] + vi > D[w]:
                D[w] = D[w - wi] + vi
    return D[capacity]


# ==================== Жадные алгоритмы ====================

def knapsack_greedy(weights, values, capacity, key):
    order = sorted(range(len(weights)), key=key, reverse=True)
    total, remain, chosen = 0, capacity, []
    for i in order:
        if weights[i] <= remain:
            chosen.append(i)
            remain -= weights[i]
            total += values[i]
    return total, sorted(chosen)


def greedy_density(weights, values, capacity):
    """Критерий 1: максимальная удельная ценность vᵢ / wᵢ."""
    return knapsack_greedy(weights, values, capacity,
                           key=lambda i: values[i] / weights[i])


def greedy_min_weight(weights, values, capacity):
    """Критерий 2: минимальный вес (сначала самые лёгкие)."""
    return knapsack_greedy(weights, values, capacity,
                           key=lambda i: -weights[i])


# ==================== Эксперименты ====================

def experiment(trials=500, n=25, capacity=150, seed=2025):
    rng = random.Random(seed)
    names = ["Удельная ценность", "Минимальный вес"]
    dev = {k: [] for k in names}
    exact_hits = {k: 0 for k in names}
    for _ in range(trials):
        weights = [rng.randint(5, 40) for _ in range(n)]
        values = [rng.randint(10, 100) for _ in range(n)]
        opt, _ = knapsack_dp(weights, values, capacity)
        for name, func in [("Удельная ценность", greedy_density),
                           ("Минимальный вес", greedy_min_weight)]:
            got, _ = func(weights, values, capacity)
            dev[name].append((opt - got) / opt * 100)
            if got == opt:
                exact_hits[name] += 1
    return dev, exact_hits, trials


def time_scaling(capacity=150, seed=1):
    rng = random.Random(seed)
    results = []
    for n in [50, 100, 200, 500, 1000, 2000, 5000, 10_000, 20_000]:
        weights = [rng.randint(5, 40) for _ in range(n)]
        values = [rng.randint(10, 100) for _ in range(n)]

        t0 = time.perf_counter()
        greedy_density(weights, values, capacity)
        t_greedy = time.perf_counter() - t0

        t0 = time.perf_counter()
        knapsack_dp_value_only(weights, values, capacity)
        t_dp = time.perf_counter() - t0

        results.append((n, t_greedy, t_dp))

        if t_dp > 10:
            break
    return results


# ==================== Запуск ====================

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # ---------- Контрпример ----------
    print("--- Контрпример (W = 10) ---")
    w, v, W = [6, 5, 5], [12, 9, 9], 10
    g1, ch1 = greedy_density(w, v, W)
    g2, ch2 = greedy_min_weight(w, v, W)
    opt, _ = knapsack_dp(w, v, W)
    print(f"  Веса: {w}, ценности: {v}, W = {W}")
    print(f"  Жадно по vᵢ/wᵢ: предметы {ch1}, ценность {g1}, "
          f"отклонение {(opt - g1) / opt * 100:.1f}%")
    print(f"  Жадно по min wᵢ: предметы {ch2}, ценность {g2}, "
          f"отклонение {(opt - g2) / opt * 100:.1f}%")
    print(f"  Оптимум (ДП):    ценность {opt}\n")

    # ---------- Серия экспериментов ----------
    dev, hits, trials = experiment()
    print(f"--- Серия из {trials} случайных наборов (N = 25, W = 150) ---")
    print(f"{'Критерий':<24}{'среднее, %':>12}{'медиана, %':>12}"
          f"{'максимум, %':>13}{'совпало с оптимумом':>22}")
    for name, d in dev.items():
        print(f"{name:<24}{statistics.mean(d):>12.2f}"
              f"{statistics.median(d):>12.2f}{max(d):>13.2f}"
              f"{hits[name] / trials * 100:>21.1f}%")

    # ---------- Ж5: масштабирование ----------
    print(f"\n--- Ж5: время при росте N (W = 150) ---")
    scaling = time_scaling()
    print(f"{'N':>8}{'жадный, с':>14}{'ДП, с':>12}{'ДП / жадный':>14}")
    for n, tg, td in scaling:
        print(f"{n:>8}{tg:>14.4f}{td:>12.4f}{td / tg:>14.1f}")

    print("\nЭкстраполяция: при каком N ДП превысит 10 с?")
    n_last, _, t_last = scaling[-1]
    c = t_last / (n_last * 150)
    n_critical = int(10 / (c * 150))
    print(f"  Оценка: T_dp(N) ≈ {c:.2e} · N · W")
    print(f"  При W = 150: N ≈ {n_critical} → 10 с")
    print(f"  При W = 1000: N ≈ {int(10 / (c * 1000))} → 10 с")

    # ---------- Графики ----------
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].hist(dev["Удельная ценность"], bins=30, alpha=0.6,
                 label="vᵢ/wᵢ", color="steelblue")
    axes[0].hist(dev["Минимальный вес"], bins=30, alpha=0.6,
                 label="min wᵢ", color="darkorange")
    axes[0].set_xlabel("Отклонение от оптимума, %")
    axes[0].set_ylabel("Число наборов")
    axes[0].set_title("Распределение отклонений (500 наборов)")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    ns = [r[0] for r in scaling]
    tg = [r[1] for r in scaling]
    td = [r[2] for r in scaling]
    axes[1].loglog(ns, tg, "o-", label="Жадный")
    axes[1].loglog(ns, td, "s-", label="ДП")
    axes[1].axhline(10, color="red", ls="--", label="10 с")
    axes[1].set_xlabel("N (лог. шкала)")
    axes[1].set_ylabel("Время, с (лог. шкала)")
    axes[1].set_title("Ж5: время при росте N (W = 150)")
    axes[1].legend()
    axes[1].grid(True, which="both", alpha=0.3)

    plt.tight_layout()
    plt.savefig("lr8_plot.png", dpi=150)
    plt.show()