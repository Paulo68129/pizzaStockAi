# PizzaStockAI

Sistema profissional de gestão para pizzarias: estoque, receitas, vendas, finanças, alertas e previsão de demanda com machine learning.

## Stack

- **Backend:** FastAPI + SQLAlchemy + JWT
- **Frontend:** Streamlit (multipage)
- **Dados:** SQLite (local) ou PostgreSQL (produção)
- **ML:** scikit-learn (regressão linear)
- **Gráficos:** Plotly
- **Ops:** Docker Compose

## Subir localmente (rápido)

```powershell
cd PizzaStockAI
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python seed.py
```

Terminal 1 — API:

```powershell
.\.venv\Scripts\python -m uvicorn backend.app:app --reload --port 8000
```

Terminal 2 — Dashboard:

```powershell
.\.venv\Scripts\python -m streamlit run frontend/dashboard.py
```

- API / docs: http://localhost:8000/docs
- Dashboard: http://localhost:8501

### Contas demo

| Perfil | E-mail | Senha |
|--------|--------|-------|
| Administrador | admin@pizzastock.local | 123456 |
| Gerente | gerente@pizzastock.local | 123456 |
| Atendente | atendente@pizzastock.local | 123456 |

## PostgreSQL (produção)

```powershell
$env:DATABASE_URL = "postgresql+psycopg2://user:senha@localhost:5432/pizzastock"
$env:PIZZASTOCK_SECRET_KEY = "chave-secreta-forte"
.\.venv\Scripts\python seed.py
.\.venv\Scripts\python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

## Docker

```powershell
docker compose up --build
```

- API: http://localhost:8000
- Frontend: http://localhost:8501
- Postgres: localhost:5432 (`pizzastock` / `pizzastock`)

## API REST

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/login` ou `/auth/login` | JWT |
| GET/POST/PUT/DELETE | `/ingredientes` | Estoque |
| GET/POST | `/pizzas` | Cardápio + receita |
| GET/POST | `/vendas` | Vendas (baixa estoque) |
| GET | `/analytics` | KPIs |
| GET | `/analytics/completo` | Painel completo |
| GET | `/alertas` ou `/analytics/alertas` | Alertas |
| GET | `/analytics/previsoes` | Previsão ML |
| GET | `/analytics/recomendacoes` | Compras sugeridas |
| GET | `/health` | Healthcheck |

Autenticação: header `Authorization: Bearer <token>`.

## Funcionalidades

1. Cadastro de ingredientes (mínimo, custo, validade)
2. Receitas por pizza com baixa automática no estoque
3. Registro de vendas com validação de saldo/validade
4. Dashboard em tempo real (faturamento, pedidos, lucro, críticos)
5. Financeiro (diário/semanal/mensal/anual, CMV, ticket médio)
6. Alertas (estoque, ruptura, validade, crescimento de vendas)
7. Previsão de demanda (LinearRegression) e recomendação de compras
8. Ranking de pizzas, horário de pico e meta diária
9. Perfis: administrador, gerente, atendente

## Estrutura

```
PizzaStockAI/
├── backend/          # FastAPI
├── frontend/         # Streamlit (dashboard.py + app_pages/)
├── ml/               # forecast + recommendation
├── database/         # SQLite local
├── tests/
├── seed.py
├── docker-compose.yml
└── requirements.txt
```

## Testes

```powershell
.\.venv\Scripts\python -m pytest -q
```
