from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.analytics import financial_summary
from backend.database import SessionLocal
from frontend.data import load_data, money

st.title("Financeiro", icon=":material/payments:")
st.caption("Faturamento, CMV e ticket médio por período.")

ingredients, pizzas, recipes, sales = load_data()

with SessionLocal() as db:
    financeiro = financial_summary(db)

cols = st.columns(4)
labels = [("Diário", "diario"), ("Semanal", "semanal"), ("Mensal", "mensal"), ("Anual", "anual")]
for col, (label, key) in zip(cols, labels):
    data = financeiro[key]
    with col:
        st.metric(f"Faturamento {label.lower()}", money(data["faturamento"]), border=True)
        st.caption(f"Lucro {money(data['lucro'])} · CMV {data['cmv_percentual']:.1f}%")

mensal = financeiro["mensal"]
with st.container(horizontal=True):
    st.metric("Ticket médio (mês)", money(mensal["ticket_medio"]), border=True)
    st.metric("CMV (mês)", f"{mensal['cmv_percentual']:.1f}%", border=True)
    st.metric("Pedidos (mês)", str(mensal["pedidos"]), border=True)
    st.metric("Quantidade vendida", str(mensal["quantidade"]), border=True)

left, right = st.columns([1.6, 1], gap="large")
with left, st.container(border=True):
    st.subheader("Evolução diária", icon=":material/ssid_chart:")
    if sales.empty:
        st.info("Sem dados de venda.")
    else:
        chart = sales.copy()
        chart["data"] = pd.to_datetime(chart["criada_em"]).dt.date
        daily = chart.groupby("data", as_index=False).agg(valor=("valor_total", "sum"), custo=("custo_total", "sum"))
        fig = px.line(daily, x="data", y="valor", markers=True, labels={"valor": "Faturamento", "data": "Data"})
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

with right, st.container(border=True):
    st.subheader("Composição do mês", icon=":material/pie_chart:")
    if mensal["faturamento"] <= 0:
        st.caption("Sem faturamento no mês.")
    else:
        df = pd.DataFrame(
            {
                "parte": ["Custo (CMV)", "Lucro"],
                "valor": [mensal["custo"], mensal["lucro"]],
            }
        )
        fig = px.pie(df, names="parte", values="valor", hole=0.45)
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
