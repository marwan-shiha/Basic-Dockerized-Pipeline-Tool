## Tool-Set & Tech Stack

- **Python 3** — Core programming language for the modular ETL pipeline.
- **uv** — Fast Python package and virtual environment manager (`pyproject.toml` & `uv.lock`).
- **Click** — Powers the interactive command-line interface, prompts, and user input validation.
- **Rich** — Renders styled terminal panels, status spinners, and data-quality summary tables.
- **Pandas** — Handles dataset extraction (`.csv` and `.parquet`), null-value imputation, deduplication, and column normalization.
- **SQLAlchemy** — Manages the PostgreSQL database engine and chunked DataFrame ingestion (`to_sql`).
- **psycopg2-binary** — PostgreSQL database adapter used by SQLAlchemy (`postgresql+psycopg2://`).
- **tqdm** — Displays a real-time progress bar during chunked database uploads.
- **Docker & Docker Compose** — Containerizes and orchestrates the database and admin services with dynamic environment variables and health checks.
- **PostgreSQL 17** — Target relational database for storing the cleaned datasets.
- **pgAdmin 4** — Web-based GUI for inspecting and querying the loaded PostgreSQL tables.
