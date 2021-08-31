pre-commit:
	isort .
	black .
	mypy .
	brownie test --coverage