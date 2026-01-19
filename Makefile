.PHONY: dev api frontend install

dev:
	@make -j2 api frontend

api:
	cd api && uv run src/main.py

frontend:
	cd frontend && npm run dev

install:
	cd api && uv sync
	cd frontend && npm install
