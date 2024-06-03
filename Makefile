.DEFAULT_GOAL := all

.PHONY: install
install:
	pip install -r requirements.txt

.PHONY: flask_app
flask_app:
	python flask_app.py

.PHONY: format
format:
	black .
	ruff check . --fix --exit-zero