# UCL — Universal Code Language (MVP)

A standalone, AI-assisted project conversion web app. This MVP prioritizes conversion **to UiPath** while exposing Python and Blue Prism source/target choices so the architecture can grow into all six conversion directions.

## What is included

- FastAPI backend and responsive browser UI
- Single-file and ZIP project uploads
- Source selection or automatic detection for Python, UiPath, and Blue Prism
- UiPath Studio target selection: 24.x, 25.x, 26.x
- Configurable provider settings for Google Gemini, OpenAI API, Anthropic Claude, OpenRouter, Azure OpenAI, Ollama, and custom OpenAI-compatible APIs
- Encrypted-at-rest provider API key storage (Fernet)
- Admin login, recent conversion history, downloadable ZIP output
- Prompted semantic migration with a report, static XML/XAML/JSON/Python checks, and warnings
- ZIP path traversal protections and upload size limits

## Important prototype limitations

1. A conversion response is LLM-generated. Static validation is not a guarantee that the project will run or preserve every behavior. UiPath Studio/runtime execution tests are not performed by this web app.
2. The model receives source files as text, up to the configured source-character limit. Binary assets, very large files, and skipped directories are not included. Large projects may need project chunking and multi-pass orchestration in a later release.
3. Blue Prism exports differ by version and export type. A `.bpprocess` file can be analyzed if it is readable XML, but native importable Blue Prism release packaging is not guaranteed.
4. The Blue Prism target is experimental; its report must state when manual reconstruction is needed. UiPath is the main target.
5. This MVP makes one model call per project. Production-grade conversion should add a separate analysis pass, intermediate representation, per-workflow generation, dependency-aware ordering, retry/repair loops, and automated Studio tests.
6. Some provider models/API features vary. Use a model that supports the configured API endpoint and sufficient context/output limits.

## Requirements

- Python 3.11+ recommended
- A provider API key, or a locally running Ollama OpenAI-compatible endpoint
- Internet access from the server for hosted LLM providers

## Run locally on Windows

1. Install Python 3.11 or newer.
2. Extract the ZIP and open a terminal in the `ucl_converter` folder.
3. Create a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env`.
5. Generate a Fernet encryption key:

   ```powershell
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```

6. Set `UCL_ENCRYPTION_KEY` to that key, change `UCL_ADMIN_PASSWORD` to a strong password, and set a private `UCL_SESSION_SECRET` in `.env`.
7. Start the server:

   ```powershell
   uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

8. Open `http://127.0.0.1:8000` and configure the LLM at `/admin`.

For local-only testing, the default username is `admin`, but you must change the password placeholder in `.env` before admin login is allowed.

## Provider setup

- **Gemini:** API key; default model `gemini-2.5-flash`.
- **OpenAI API:** API key; default model `gpt-4.1`. This is an API key, not a ChatGPT subscription password.
- **Anthropic:** API key; default model `claude-sonnet-4-20250514`.
- **OpenRouter:** API key; model identifier supported by OpenRouter.
- **Azure OpenAI:** resource endpoint in Base URL, deployment name in Model, API key, and API version.
- **Ollama:** local endpoint and model; API key is usually optional.
- **Custom OpenAI-compatible:** endpoint base URL, model and provider API key.

## Deployment and security checklist

Before exposing this to the public internet:

- Use HTTPS and set `UCL_SESSION_HTTPS_ONLY=true`.
- Use a strong random `UCL_ADMIN_PASSWORD` and `UCL_SESSION_SECRET`.
- Keep `.env`, `data/ucl.sqlite3`, outputs, and backups outside public/static directories.
- Add rate limiting, per-user auth, quotas, file retention/deletion, CSRF protection, malware scanning, and isolated job workers.
- Decide a privacy/retention policy and disclose that source code is sent to the configured LLM provider.
- Do not put real business credentials or production secrets in source projects.
- Test output in the actual target Studio version and runtime before production.

## Structure

```text
ucl_converter/
  app/main.py          FastAPI routes, upload handling, conversion orchestration
  app/providers.py     LLM provider adapters
  app/security.py      API key encryption
  app/db.py            SQLite settings/history
  static/index.html    Converter UI
  static/admin.html    Admin UI
  static/style.css     UI styles
  static/app.js        Converter interactions
  static/admin.js      Provider settings interactions
  requirements.txt
  .env.example
```
