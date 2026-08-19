# GamerZone Backend

FastAPI backend for the GamerZone community website.

## Local setup

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Run the dev server

```bash
uvicorn app.main:app --reload
```

- App: http://127.0.0.1:8000
- Interactive docs (Swagger UI): http://127.0.0.1:8000/docs
- Alternative docs (ReDoc): http://127.0.0.1:8000/redoc

## Project structure

```
app/
├── main.py            # FastAPI app instance, mounts routers
├── core/
│   └── config.py      # centralized settings (env-var driven)
└── api/
    └── v1/
        └── router.py  # versioned API routes
```
