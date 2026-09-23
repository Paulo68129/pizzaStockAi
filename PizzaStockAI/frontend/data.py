from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, select

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.database import DATABASE_URL
from backend.models import Ingredient, Pizza, RecipeItem, Sale
from frontend.clock import operational_today

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)


@st.cache_data(ttl=10, max_entries=8)
def load_data():
    with engine.connect() as connection:
        ingredients = pd.read_sql(select(Ingredient), connection)
        pizzas = pd.read_sql(select(Pizza), connection)
        recipes = pd.read_sql(select(RecipeItem), connection)
        sales = pd.read_sql(select(Sale), connection)
    return ingredients, pizzas, recipes, sales


def clear_data_cache() -> None:
    load_data.clear()


def money(value: float) -> str:
    return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def today_sales(sales: pd.DataFrame) -> pd.DataFrame:
    if sales.empty:
        return sales
    today = pd.Timestamp(operational_today())
    return sales[pd.to_datetime(sales["criada_em"]) >= today]


def sales_ranking(pizzas: pd.DataFrame, sales: pd.DataFrame) -> pd.DataFrame:
    if sales.empty or pizzas.empty:
        return pd.DataFrame(columns=["pizza", "quantidade", "faturamento", "custo", "lucro"])
    ranking = sales.merge(pizzas[["id", "nome"]], left_on="pizza_id", right_on="id")
    grouped = ranking.groupby("nome", as_index=False).agg(
        quantidade=("quantidade", "sum"),
        faturamento=("valor_total", "sum"),
        custo=("custo_total", "sum"),
    )
    grouped["lucro"] = grouped["faturamento"] - grouped["custo"]
    return grouped.rename(columns={"nome": "pizza"}).sort_values("quantidade", ascending=False)


def can_manage_stock(perfil: str) -> bool:
    return perfil in {"gerente", "administrador"}


def can_delete(perfil: str) -> bool:
    return perfil == "administrador"
