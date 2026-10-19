"""Flask application for the BloomCheck educational demonstration."""
from __future__ import annotations

import re
import threading
from collections import deque
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, render_template, request

from bloom_filter import BloomFilter, normalize_email
from database import DEFAULT_DB_PATH, count_emails, get_all_emails, initialize_database, is_registered
from dataset_generator import generate_emails

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def valid_email(value: Any) -> bool:
    return isinstance(value, str) and len(value.strip()) <= 254 and bool(EMAIL_PATTERN.fullmatch(value.strip()))


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(DB_PATH=str(DEFAULT_DB_PATH), FILTER_CAPACITY=10_000, HASH_COUNT=7, DATASET_SIZE=1_000, HISTORY_LIMIT=8, TESTING=False)
    if test_config:
        app.config.update(test_config)

    db_path = Path(app.config["DB_PATH"])
    initialize_database(db_path, generate_emails(app.config["DATASET_SIZE"]))
    emails = get_all_emails(db_path)
    bloom = BloomFilter(app.config["FILTER_CAPACITY"], app.config["HASH_COUNT"])
    for email in emails:
        bloom.add(email)
    history: deque[dict[str, Any]] = deque(maxlen=app.config["HISTORY_LIMIT"])
    lock = threading.RLock()

    app.extensions["bloomcheck"] = {"bloom": bloom, "history": history, "lock": lock, "db_path": db_path}

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/stats")
    def stats():
        with lock:
            actual_count = count_emails(db_path)
            payload = bloom.stats()
            payload.update({"expected_count": app.config["DATASET_SIZE"], "actual_count": actual_count, "synchronized": actual_count == bloom.inserted_count})
            return jsonify(payload)

    @app.get("/api/filter")
    def filter_data():
        with lock:
            return jsonify({"capacity": bloom.capacity, "bits": bloom.bit_array(), "set_bits": bloom.set_bits, "unset_bits": bloom.unset_bits})

    @app.get("/api/history")
    def get_history():
        with lock:
            return jsonify({"history": list(history)})

    @app.post("/api/check")
    def check_email():
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or "email" not in data:
            return jsonify({"error": "Send a JSON object with an 'email' field."}), 400
        email = data.get("email")
        if not valid_email(email):
            return jsonify({"error": "Enter a valid email address, such as name@example.com."}), 400
        normalized = normalize_email(email)
        with lock:
            outcome = bloom.check(normalized)
            exact_performed = bool(outcome["possibly_present"])
            exact_registered = is_registered(normalized, db_path) if exact_performed else False
            if not outcome["possibly_present"]:
                status = "available"
                title = "Available"
                explanation = "At least one required bit is 0, so this synchronized Bloom filter definitively excludes the address."
            elif exact_registered:
                status = "registered"
                title = "Already registered"
                explanation = "All queried bits were 1, so the filter reported a possible match. SQLite confirmed the address exists."
            else:
                status = "false_positive"
                title = "Possible match — not registered"
                explanation = "All queried bits were 1, but SQLite confirmed the address is absent. This is a genuine Bloom-filter false positive."
            result = {
                "email": normalized,
                "positions": outcome["positions"],
                "bit_values": outcome["bit_values"],
                "zero_positions": outcome["zero_positions"],
                "preliminary_result": "possibly_present" if outcome["possibly_present"] else "definitely_not_present",
                "exact_verification_performed": exact_performed,
                "exact_registered": exact_registered if exact_performed else None,
                "status": status,
                "title": title,
                "explanation": explanation,
            }
            history.appendleft({"email": normalized, "status": status, "title": title})
            return jsonify(result)

    @app.post("/api/demo/false-positive")
    def false_positive_demo():
        with lock:
            # Bounded deterministic candidate search; never invents an outcome.
            for index in range(1, 50_001):
                candidate = f"false-positive-candidate-{index:05d}@example.org"
                check = bloom.check(candidate)
                if check["possibly_present"] and not is_registered(candidate, db_path):
                    result = {
                        "found": True,
                        "email": candidate,
                        "positions": check["positions"],
                        "bit_values": check["bit_values"],
                        "zero_positions": check["zero_positions"],
                        "preliminary_result": "possibly_present",
                        "exact_verification_performed": True,
                        "exact_registered": False,
                        "status": "false_positive",
                        "title": "Genuine false positive found",
                        "explanation": "Every addressed bit is set, but SQLite confirms this synthetic candidate is absent. The Bloom filter can say 'possibly present', not 'definitely registered'.",
                    }
                    history.appendleft({"email": candidate, "status": "false_positive", "title": "False positive demo"})
                    return jsonify(result)
            return jsonify({"found": False, "message": "No false-positive candidate was found within the 50,000-candidate search limit. No result was fabricated."})

    @app.post("/api/demo/insert")
    def insertion_demo():
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or not valid_email(data.get("email")):
            return jsonify({"error": "Send a valid email address in the 'email' field."}), 400
        candidate = normalize_email(data["email"])
        # A read-only hypothetical insertion demo: mutate a cloned filter, never source state.
        with lock:
            clone = BloomFilter(bloom.capacity, bloom.hash_count)
            for stored in get_all_emails(db_path):
                clone.add(stored)
            trace = clone.add(candidate)
            return jsonify({"email": candidate, "positions": trace["positions"], "before": trace["before"], "after": trace["after"], "changed_positions": trace["changed_positions"], "already_set_positions": trace["already_set_positions"], "bits": clone.bit_array(), "set_bits": clone.set_bits, "note": "Simulation only. The SQLite dataset and live Bloom filter were not modified."})

    @app.get("/benchmark")
    def benchmark_page():
        return render_template("benchmark.html")

    @app.post("/api/benchmark")
    def run_benchmark():
        import time
        data = request.get_json(silent=True)
        if data is None:
            data = {}
        if not isinstance(data, dict):
            return jsonify({"error": "Send a JSON object with benchmark options."}), 400
        try:
            query_count = int(data.get("query_count", 500))
            trials = int(data.get("trials", 5))
        except (TypeError, ValueError):
            return jsonify({"error": "Query count and trial count must be integers."}), 400
        if query_count not in {100, 500, 1000, 2000} or trials not in {3, 5, 10}:
            return jsonify({"error": "Choose one of the supported query and trial counts."}), 400
        with lock:
            collection = get_all_emails(db_path)
            members = collection[:]
            candidates = [f"benchmark-absent-{i:05d}@example.org" for i in range(max(query_count, 1000))]
            pool = members + candidates
            queries = [pool[(i * 37 + 11) % len(pool)] for i in range(query_count)]
            # Rotate a deterministic workload with both known members and non-members.
            for i in range(0, len(queries), 2):
                queries[i] = members[(i * 13) % len(members)]
            for i in range(1, len(queries), 2):
                queries[i] = candidates[(i * 17) % len(candidates)]
            def linear(query: str) -> bool:
                return query in collection
            def sqlite_lookup(query: str) -> bool:
                return is_registered(query, db_path)
            def bloom_verified(query: str) -> bool:
                return False if not bloom.check(query)["possibly_present"] else is_registered(query, db_path)
            methods = [("linear", linear), ("sqlite", sqlite_lookup), ("bloom", bloom_verified)]
            # Warm-up runs are excluded from results.
            for _, method in methods:
                for query in queries[:min(30, len(queries))]:
                    method(query)
            results = []
            for label, method in methods:
                trial_ms = []
                for _ in range(trials):
                    start = time.perf_counter()
                    outputs = [method(query) for query in queries]
                    elapsed = (time.perf_counter() - start) * 1000
                    trial_ms.append(elapsed)
                results.append({"method": label, "trial_ms": [round(value, 3) for value in trial_ms], "average_ms": round(sum(trial_ms) / len(trial_ms), 3), "average_us_per_query": round((sum(trial_ms) / len(trial_ms)) * 1000 / len(queries), 3), "correct_results": len(outputs) == len(queries)})
            return jsonify({"query_count": query_count, "trials": trials, "record_count": len(collection), "results": results, "note": "Times are environment-dependent. All strategies used the same query list; Bloom results performed SQLite verification for possible positives."})

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app


app = create_app()

if __name__ == "__main__":
    # Development server only. Do not expose this configuration to the public internet.
    app.run(host="127.0.0.1", port=5000, debug=False)
