.PHONY: test test-cov lint install

install:
	pip install -r backend/requirements.txt

test:
	cd backend && pytest -v

test-cov:
	cd backend && pytest --cov=app --cov-report=term-missing

lint:
	cd backend && flake8 --select=E,F --ignore=E501 app/
