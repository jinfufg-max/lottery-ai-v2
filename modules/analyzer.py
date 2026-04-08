def analyze(numbers):
    return {
        "count": len(numbers),
        "max": max(numbers) if numbers else None,
        "min": min(numbers) if numbers else None
    }
