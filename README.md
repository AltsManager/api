# 🚀 FastAPI - Getting Started Guide

This is a new starter project, the beginning of the FastAPI core for AltsManager, based on a stadand FastAPI deployment from the Medium article:
**“Getting Started with FastAPI: A Step-by-Step Beginner’s Guide”**

📖 Check the full article: [Getting Started with FastAPI: A Step-by-Step Beginner’s Guide](https://medium.com/@inandelibas/getting-started-with-fastapi-a-step-by-step-beginners-guide-c2c5b35014e9)

## 💡 Features Covered

- FastAPI installation and setup
- First route example with `@app.get("/")`
- Path & Query Parameters
- Request Body with Pydantic Models
- Response handling & status codes
- Async endpoints & concurrency
- Automatic API docs with Swagger UI
- Project structure for growing apps
- Router usage with `include_router()`

## ▶️ How to Run

```bash
git clone https://github.com/AltsManager/api.git
cd api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload
```

## Development

```bash
ruff check .      # lint
pytest            # run tests
```

Visit:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## 📂 Project Structure

See `app/` folder for full implementation.
