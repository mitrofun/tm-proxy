# target: run - Run server
run:
	echo "Run develop server"
	uvicorn main:app --reload

# target: lint - Run linters flake8 and mypy
lint:
	flake8 . --count
	mypy main.py

# target: qa - Run test
qa:
	py.test

# target: clean - Delete cache folders
clean:
	@rm -rf .benchmarks .coverage coverage.xml htmlcov report.xml .tox
	@find . -type d -name '.mypy_cache' -exec rm -rf {} +
	@find . -type d -name '__pycache__' -exec rm -rf {} +
	@find . -type d -name '*pytest_cache*' -exec rm -rf {} +
	@find . -type f -name "*.py[co]" -exec rm -rf {} +

# target: poetry-export - Export dependencies to requirements.txt file for installation with pip
poetry-export:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

# target: docker - Run in docker
docker:
	docker build -t tm-proxy . && docker run -ti -p 8000:8000 tm-proxy
