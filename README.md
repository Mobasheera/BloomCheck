# BloomCheck

**Bloom Filter Based Email Availability Checker and Visualizer** — a beginner-friendly Big Data Analytics mini-project.

BloomCheck demonstrates how a Bloom filter can screen a collection of email addresses efficiently, how false positives arise, and why a positive result must be verified against an exact reference database. It is an educational demonstration, not an authentication or account-creation service. It is not affiliated with Google and does not claim that Google's systems use Bloom filters.

## Features

- Clean responsive two-panel interface with a Google-inspired blue/white palette.
- Hand-built Bloom filter using a compact `bytearray` and deterministic SHA-256 double hashing.
- 1,000 deterministic synthetic addresses using the reserved `example.com` domain.
- Exact SQLite verification for possible positives; definite negatives avoid the exact lookup.
- Live bit-map, queried positions, bit values, occupancy and theoretical false-positive estimate.
- Bounded, reproducible false-positive candidate search that only reports candidates confirmed absent by SQLite.
- Insertion simulation against a temporary filter, leaving the live collection unchanged.
- Repeated performance benchmark for a linear scan, indexed SQLite lookup, and Bloom filter with exact verification.
- Automated tests for the filter, database, routes, request validation and demonstrations.
- No third-party APIs, accounts, analytics, database server or front-end framework required.

## Requirements

- Windows 11
- Python 3.10 or newer (Python 3.11/3.12 recommended)
- VS Code (recommended)
- Internet is needed only to install Flask for the first time; the application itself runs locally without online services.

## Run on Windows 11 (VS Code)

1. Download and extract the ZIP, or clone the repository.
2. Open the `BloomCheck` folder in VS Code.
3. Open **Terminal → New Terminal**. Confirm you are in the folder containing `app.py`.
4. Create a virtual environment:

   ```powershell
   py -m venv .venv
   ```

5. Activate it in PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use the Command Prompt terminal and run:

   ```bat
   .venv\Scripts\activate.bat
   ```

6. Install the one web dependency:

   ```powershell
   py -m pip install -r requirements.txt
   ```

7. Start the local app:

   ```powershell
   py app.py
   ```

8. Open **http://127.0.0.1:5000** in Firefox or your preferred browser. Keep the terminal open while using the app. Stop the server with `Ctrl+C`.

The first startup creates `data/bloomcheck.sqlite3` and inserts the deterministic synthetic dataset. It is generated automatically; there is no need to download or create a database manually.

## Try the demo

- Registered sample: `member0001@example.com`
- Another registered sample: `member0420@example.com`
- Likely absent sample: `new-person@example.org`
- Try uppercase or surrounding spaces to see the documented normalization policy.
- Use **Insertion simulator** to see which bits would be set without changing the live collection.
- Use **Find a false positive** to search up to 50,000 deterministic synthetic non-member candidates. A result is shown only if every queried bit is set and SQLite confirms the candidate is not registered. If none is found within the bound, the UI reports that honestly.
- Open **Performance experiment** and run the same controlled query set through three strategies.

## Run tests

With the virtual environment activated:

```powershell
py -m unittest discover -s tests -v
```

The suite uses temporary databases for isolation and does not depend on a previously generated project database.

## Run the command-line benchmark

```powershell
py benchmark.py
py benchmark.py --queries 1000 --trials 5
```

Reported times are measurements from your computer; they are not fixed project claims. Linear scan is O(n) per lookup; SQLite uses an indexed equality query; a Bloom filter lookup takes O(k) bit checks, but this implementation adds SQLite verification for possible positives. At 1,000 entries, SQLite may already be very fast and observed timings can vary.

## How the algorithm works

1. The synthetic dataset is normalized (trim surrounding whitespace, lowercase) and loaded into SQLite.
2. On application startup, the same records are inserted into a 10,000-bit Bloom filter.
3. SHA-256 is domain-separated into two deterministic digests. Double hashing derives seven positions: `position_i = (h1 + i × h2) mod m`.
4. An insertion sets each addressed bit to 1 and never clears a bit.
5. A query with any addressed bit at 0 is **definitely not present** in a synchronized filter. When every addressed bit is 1, the query is **possibly present**.
6. Possible positives are verified by an exact, parameterized SQLite query. The database determines the final answer.

The theoretical false-positive estimate is calculated at runtime from the actual capacity, hash count and number of inserted addresses using `(1 - e^(-kn/m))^k`. It is not the measured false-positive rate. The observed rate depends on the actual contents and workload.

## Architecture

```text
Browser (HTML / CSS / vanilla JavaScript)
              │ Fetch JSON API
              ▼
         Flask (app.py)
          │          │
          ▼          ▼
    BloomFilter    SQLite database
  (bytearray bits) (exact reference)
```

See [`docs/architecture.md`](docs/architecture.md) for responsibilities and request flow.

## Project structure

```text
BloomCheck/
├── app.py
├── bloom_filter.py
├── database.py
├── dataset_generator.py
├── benchmark.py
├── requirements.txt
├── README.md
├── LICENSE
├── .gitignore
├── data/
│   └── .gitkeep
├── templates/
│   ├── index.html
│   └── benchmark.html
├── static/
│   ├── css/style.css
│   └── js/
│       ├── app.js
│       └── benchmark.js
├── tests/
│   ├── test_bloom_filter.py
│   ├── test_database.py
│   └── test_api.py
└── docs/architecture.md
```

## Design and data notes

- The filter uses a compact `bytearray`, not a Python list of integer objects.
- A fixed, deterministic sample keeps demonstrations reproducible and uses only reserved example domains.
- The app keeps recent checks in bounded process memory only. It does not persist submitted queries or store passwords.
- The insertion tool simulates a write on a temporary filter so SQLite and the live filter remain synchronized.
- The simplified lowercase/trim normalization is for this educational exercise. Real email normalization rules have nuances, and provider-specific rules should not be blindly applied.
- A Bloom filter has no deletion in this implementation and can return false positives, but a correctly synchronized filter does not return false negatives for inserted items.
- The theoretical formula assumes an idealized hash model; empirical observations need to be measured separately.

## Troubleshooting

- **`py` is not recognized:** install Python from python.org and enable the launcher/PATH options, then reopen VS Code.
- **Flask module missing:** activate the `.venv` and run `py -m pip install -r requirements.txt` again.
- **Address already in use:** stop the other process using port 5000, or adjust the port in the final `app.run(...)` line of `app.py` and open the matching URL.
- **PowerShell script activation blocked:** use the Command Prompt activation command above. Running `py .venv\Scripts\python.exe app.py` is another way to use the venv without activating it.
- **Database/filter mismatch after code changes:** stop Flask and remove `data/bloomcheck.sqlite3`, then restart. The app recreates the default generated dataset. Do not delete it while the server is running.

## Future improvements

- Add controlled dataset-size and filter-parameter experiments.
- Record precision/recall-style experiment summaries for a known query corpus.
- Compare alternative hash counts and bit-array capacities.
- Add exportable benchmark results for inclusion in the short academic report.

## License

MIT. See [`LICENSE`](LICENSE).
