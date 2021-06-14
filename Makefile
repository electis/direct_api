lint:
	black . --skip-string-normalization
	mypy .
	flake8 .
	pylint *.py
