# TM-proxy
Proxy website adds trademark char every word with length is 6

## Requirements:

- python3.9+
- beautifulsoup4
- httpx
- fastapi
- uvicorn

more dependencies in file `requirements.txt` or `pyproject.toml`

## Local run for develop

1. Clone repository
```
git clone https://github.com/mitrofun/tm-proxy.git
```
2. Create virtual environment
```
cd tm-proxy
virtualenv .venv
source .venv/bin/activate
```
3. Install dependencies
```
pip install poetry && poetry install
```
4. For override settings create custom configuration *Optional
```
cp example.env config.env
```
5. Run develop server
```
uvicorn main:app --reload
```

## Testing

1. Run linter
```
flake8 . && mypy .
```
2. Run test
```
pytest
```

## Run in docker
```
docker build -t tm-proxy . && docker run -ti -p 8000:8000 tm-proxy
```
