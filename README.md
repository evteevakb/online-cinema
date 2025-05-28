Ссылка на репозиторий:
https://github.com/wegas66/Auth_sprint_1

# Online Cinema

This is a repository for the online cinema platform.

## Repository Structure

The repository is organized as follows:

```python
├── backup  # backup files
│ ├── admin  # DB dumps
│ └── elastic  # Elasticsearch dumps
│
├── deploy
│ ├── init  # shared infrastructure configs and entrypoints
│ └── admin, api, auth, etl, events_api, events_etl  # service deployment files
│
├── docs  # documentation-related files
│ └── diagrams  # diagrams used for documentation
│   ├── out  # diagrams in PNG format (rendered output)
│   └── src  # diagrams in PlantUML format (source files)
│
├── services  # core backend services
│ ├── admin  # admin panel
│ ├── api  # API gateway 
│ ├── auth  # authentication and authorization service
│ ├── etl  # ETL pipeline from PostgreSQL to Elasticsearch
│ ├── events_api  # service for collecting user events
│ └── events_etl  # ETL pipeline from Kafka to ClickHouse
│
├── .gitignore
├── pyproject.toml  # shared dev tools configuration (linters, type checkers)
└── README.md
```

## Running Services for the Current Sprint

To run the services for the current sprint, follow the instructions  in sections "Setting up environment variables" and "Running" in the [`deploy/auth/README.md`](./deploy/auth/README.md)

## Development Setup

Use [`uv`](https://github.com/astral-sh/uv) for dependency and virtual environment management.

**Create and activate a virtual environment:**

```bash
uv venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
```

**Install development tools:**

```bash
uv sync --group lint
```

**Sort imports:**

```bash
uv run isort .
```

**Format code:**

```bash
uv run ruff format .
```

**Check typing:**

```bash
uv run mypy .
```
