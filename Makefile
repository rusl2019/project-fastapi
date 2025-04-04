clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "users.db" -exec rm -rf {} +

format:
	@fd -e py -x black --line-length 79 --target-version py39 --exclude __pycache__ --exclude .venv