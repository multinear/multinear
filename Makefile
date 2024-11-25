.PHONY: all
all:
	@echo "Nothing to do by default"

python_cmd = cd multinear && uv run

# Install required packages
# run `uv sync --python 3.x` to install a specific Python version
.PHONY: install
install:
	@echo "Installing Python packages"
	uv sync
	@echo "Installing Node packages"
	cd multinear/frontend && npm install

# Run web server
.PHONY: web
web:
	$(python_cmd) uvicorn main:app

# Run web server in development mode
.PHONY: web_dev
web_dev:
	$(python_cmd) uvicorn main:app --reload

# Build frontend
.PHONY: frontend_build
frontend_build:
	cd multinear/frontend && npm run build

# Run frontend in development mode
.PHONY: frontend_dev
frontend_dev:
	cd multinear/frontend && npm run dev
