.PHONY: up down logs test dev

# Build and start the app at http://127.0.0.1:8000
up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

test:
	pytest

# Work on the code: backend with auto-reload on :8000, React dev server on
# :3000 (open that one; it proxies /api to the backend). Ctrl+C stops both.
dev:
	@trap 'kill 0' INT TERM; \
	python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000 & \
	(cd frontend && BROWSER=none npm start) & \
	wait
