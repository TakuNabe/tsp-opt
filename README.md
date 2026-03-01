# tsp-opt

Prototype of an optimization SDK for the Traveling Salesman Problem (TSP).

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
# Install dependencies
uv sync
```

## Running the app

```bash
# Start the Streamlit web UI
uv run streamlit run src/controller/app.py
```

The app will open in your browser at `http://localhost:8501`.

## Running tests

```bash
# Run all tests
uv run pytest -v

# Run unit tests only
uv run pytest tests/unit_test -v

# Run integration tests only
uv run pytest tests/integration_test -v
```

## Linting

```bash
uv run ruff check .
uv run ruff format .
```
