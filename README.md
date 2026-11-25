# Basic-Dockerized-Pipeline-Tool

An interactive, cross-platform CLI **ETL (Extract, Transform, Load)** pipeline built in Python. It ingests `.csv` or `.parquet` datasets from a URL or local file path, audits and cleans the data interactively, dynamically spins up a containerized **PostgreSQL 17 + pgAdmin 4** stack using Docker Compose, and uploads the cleaned data in chunks with a live progress bar.

---

## Tools & Tech Stack

Every library and service in this project serves a specific role in the ETL workflow:

| Tool / Library | Category | What It Does in This Project |
| :--- | :--- | :--- |
| **Python 3.12+** | Language | Core programming language powering the pipeline and CLI. |
| **[`uv`](https://docs.astral.sh/uv/)** | Environment & Package Manager | Fast, isolated Python virtual environment and dependency manager. Reads `pyproject.toml` and `uv.lock` so the script runs cleanly without touching system Python. |
| **Click** | CLI Framework | Powers the interactive command-line prompts, input validation, defaults, password masking, and confirmation dialogs. |
| **Rich** | Terminal UI | Renders styled panels, status spinners, and formatted Data Quality summary tables in the terminal. |
| **Pandas** | Data Processing | Reads `.csv` and `.parquet` files into DataFrames, inspects nulls and duplicates, normalizes column names, and handles data cleaning. |
| **PyArrow** | Parquet Engine | Backend engine used by Pandas to read `.parquet` datasets efficiently. |
| **SQLAlchemy** | Database Toolkit / ORM | Manages the PostgreSQL connection pool and executes schema creation and chunked inserts via `.to_sql()`. |
| **psycopg2-binary** | PostgreSQL Driver | Low-level database adapter (`postgresql+psycopg2://`) used by SQLAlchemy to communicate with PostgreSQL. |
| **tqdm** | Progress Tracking | Displays a live terminal progress bar as 10,000-row batches are uploaded to the database. |
| **Docker & Docker Compose** | Containerization | Provisions isolated **PostgreSQL 17** and **pgAdmin 4** containers with persistent volumes and health checks. |
| **PostgreSQL 17** | Database | Destination relational database where the cleaned dataset is stored. |
| **pgAdmin 4** | Database GUI | Web-based interface (`http://localhost:8080`) for browsing schemas, viewing tables, and running SQL queries against your loaded data. |

---

## Project Structure

```text
Basic-Dockerized-Pipeline-Tool/
├── main.py                 # Entry point that launches the CLI
├── docker-compose.yaml     # Parameterized Postgres 17 + pgAdmin 4 stack
├── pyproject.toml          # Project metadata and dependency definitions
├── uv.lock                 # Locked dependency versions for reproducible runs
├── .gitignore              # Excludes .venv/, __pycache__/, and local artifacts
└── src/
    ├── cli.py              # Interactive CLI orchestration & Rich UI
    ├── extract.py          # Data ingestion from URL or local file path
    ├── transform.py        # Data quality inspection & cleaning logic
    ├── docker_manager.py   # Dynamic Docker Compose startup & health polling
    └── load.py             # Chunked SQLAlchemy ingestion into PostgreSQL
```

---

## How Everything Works (Under the Hood)

The pipeline runs in **four modular stages**, orchestrated by `src/cli.py`:

```text
[CSV / Parquet URL or Local File]
               │
               ▼
  1. EXTRACT (src/extract.py)
     • Detects file format (.csv or .parquet)
     • Loads dataset into a Pandas DataFrame
               │
               ▼
  2. TRANSFORM (src/transform.py)
     • Audits rows, columns, null cells, and duplicate rows
     • Displays Rich summary table in the terminal
     • Normalizes column names (lowercase + snake_case)
     • Applies user choices for nulls (keep / zero / custom) & duplicates
               │
               ▼
  3. INFRASTRUCTURE (src/docker_manager.py + docker-compose.yaml)
     • Injects user's DB username, password, DB name, and port as env vars
     • Runs `docker compose up -d` for pg-database & pgadmin
     • Polls `pg_isready` inside the container until PostgreSQL is healthy
               │
               ▼
  4. LOAD (src/load.py)
     • Connects via SQLAlchemy (`postgresql+psycopg2://`)
     • Creates/replaces table schema using `df.head(0).to_sql(...)`
     • Streams data in 10,000-row chunks with a `tqdm` progress bar
     • Disposes the connection pool cleanly
               │
               ▼
     [Ready to Query in pgAdmin 4]
```

### Module Breakdown

1. **`src/extract.py` — Data Extraction**
   * Accepts either a local file path or a remote HTTP/HTTPS URL.
   * Automatically routes `.csv` files through `pd.read_csv()` and `.parquet` files through `pd.read_parquet()`.

2. **`src/transform.py` — Inspection & Cleaning**
   * `inspect_dataset(df)`: Computes a dictionary of data quality metrics (`rows`, `columns`, `null_cells`, `duplicate_rows`) before any changes are made.
   * `clean_dataset(df, null_strategy, custom_fill, drop_duplicates)`: Works on a safe copy of the DataFrame, standardizes all column names to `lowercase_snake_case` for SQL compatibility, applies your chosen null strategy (`keep`, `zero`, or `custom`), and optionally drops exact duplicate rows.

3. **`src/docker_manager.py` & `docker-compose.yaml` — Dynamic Container Management**
   * `docker-compose.yaml` uses `${VARIABLE:-default}` environment variable substitution for `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, and `POSTGRES_PORT`.
   * `start_containers(...)`: Copies the current system environment, injects your custom CLI credentials and host port, and runs `docker compose up -d` without ever modifying the YAML file on disk.
   * `wait_for_postgres(...)`: Loops and runs `docker exec pg-database pg_isready` every 2 seconds until Postgres reports ready (or raises a `TimeoutError` after 30 seconds).

4. **`src/load.py` — Chunked Database Ingestion**
   * Builds a dynamic SQLAlchemy URL: `postgresql+psycopg2://{user}:{password}@localhost:{port}/{db_name}`.
   * Creates or replaces the target table schema first using `df.head(0).to_sql(..., if_exists="replace", index=False)`.
   * Slices the DataFrame into 10,000-row batches wrapped in `tqdm(...)` and appends each chunk to PostgreSQL, preventing memory spikes on large datasets.
   * Calls `engine.dispose()` at the end to close database connections cleanly.

---

## How to Run the Script Using `uv`

### Prerequisites

Make sure you have the following installed before starting:

1. **Docker & Docker Compose** (Docker Desktop on Windows/macOS, or Docker Engine + Compose plugin on Linux — make sure the Docker daemon is running).
2. **`uv`** (handles Python and all project dependencies automatically).

If you don't have `uv` installed yet:

* **Linux / macOS:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
* **Windows (PowerShell):**
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

### Step 1: Clone the Repository

```bash
git clone https://github.com/marwan-shiha/Basic-Dockerized-Pipeline-Tool.git
cd Basic-Dockerized-Pipeline-Tool
```

### Step 2: Sync Dependencies with `uv`

This creates an isolated `.venv/` folder inside the project and installs the exact locked versions from `uv.lock`:

```bash
uv sync
```

### Step 3: Run the Pipeline

Always launch the script through `uv run` so it executes inside the isolated virtual environment (avoiding OS-level `externally-managed-environment` errors on Linux):

```bash
uv run python main.py
```

---

## Interactive CLI Walkthrough

Once you run `uv run python main.py`, follow the prompts:

1. **Source & Table Name:** Enter a direct URL or local file path (`.csv` or `.parquet`), and specify the target PostgreSQL table name (default: `cleaned_data`).
2. **Review & Clean:** Inspect the Rich **Dataset Preview & Issues Found** table, choose how to handle empty cells (`keep`, `zero`, or `custom`), and choose whether to drop exact duplicate rows.
3. **PostgreSQL Configuration:** Enter your preferred database settings or press `Enter` to use the defaults:
   * **Username:** `admin`
   * **Password:** `0000`
   * **Database Name:** `dockerized_pipeline_database`
   * **Host Port:** `5432` *(if port `5432` is already in use on your machine, enter another port such as `5433`)*
4. **Watch It Run:** Docker Compose launches PostgreSQL + pgAdmin, waits for the health check, and streams your dataset into the table with a `tqdm` progress bar.

### Sample Datasets to Test

* **CSV Test (891 rows — includes nulls and duplicate rows):**
  ```text
  https://raw.githubusercontent.com/mwaskom/seaborn-data/master/titanic.csv
  ```
* **Parquet Test (~56,000 rows — great for testing chunked uploads):**
  ```text
  https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2024-01.parquet
  ```

---

## Exploring Your Data in pgAdmin 4

After the pipeline completes:

1. Open **[http://localhost:8080](http://localhost:8080)** in your browser.
2. Sign in to pgAdmin:
   * **Email:** `admin@admin.com`
   * **Password:** `0000`
3. Right-click **Servers** → **Register** → **Server...** and configure the **Connection** tab:
   * **Host name/address:** `pg-database` *(use the Docker service name, **not** `localhost`, because pgAdmin runs inside its own container)*
   * **Port:** `5432` *(always use the internal container port `5432`, even if you mapped a different host port like `5433`)*
   * **Maintenance database:** The database name you entered (default: `dockerized_pipeline_database`)
   * **Username & Password:** The credentials you entered in the CLI

---

## Useful Docker Commands & Troubleshooting

| Task / Issue | Command / Solution |
| :--- | :--- |
| **Stop containers (keep saved data)** | `docker compose down` |
| **Reset database & change credentials** | `docker compose down -v` *(PostgreSQL only initializes `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_DB` the first time the `pg_data` volume is created. Wiping the volume with `-v` lets you start fresh with new credentials.)* |
| **Error: `port 5432: address already in use`** | Re-run `uv run python main.py` and enter an available host port like `5433` when prompted, or stop your local PostgreSQL service (`sudo systemctl stop postgresql`). |
| **Check running containers & ports** | `docker ps` |
| **View PostgreSQL logs** | `docker logs pg-database --tail 30` |

---

## License

This project is open source and available under the [MIT License](LICENSE).
