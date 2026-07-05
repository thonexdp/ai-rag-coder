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
```

`ollama-init` will automatically pull `qwen2.5:7b` and `nomic-embed-text` on first startup.
This is a **one-time download (~5 GB total)** — models are cached in the `ollama_data` volume and won't re-download on subsequent starts.

To monitor the pull progress:

```bash
docker compose logs -f ollama-init
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

To pre-load the embedding model during backend startup instead of the first document upload, also set:

```env
PREWARM_EMBEDDING_MODEL=true
```

To choose the chat and embedding providers for RAG:

Local Ollama mode:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=qwen2.5:7b
EMBEDDING_PROVIDER=auto
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
```

OpenAI mode:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4.1-mini
EMBEDDING_PROVIDER=auto
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_TIMEOUT_SECONDS=60
```

Manual sentence-transformers fallback:

```env
EMBEDDING_PROVIDER=sentence_transformers
EMBEDDING_MODEL_NAME=BAAI/bge-m3
```

Provider behavior:

- `LLM_PROVIDER=openai` + `EMBEDDING_PROVIDER=auto` uses OpenAI for both answer generation and embeddings.
- `LLM_PROVIDER=ollama` + `EMBEDDING_PROVIDER=auto` uses Ollama for both answer generation and embeddings.
- `EMBEDDING_PROVIDER=sentence_transformers` is an explicit CPU-bound fallback mode.

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

If you enable OpenAI mode, make sure the updated backend dependencies are installed first:

```bash
pip install -r requirements.txt
```

## Document ingestion diagnostics

If an uploaded PDF stays on `processing`, follow the backend logs:

```bash
docker compose logs -f backend
```

Useful ingestion progress lines:

- `Document ingestion started`
- `Document text extracted`
- `Document chunking complete`
- `Document embedding/upsert starting`
- `Chroma upsert complete`
- `Document ingestion completed`

How to read them:

- If extraction and chunking are fast but `Chroma upsert complete` takes a long time, embedding on CPU is the bottleneck.
- If `Document ingestion failed` appears, the document should move to `failed` and the app will show the failure reason.
- If a tiny `.txt` becomes `ready` quickly but a PDF is much slower, the ingestion pipeline is healthy and the PDF workload is just heavier.
- The logs also show the active embedding provider, model, and Chroma collection name.

If you switch embedding provider or embedding model, delete old uploads and re-upload them. Existing document rows are not reindexed automatically into the new collection layout.

## Mobile setup

```bash
cd mobile
flutter pub get
flutter run --dart-define=API_BASE_URL=http://10.0.2.2:9000/api/v1
```

Defaults by platform:

- Android emulator: `http://10.0.2.2:9000/api/v1`
- Chrome/web on the same machine: `http://localhost:9000/api/v1`
- Desktop or iOS simulator on the same machine: `http://localhost:9000/api/v1`
- Physical Android device on the same LAN: `http://<your-pc-lan-ip>:9000/api/v1`

Examples:

```bash
flutter run -d chrome --dart-define=API_BASE_URL=http://localhost:9000/api/v1
flutter run -d emulator-5554 --dart-define=API_BASE_URL=http://10.0.2.2:9000/api/v1
flutter run --dart-define=API_BASE_URL=http://192.168.254.143:9000/api/v1
```

### Build an APK for a physical Android device

Use the current LAN IP address of the machine running the backend. For example:

```bash
flutter build apk --dart-define=API_BASE_URL=http://192.168.254.143:9000/api/v1
```

Important notes:

- The `API_BASE_URL` in the build command must exactly match your backend machine's current LAN IP.
- `localhost` and `10.0.2.2` will not work in an installed APK on a real phone.
- If your Wi-Fi, hotspot, or router changes, your PC IP can change too. Rebuild the APK with the new IP.
- Before testing login in the app, open `http://<your-pc-lan-ip>:9000/health` in the phone browser and confirm it returns `{"status":"ok"}`.

### Physical-device troubleshooting

If the APK shows `connection failed`, check these in order:

- The APK was built with the correct IP. Example mismatch: backend is at `192.168.254.143`, but the APK was built with `192.168.1.105`.
- The phone and the backend machine are on the same LAN or Wi-Fi network.
- The backend is reachable from the phone browser at `http://<your-pc-lan-ip>:9000/health`.
- The backend is listening on the LAN interface, not just `localhost`.
- Windows Firewall or another host firewall is not blocking inbound traffic on port `9000`.

CORS does not affect the installed Android APK path. It matters for web builds, not native app requests.

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

## Ollama models

| Model | Role | Size |
|---|---|---|
| `qwen2.5:7b` | Chat + RAG answering | ~4.7 GB |
| `nomic-embed-text` | Document embeddings | ~274 MB |

To list all locally available models:

```bash
docker exec school_ollama ollama list
```

To manually pull or remove a model:

```bash
docker exec school_ollama ollama pull qwen2.5-coder:7b
docker exec school_ollama ollama rm qwen2.5-coder:7b
```

## Notes

- The vector store is wrapped behind a service interface so `Qdrant` can replace `ChromaDB` later with minimal changes.
- The LLM access is isolated behind a provider-based service layer, which keeps Ollama/OpenAI swaps localized.
- Embeddings use a provider-based service layer as well, and Chroma collections are derived from embedding provider + model to avoid mixed-dimension vector bugs.
- `ollama-init` runs once on first `docker compose up` and exits — it does not consume resources after that.
- Background document ingestion uses FastAPI background tasks for MVP simplicity.
- If your `OPENAI_API_KEY` was shared during troubleshooting, rotate it before using the project again.
