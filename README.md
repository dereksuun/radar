# Job Radar - Passo 1

Base inicial pronta com:

- FastAPI no ar
- Conexão com PostgreSQL
- Estrutura mínima organizada
- Endpoint `/health` com teste real no banco

## Estrutura

```text
job-radar/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── health.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   └── main.py
├── .env.example
├── docker-compose.yml
└── requirements.txt
```

## Rodar

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d
uvicorn app.main:app --reload
```

## Endpoints

- `GET /`
- `GET /health`
- `GET /docs`

## Se der erro de conexão com o banco

### 1) Banco não subiu

```bash
docker compose ps
```

### 2) Porta 5432 ocupada

```bash
sudo lsof -i :5432
```

### 3) `.env` incorreto

Confira se está assim:

```env
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=job_radar
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
```
