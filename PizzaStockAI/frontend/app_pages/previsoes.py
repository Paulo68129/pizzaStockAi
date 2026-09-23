from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.alerts import build_alerts
from backend.analytics import buy_recommendations, demand_forecast
from backend.database import SessionLocal
from frontend.data import load_data, money

st.title("Previsões e inteligência", icon=":material/psychology:")
st.caption("Previsão de demanda com regressão linear, alertas e recomendações de compra.")

ingredients, pizzas, recipes, sales = load_data()

with SessionLocal() as db:
    forecast = demand_forecast(db, days=7)
    recommendations = buy_recommendations(db, horizon_days=7)
    alerts = build_alerts(db)

with st.container(horizontal=True):
    st.metric("Dias previstos", "7", border=True)
    st.metric("Itens a comprar", str(len(recommendations)), border=True)
    st.metric("Alertas ativos", str(len(alerts)), border=True)

left, right = st.columns([1.5, 1], gap="large")
with left, st.container(border=True):
    st.subheader("Demanda prevista (faturamento)", icon=":material/timeline:")
    hist = pd.DataFrame(forecast["historico"])
    prev = pd.DataFrame(forecast["previsao"])
    if hist.empty and prev.empty:
        st.info("Registre mais vendas para treinar o modelo.")
    else:
        hist["tipo"] = "Histórico"
        prev["tipo"] = "Previsão"
        combined = pd.concat([hist, prev], ignore_index=True)
        fig = px.line(
            combined,
            x="data",
            y="valor",
            color="tipo",
            markers=True,
            labels={"valor": "Faturamento", "data": "Data"},
        )
        fig.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.caption("Modelo: LinearRegression (scikit-learn) sobre o histórico diário.")

with right, st.container(border=True):
    st.subheader("Alertas", icon=":material/warning:")
    if not alerts:
        st.success("Operação estável.")
    else:
        for alert in alerts:
            st.markdown(f"- {alert['mensagem']}")

with st.container(border=True):
    st.subheader("Recomendação de compras (7 dias)", icon=":material/shopping_cart:")
    if not recommendations:
        st.success("Estoque suficiente para a demanda prevista.")
    else:
        for item in recommendations:
            st.markdown(
                f"**{item['ingrediente']}:** comprar {item['quantidade']:.1f} {item.get('unidade', 'kg')} "
                f"(custo estimado {money(item.get('custo_estimado', 0))})"
            )
        df = pd.DataFrame(recommendations)
        st.dataframe(df, width="stretch", hide_index=True)
