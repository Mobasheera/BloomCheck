"""Repeatable CLI performance experiment for BloomCheck."""
from __future__ import annotations

import argparse
import statistics
import time
from pathlib import Path

from bloom_filter import BloomFilter
from database import DEFAULT_DB_PATH, get_all_emails, initialize_database, is_registered


def run_benchmark(query_count: int = 500, trials: int = 5, db_path: str | Path = DEFAULT_DB_PATH) -> dict:
    if query_count <= 0 or trials <= 0:
        raise ValueError("query_count and trials must be positive")
    initialize_database(db_path)
    emails = get_all_emails(db_path)
    bloom = BloomFilter()
    for email in emails:
        bloom.add(email)
    candidates = [f"benchmark-absent-{i:05d}@example.org" for i in range(max(query_count, 1000))]
    queries = []
    for i in range(query_count):
        queries.append(emails[(i * 13) % len(emails)] if i % 2 == 0 else candidates[(i * 17) % len(candidates)])

    methods = {
        "linear": lambda query: query in emails,
        "sqlite": lambda query: is_registered(query, db_path),
        "bloom_with_exact_verification": lambda query: False if not bloom.check(query)["possibly_present"] else is_registered(query, db_path),
    }
    measurements = {}
    for name, method in methods.items():
        for query in queries[:min(30, query_count)]:
            method(query)
        durations = []
        for _ in range(trials):
            start = time.perf_counter()
            output = [method(query) for query in queries]
            durations.append((time.perf_counter() - start) * 1000)
            assert len(output) == query_count
        measurements[name] = {
            "trial_ms": [round(value, 3) for value in durations],
            "average_ms": round(statistics.mean(durations), 3),
            "average_microseconds_per_query": round(statistics.mean(durations) * 1000 / query_count, 3),
        }
    return {"record_count": len(emails), "query_count": query_count, "trials": trials, "results": measurements}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queries", type=int, default=500, help="queries per trial")
    parser.add_argument("--trials", type=int, default=5, help="number of measured trials")
    args = parser.parse_args()
    for name, details in run_benchmark(args.queries, args.trials)["results"].items():
        print(f"{name}: average {details['average_ms']} ms; per query {details['average_microseconds_per_query']} µs; trials {details['trial_ms']}")
