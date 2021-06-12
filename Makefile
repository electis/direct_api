lint:
	flake8 .
	pylint *
	mypy .
	black .
