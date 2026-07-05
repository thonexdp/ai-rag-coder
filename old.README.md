# AI School Assistant

Local-first school assistant built with `FastAPI`, `SQLAlchemy`, `PostgreSQL/SQLite`, `Ollama`, `ChromaDB`, and `Flutter`.

## What is included

- JWT auth with `student`, `faculty`, and `admin` roles
- Admin-only document upload for `PDF`, `DOCX`, and `TXT`
- Local RAG chat flow with citations and chat history
- SQL-backed student schedule retrieval
- Seeded announcements and demo users
- Flutter mobile shell with Riverpod MVVM, chat, schedule, document management, and voice hooks

## Services

| Service | Purpose | Port |
|---|---|---|
| backend | FastAPI REST API | 9000 |
| postgres | Relational data | 5432 |
| ollama | Local LLM runtime | 11434 |
| chromadb | Vector storage | 9001 |

## Backend setup

```bash
cd ai_school_assistant
docker compose build
docker compose up -d
docker exec -it school_ollama ollama pull qwen2.5:7b
docker exec -it school_ollama ollama pull nomic-embed-text
```

Health check:

```bash
curl http://localhost:9000/health
```

If `curl` returns `Empty reply from server`, the backend container usually started but the FastAPI app inside it crashed or is still restarting. Check:

```bash
docker compose ps
docker compose logs backend
```

If you changed `backend/requirements.txt` or the `Dockerfile`, rebuild the backend image before starting again:

```bash
docker compose down
docker compose build --no-cache backend
docker compose up -d
```

## Local backend development

```bash
cd backend
pip install -r requirements.txt
```

For SQLite-based local development, set this in `backend/.env`:

```env
USE_SQLITE_FOR_DEV=true
SQLITE_DATABASE_URL=sqlite:///./school_assistant.db
```

Run the API:

```bash
uvicorn app.main:app --reload --port 9000
```

Run migrations:

```bash
alembic upgrade head
```

Run tests:

```bash
pytest
```

## Mobile setup

```bash
cd mobile
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:9000/api/v1
```

Use `http://localhost:9000/api/v1` instead when targeting desktop or an iOS simulator on the same machine.

## Seeded accounts

- Admin: `admin@school.local` / `Admin123!`
- Student: `student@school.local` / `Student123!`

## Key API endpoints

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/chat`
- `GET /api/v1/chat/history`
- `POST /api/v1/documents`
- `GET /api/v1/documents`
- `GET /api/v1/students/me/schedule`
- `GET /api/v1/announcements`

## Notes

- The vector store is wrapped behind a service interface so `Qdrant` can replace `ChromaDB` later.
- The LLM access is isolated in `OllamaLLMService`, which keeps model swaps localized.
- `nomic-embed-text` is now pulled in Docker setup so you have a local embedding model available alongside `qwen2.5:7b`.
- Background document ingestion uses FastAPI background tasks for MVP simplicity.
