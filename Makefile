.DEFAULT_GOAL := all

.PHONY: install
install:
	pip install -r requirements.txt

.PHONY: run_app
run_app:
	python main.py

.PHONY: format
format:
	black .
	ruff check . --fix --exit-zero
