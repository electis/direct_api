lint:
	black . --skip-string-normalization
	mypy . --exclude docs
	flake8 .
	pylint *.py
