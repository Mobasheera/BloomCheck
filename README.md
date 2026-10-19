::: {align="center"}
`<img src="docs/bloomcheck-logo.svg" alt="BloomCheck logo" width="460">`{=html}

### Bloom Filter Based Email Availability Checker & Visualizer

**Check smarter. Understand every bit.**

An interactive Big Data Analytics mini-project that makes Bloom filters
easier to explore---one query, hash position, and bit at a time.

```{=html}
<p>
```
`<img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white">`{=html}
`<img alt="Flask" src="https://img.shields.io/badge/Flask-3.x-202124?style=flat-square&logo=flask&logoColor=white">`{=html}
`<img alt="SQLite" src="https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white">`{=html}
`<img alt="License" src="https://img.shields.io/badge/License-MIT-34A853?style=flat-square">`{=html}
`<img alt="Runs locally" src="https://img.shields.io/badge/Mode-Local%20Demo-1A73E8?style=flat-square">`{=html}
```{=html}
</p>
```
[Features](#-features) · [Quick start](#-quick-start-windows-11) · [How
it works](#-how-it-works) · [Project structure](#-project-structure) ·
[Tests](#-run-the-tests)
:::

------------------------------------------------------------------------

## ✨ What is BloomCheck?

BloomCheck demonstrates how a **Bloom filter** can quickly screen
email-like identifiers before an exact database lookup. The app
visualizes the filter's bit array and hash positions, explains the
result of each query, and shows why a positive Bloom filter result means
**"possibly present"**, not "definitely present."

> \[!NOTE\] BloomCheck is an educational demonstration using synthetic
> addresses. It is not a real account-registration or email-verification
> service, is not affiliated with Google, and makes no claim about
> Google's internal systems. The blue-and-white interface is inspired by
> familiar sign-in design patterns without using Google branding.

## 🌟 Features

  -----------------------------------------------------------------------
  Feature                             What you can explore
  ----------------------------------- -----------------------------------
  **Email availability checker**      Query a sample address and inspect
                                      the decision path.

  **Bloom filter visualizer**         See the bit array, the positions
                                      checked, bit values, and occupancy.

  **Exact verification**              Possible positives are checked
                                      against SQLite to distinguish
                                      registered samples from false
                                      positives.

  **False-positive explorer**         Search a bounded, deterministic set
                                      of non-member candidates and show a
                                      false positive only when SQLite
                                      confirms it.

  **Insertion simulator**             Preview the bits an address would
                                      set without modifying the live
                                      dataset.

  **Performance experiment**          Compare linear scan, indexed SQLite
                                      lookup, and Bloom filter screening
                                      with exact verification.

  **Responsive interface**            Clean Google-inspired
                                      blue-and-white styling for desktop
                                      and mobile.

  **Local-first setup**               No API keys, third-party services,
                                      account sign-in, or separate
                                      database server required.
  -----------------------------------------------------------------------

## 🚀 Quick start (Windows 11)

### 1. Requirements

-   Windows 11
-   Python **3.10 or newer** (Python 3.11 or 3.12 recommended)
-   VS Code (recommended)

### 2. Open the project

Download or clone this repository, then open the `BloomCheck` folder in
VS Code. In VS Code, choose **Terminal → New Terminal**.

### 3. Create and activate a virtual environment

``` powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, open a Command Prompt terminal and use:

``` bat
.venv\Scripts\activate.bat
```

### 4. Install dependencies

``` powershell
python -m pip install -r requirements.txt
```

### 5. Start BloomCheck

``` powershell
python app.py
```

Open **http://127.0.0.1:5000** in your browser. Keep the terminal open
while using the app; press `Ctrl+C` to stop the server.

The app initializes its local SQLite database and deterministic sample
dataset automatically on first startup.

## 🧪 Try the demo

Use these synthetic sample addresses:

  Example                    Purpose
  -------------------------- ---------------------------------------
  `member0001@example.com`   Sample address in the dataset
  `member0420@example.com`   Another sample address in the dataset
  `new-person@example.org`   Sample address expected to be absent

Try changing letter case or adding surrounding spaces to explore the
app's normalization policy. Use the insertion simulator, false-positive
explorer, and performance experiment to investigate the behavior
further.

All sample addresses use reserved example domains; they are not real
user records.

## 🧠 How it works

``` text
Address entered
      │
      ▼
Normalize address
(trim + lowercase)
      │
      ▼
Calculate k hash positions
(SHA-256 double hashing)
      │
      ▼
Read Bloom filter bits
      │
      ├── At least one bit is 0 ──► Definitely not present
      │
      └── Every bit is 1 ─────────► Possibly present
                                      │
                                      ▼
                               Exact SQLite lookup
                                      │
                              Final exact answer
```

### The key idea

-   **A zero bit means "definitely absent"** in a correctly synchronized
    filter.
-   **All one bits mean "possibly present."** Different values can set
    the same bits, creating a false positive.
-   **SQLite is the source of truth** for the final result. BloomCheck
    verifies possible positives against the exact dataset.
-   A Bloom filter in this implementation does not support deletion.

The implementation uses a compact `bytearray`, deterministic SHA-256
double hashing, and seven bit positions. The theoretical false-positive
estimate is calculated from the filter's configured capacity, number of
hash functions, and number of inserted entries. It is an estimate, not
the measured false-positive rate.

## 📁 Project structure

``` text
BloomCheck/
├── app.py                    # Flask app and JSON routes
├── bloom_filter.py            # Bloom filter implementation
├── database.py                # SQLite setup and exact lookup
├── dataset_generator.py       # Reproducible synthetic sample data
├── benchmark.py               # Command-line performance benchmark
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── LICENSE                    # MIT license
├── .gitignore                 # Ignores local/generated files
├── data/
│   └── .gitkeep               # Keeps the data folder in Git
├── docs/
│   ├── architecture.md        # Architecture and request flow
│   └── bloomcheck-logo.svg    # Logo used in this README
├── templates/
│   ├── index.html             # Main visualizer
│   └── benchmark.html         # Browser benchmark page
├── static/
│   ├── css/style.css          # Responsive styling
│   └── js/
│       ├── app.js             # Visualizer interactions
│       └── benchmark.js       # Benchmark interactions
└── tests/
    ├── test_bloom_filter.py
    ├── test_database.py
    └── test_api.py
```

The SQLite file is generated locally at runtime and is intentionally not
included in the repository.

## ✅ Run the tests

Activate the virtual environment, then run:

``` powershell
python -m unittest discover -s tests -v
```

The tests cover Bloom filter behavior, database operations, and API
routes. Run them after installing the dependencies.

## 📊 Run the command-line benchmark

``` powershell
python benchmark.py
```

You can also specify the query count and number of trials:

``` powershell
python benchmark.py --queries 1000 --trials 5
```

Results depend on your machine and workload. At the sample dataset size,
indexed SQLite may be very fast; a Bloom filter is not guaranteed to win
every benchmark. The Bloom path also performs exact verification for
possible positives.

## 🔐 Privacy and limitations

-   The included dataset is synthetic and reproducible.
-   Submitted checks are not intended to be persisted as user accounts
    or credentials.
-   Recent-check history is held in bounded application memory.
-   Email normalization is simplified for this educational
    demonstration.
-   The default free Render filesystem is ephemeral. For a hosted demo,
    generated SQLite data may need to be recreated after a restart or
    redeploy; do not use this configuration for persistent real-user
    records.
-   This project illustrates a probabilistic data structure; it is not
    an email-delivery, account-authentication, or security product.

## 🛠️ Troubleshooting

```{=html}
<details>
```
```{=html}
<summary>
```
`<strong>`{=html}`<code>`{=html}py`</code>`{=html} is not
recognized`</strong>`{=html}
```{=html}
</summary>
```
Install Python from
[python.org](https://www.python.org/downloads/windows/), enable the
Python launcher/PATH option if offered, then reopen the VS Code
terminal.
```{=html}
</details>
```
```{=html}
<details>
```
```{=html}
<summary>
```
`<strong>`{=html}`<code>`{=html}ModuleNotFoundError: No module named
'flask'`</code>`{=html}`</strong>`{=html}
```{=html}
</summary>
```
Activate `.venv` and run `python -m pip install -r requirements.txt`
again. Make sure VS Code is using the project's virtual environment.
```{=html}
</details>
```
```{=html}
<details>
```
```{=html}
<summary>
```
`<strong>`{=html}Port 5000 is already in use`</strong>`{=html}
```{=html}
</summary>
```
Stop the other local server using that port, or change the port in the
`app.run(...)` configuration in `app.py` and open the matching local
URL.
```{=html}
</details>
```
```{=html}
<details>
```
```{=html}
<summary>
```
`<strong>`{=html}Database data needs to be regenerated`</strong>`{=html}
```{=html}
</summary>
```
Stop the app first. If you need a fresh synthetic dataset, remove
`data/bloomcheck.sqlite3` and restart the application. It will recreate
the database. Do not delete the database while the server is running.
```{=html}
</details>
```
## 🗺️ Future improvements

-   Configurable filter capacity and hash count.
-   Repeatable false-positive experiments with exportable results.
-   Comparison of multiple Bloom filter configurations.
-   Downloadable benchmark summaries for a project report.

## 📄 License

Released under the [MIT License](LICENSE).

------------------------------------------------------------------------

::: {align="center"}
**BloomCheck** · Big Data Analytics Mini Project

*Check smarter. Understand every bit.*

[GitHub repository](https://github.com/Mobasheera/BloomCheck)
:::
