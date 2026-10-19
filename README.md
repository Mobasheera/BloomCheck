<div align="center">

<img src="docs/bloomcheck-logo.svg" alt="BloomCheck logo" width="420">

# Bloom Filter Based Email Availability Checker and Visualizer

**Check smarter. Understand every bit.**

An interactive Big Data Analytics mini-project that demonstrates how Bloom filters can quickly screen email-like identifiers, visualize hash positions, and explain false positives using an exact SQLite lookup.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-202124?style=flat-square&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![JavaScript](https://img.shields.io/badge/Frontend-JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=202124)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat-square&logo=css3&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-34A853?style=flat-square)

</div>

---

## 📌 Overview

BloomCheck is an educational web application for exploring a **Bloom filter**, a space-efficient probabilistic data structure used to test whether an item may belong to a set.

The application accepts an email-like identifier, checks the Bloom filter, displays the relevant bit positions, and uses SQLite to verify possible matches against a sample dataset. It also includes visual experiments for insertion, false positives, and performance comparisons.

> **Important:** BloomCheck is a learning/demo project. It uses synthetic example addresses and is not a real account-registration, authentication, or email-verification service. It is not affiliated with Google.

## ✨ Features

- **Email availability checker** — check a sample address and inspect the result.
- **Bloom filter visualizer** — see the bit array, hash positions, bit values, and occupancy.
- **Exact SQLite verification** — verify possible Bloom filter matches against the underlying sample dataset.
- **False-positive explorer** — explore candidates that are absent from the dataset but may pass the Bloom filter.
- **Insertion simulator** — preview the bit positions an address would set without changing the live dataset.
- **Performance benchmark** — compare lookup approaches and view timing results.
- **Recent checks** — view a bounded history of recent queries during the running session.
- **Responsive UI** — a clean blue-and-white interface inspired by modern sign-in pages.
- **Local-first setup** — no API keys or separate database server required.

## 🧰 Technology Stack

| Technology | Role in BloomCheck |
|---|---|
| **Python 3** | Main programming language and Bloom filter logic |
| **Flask** | Web server and JSON API routes |
| **SQLite** | Local dataset and exact membership verification |
| **HTML5** | Page structure and interface elements |
| **CSS3** | Layout, styling, responsive design, and visual states |
| **JavaScript** | Interactive checks, bit visualizations, and benchmark UI |
| **SHA-256** | Deterministic hash input for Bloom filter position generation |
| **`unittest`** | Automated tests for core logic, database, and API |

## 🧠 How It Works

```text
User enters an email-like address
              │
              ▼
       Normalize the input
       (trim and lowercase)
              │
              ▼
       Calculate hash positions
       (SHA-256 double hashing)
              │
              ▼
        Read Bloom filter bits
              │
        ┌─────┴─────┐
        │           │
  Any bit is 0   Every bit is 1
        │           │
        ▼           ▼
 Definitely not   Possibly present
    present           │
                      ▼
              Exact SQLite lookup
                      │
                      ▼
               Final exact result
```

### Understanding the result

- **Definitely not present:** At least one required bit is `0`. Assuming the filter and dataset are synchronized, the item is not in the set.
- **Possibly present:** All required bits are `1`. The item may be in the set, or it may be a false positive.
- **Exact verification:** BloomCheck queries SQLite to determine whether a possible match is actually present in the sample dataset.

A Bloom filter can produce false positives, but a correctly configured Bloom filter does not produce false negatives for items inserted into that same filter. Deletion is not supported by this basic implementation.

## 🚀 Quick Start — Windows 11

### Requirements

- Windows 11
- Python 3.10 or newer (Python 3.11 or 3.12 recommended)
- VS Code (recommended)
- Firefox, Edge, or another modern browser

### 1. Open the project

Download or clone this repository and open the `BloomCheck` folder in VS Code. Select **Terminal → New Terminal**.

### 2. Create a virtual environment

```powershell
py -m venv .venv
```

### 3. Activate the environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use a Command Prompt terminal instead:

```bat
.venv\Scripts\activate.bat
```

### 4. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 5. Run the app

```powershell
python app.py
```

Open this address in your browser:

**http://127.0.0.1:5000**

Keep the terminal open while using BloomCheck. Press `Ctrl+C` in the terminal to stop the local server.

The application initializes its local SQLite database and sample dataset automatically when needed.

## 🧪 Sample Inputs

The generated dataset uses synthetic addresses under reserved example domains.

| Example | Intended use |
|---|---|
| `member0001@example.com` | Check an address included in the sample dataset |
| `member0420@example.com` | Check another sample member |
| `new-person@example.org` | Check an address expected to be absent |

Input normalization trims surrounding whitespace and converts the address to lowercase. These examples are for demonstrations only; they are not real user accounts.

## 📊 Benchmark

BloomCheck includes a benchmark interface and a command-line benchmark script for comparing membership-check approaches.

Run the command-line benchmark from the project root:

```powershell
python benchmark.py
```

If supported by the script, query count and trial options can be supplied as command-line arguments; run `python benchmark.py --help` to see the available options.

Benchmark timings depend on the machine, dataset size, and workload. A Bloom filter is not guaranteed to outperform indexed SQLite for every small dataset. Since BloomCheck verifies possible positives against SQLite, the total time includes that verification work.

## 🗂️ Project Structure

```text
BloomCheck/
├── app.py                    # Flask app and API routes
├── bloom_filter.py            # Bloom filter implementation
├── database.py                # SQLite setup and exact lookup
├── dataset_generator.py       # Synthetic sample data
├── benchmark.py               # Performance benchmark
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
├── LICENSE                    # MIT license
├── .gitignore                 # Ignored local/generated files
├── data/
│   └── .gitkeep               # Keeps the data folder in Git
├── docs/
│   ├── architecture.md        # Architecture notes
│   └── bloomcheck-logo.svg    # README logo
├── templates/
│   ├── index.html             # Main visualizer page
│   └── benchmark.html         # Benchmark page
├── static/
│   ├── css/style.css          # Responsive styles
│   └── js/
│       ├── app.js             # Main UI interactions
│       └── benchmark.js       # Benchmark interactions
└── tests/
    ├── test_bloom_filter.py
    ├── test_database.py
    └── test_api.py
```

The SQLite database is generated locally and should not be committed to GitHub.

## ✅ Run Tests

Activate the virtual environment, install the requirements, and run:

```powershell
python -m unittest discover -s tests -v
```

The test suite covers Bloom filter behavior, database operations, and API routes.

## 🌐 Deployment Notes

BloomCheck can run locally or be deployed as a Flask web service, for example on Render. The included synthetic dataset is suitable for a demonstration, not production account data.

On a free hosting instance with an ephemeral filesystem, local SQLite data may be lost after a restart or redeploy and need to be regenerated. Do not store real user accounts, passwords, or sensitive data in this demo configuration.

## 🔒 Privacy & Limitations

- The dataset contains generated example addresses, not real users.
- The application is an educational visualization, not a production email verification or authentication system.
- Email normalization is intentionally simplified.
- A standard Bloom filter does not support deletion.
- The theoretical false-positive probability is an estimate; measured outcomes depend on the actual inserted items and queries.
- Recent-check history is session/process-local and is not intended as permanent storage.

## 🛠️ Troubleshooting

<details>
<summary><strong><code>py</code> is not recognized</strong></summary>

Install Python from [python.org](https://www.python.org/downloads/windows/), ensure the Python launcher is available, then reopen the VS Code terminal.
</details>

<details>
<summary><strong><code>ModuleNotFoundError: No module named 'flask'</code></strong></summary>

Activate `.venv` and run:

```powershell
python -m pip install -r requirements.txt
```

Make sure VS Code is using the virtual environment created inside this project.
</details>

<details>
<summary><strong>The port is already in use</strong></summary>

Stop the other application using port `5000`, or change the port in the `app.run(...)` configuration in `app.py` and use the corresponding local URL.
</details>

<details>
<summary><strong>I need to reset the sample database</strong></summary>

Stop the application first. Then remove the generated SQLite database file inside `data/` and restart the app so it can recreate the synthetic dataset. Never delete the database while the app is using it.
</details>

## 🛣️ Possible Future Enhancements

- Adjustable filter size and hash count.
- Repeatable false-positive experiments with downloadable results.
- Side-by-side Bloom filter configuration comparisons.
- Exportable benchmark results for reports and presentations.

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**BloomCheck**  
*Bloom Filter Based Email Availability Checker and Visualizer*

Made as a Big Data Analytics mini-project.

</div>
