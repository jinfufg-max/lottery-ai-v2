import random
from collections import Counter

def analyze_history(history):
    numbers = []
    specials = []

    for row in history:
        nums = row[:-1]
        sp = row[-1]
        numbers.extend(nums)
        specials.append(sp)

    num_freq = Counter(numbers)
    sp_freq = Counter(specials)

    return num_freq, sp_freq


def generate_combinations(num_freq, sp_freq, n_groups=200):
    nums = [n for n, _ in num_freq.most_common(30)]
    sps = [s for s, _ in sp_freq.most_common(10)]

    results = []

    for _ in range(n_groups):
        combo = sorted(random.sample(nums, 6))
        sp = random.choice(sps)

        score = sum(num_freq[n] for n in combo) + sp_freq[sp]

        results.append((combo, sp, score))

    results.sort(key=lambda x: x[2], reverse=True)

    return results


def split_groups(data):
    return {
        "大銀袋": data[:100],
        "大金袋": data[100:160],
        "準提銀袋": data[160:200],
        "準提金袋": data[200:210],
    }