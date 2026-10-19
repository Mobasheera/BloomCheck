# BloomCheck Architecture

## Components

- **`templates/index.html` and `templates/benchmark.html`**: semantic page structure and accessible controls.
- **`static/css/style.css`**: responsive presentation, color tokens and reduced-motion handling.
- **`static/js/app.js` and `static/js/benchmark.js`**: call the local API, render backend-supplied state, and report network errors.
- **`app.py`**: creates the Flask app, initializes its dataset and Bloom filter, validates requests, coordinates screening and exact verification, and exposes JSON routes.
- **`bloom_filter.py`**: implements bit operations, deterministic double hashing, membership screening and statistics.
- **`database.py`**: owns SQLite setup and parameterized exact membership queries.
- **`dataset_generator.py`**: creates the fixed synthetic `memberNNNN@example.com` reference set.
- **`benchmark.py`**: provides a repeatable command-line comparison of the three lookup methods.

## Startup and data consistency

At startup, Flask initializes `registered_emails` in SQLite using a stable synthetic dataset. It then reads the database collection and inserts those same normalized addresses into one in-memory `BloomFilter`. The `/api/stats` route surfaces a consistency indicator by comparing the database row count with the filter's startup insertion count. If modifying the dataset or initialization logic, update/rebuild both representations together.

## Email check flow

1. The browser validates the most common email shape for quick feedback and posts JSON to `POST /api/check`.
2. Flask validates the request independently, trims surrounding whitespace and lowercases the address.
3. The Bloom filter derives seven positions from two domain-separated SHA-256 digests and returns the bit values.
4. If any checked bit is 0, the request can return **available** without querying SQLite, because a correctly synchronized Bloom filter cannot exclude an inserted member.
5. If every checked bit is 1, Flask performs a parameterized exact equality lookup in SQLite. The database tells whether the address is **registered** or whether the filter yielded a **false positive**.
6. The response carries the actual positions, values, preliminary result, whether verification ran and the final result. The browser uses those values to update the position chips, bit map, decision path and recent-check history.

## Supporting API routes

- `GET /api/stats`: current bit and data statistics plus estimated theoretical false-positive probability.
- `GET /api/filter`: complete bounded bit-array JSON for this 10,000-bit project configuration.
- `GET /api/history`: latest checks from bounded process memory; no permanent query log.
- `POST /api/demo/insert`: inserts into a temporary clone for inspection only, leaving the live filter and database untouched.
- `POST /api/demo/false-positive`: searches a bounded deterministic sequence and returns only a candidate that the filter considers possible and SQLite confirms absent.
- `GET /api/benchmark` and `POST /api/benchmark`: page and repeated timing experiment.
- `GET /api/health`: local status check.

## Concurrency and scope

A process-local reentrant lock prevents requests from reading or updating filter-related in-memory state concurrently in ways that would confuse the demo. The reference database is accessed through SQLite with parameterized statements. The app binds to `127.0.0.1` and runs with Flask's debug mode disabled by default. This project is for local demonstration, not a hardened production service.

## Complexity and limitations

- Bloom filter insertion and screening: O(k) operations, where k is the configured number of hash positions.
- Linear exact scan: O(n) worst-case comparisons.
- SQLite equality membership check: index-assisted and workload/storage-engine dependent; do not assume a specific measured runtime.
- Approximate Bloom-filter false-positive probability: `(1 - exp(-kn/m))^k` under the standard idealized model.
- This filter does not support deletion. False positives are inherent. The simplified lowercase/trim email normalization and synthetic dataset are teaching choices, not production identity policy.
