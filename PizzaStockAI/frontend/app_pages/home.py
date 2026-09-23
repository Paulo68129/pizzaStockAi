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
from backend.database import SessionLocal
from frontend.clock import operational_now
from frontend.data import clear_data_cache, load_data, money, sales_ranking, today_sales

op_now = operational_now()
st.title("Central de operações", icon=":material/dashboard:")
st.caption(f"Visão em tempo real · {op_now.strftime('%d/%m/%Y %H:%M')} (Brasília)")

ingredients, pizzas, recipes, sales = load_data()
today = today_sales(sales)
revenue = float(today["valor_total"].sum()) if not today.empty else 0.0
cost = float(today["custo_total"].sum()) if not today.empty else 0.0
orders = int(today["quantidade"].sum()) if not today.empty else 0
critical = int((ingredients["estoque"] <= ingredients["estoque_minimo"]).sum()) if not ingredients.empty else 0
target = float(st.session_state.get("daily_target", 2000.0))
percent = min(100.0, revenue / target * 100) if target else 0.0

with st.container(horizontal=True):
    st.metric("Faturamento hoje", money(revenue), f"meta {percent:.0f}%", border=True)
    st.metric("Pedidos", str(orders), money(revenue / orders) if orders else "sem ticket", border=True)
    st.metric("Lucro", money(revenue - cost), f"CMV {cost / revenue * 100:.1f}%" if revenue else "—", border=True)
    st.metric("Ingredientes críticos", str(critical), border=True)

left, right = st.columns([1.6, 1], gap="large")
with left, st.container(border=True):
    st.subheader("Faturamento recente", icon=":material/show_chart:")
    if sales.empty:
        st.info("Registre vendas para ver o ritmo do caixa.")
    else:
        chart = sales.copy()
        chart["data"] = pd.to_datetime(chart["criada_em"]).dt.date
        daily = chart.groupby("data", as_index=False)["valor_total"].sum()
        fig = px.line(daily, x="data", y="valor_total", markers=True, labels={"valor_total": "Valor", "data": "Data"})
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

with right, st.container(border=True):
    st.subheader("Meta diária", icon=":material/flag:")
    st.progress(percent / 100, text=f"{money(revenue)} de {money(target)}")
    new_target = st.number_input("Definir meta", min_value=0.0, value=target, step=100.0)
    if new_target != target:
        st.session_state.daily_target = new_target
        st.rerun()

col_a, col_b = st.columns(2, gap="large")
with col_a, st.container(border=True):
    st.subheader("Ranking de pizzas", icon=":material/leaderboard:")
    ranking = sales_ranking(pizzas, sales).head(5)
    if ranking.empty:
        st.caption("Sem vendas ainda.")
    else:
        for idx, row in enumerate(ranking.itertuples(), start=1):
            st.markdown(f"**{idx}º {row.pizza}** — {int(row.quantidade)} un · {money(row.faturamento)}")

with col_b, st.container(border=True):
    st.subheader("Alertas", icon=":material/notifications_active:")
    with SessionLocal() as db:
        alerts = build_alerts(db)
    if not alerts:
        st.success("Nenhum alerta no momento.", icon=":material/check_circle:")
    else:
        for alert in alerts[:8]:
            icon = ":material/error:" if alert["severidade"] == "critico" else ":material/warning:"
            st.markdown(f"{icon} {alert['mensagem']}")

st.caption(f"Relógio operacional {op_now.strftime('%H:%M')} · cache de dados ~10s")
if st.button("Atualizar agora", icon=":material/refresh:"):
    clear_data_cache()
    st.rerun()
