from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.analytics import peak_hours, pizza_ranking
from backend.database import SessionLocal
from frontend.data import load_data, money, sales_ranking, today_sales

st.title("Métricas", icon=":material/monitoring:")
st.caption("Ranking, horário de pico, meta e desempenho do mix.")

ingredients, pizzas, recipes, sales = load_data()
today = today_sales(sales)
revenue = float(today["valor_total"].sum()) if not today.empty else 0.0
target = float(st.session_state.get("daily_target", 2000.0))
percent = min(100.0, revenue / target * 100) if target else 0.0

with SessionLocal() as db:
    ranking = pizza_ranking(db)
    pico = peak_hours(db)

with st.container(horizontal=True):
    st.metric("Meta diária", money(target), border=True)
    st.metric("Atual", money(revenue), f"{percent:.0f}%", border=True)
    st.metric("Horário de pico", pico.get("rotulo", "—"), border=True)

left, right = st.columns(2, gap="large")
with left, st.container(border=True):
    st.subheader("Ranking de pizzas", icon=":material/emoji_events:")
    if not ranking:
        st.info("Sem vendas suficientes.")
    else:
        for item in ranking:
            st.markdown(
                f"**{item['posicao']}º {item['pizza']}** — "
                f"{item['quantidade']} un · {money(item['faturamento'])} · lucro {money(item['lucro'])}"
            )

with right, st.container(border=True):
    st.subheader("Distribuição por horário", icon=":material/schedule:")
    dist = pico.get("distribuicao") or []
    if not dist:
        st.caption("Sem dados de horário.")
    else:
        df = pd.DataFrame(dist)
        fig = px.bar(df, x="hora", y="pedidos", labels={"pedidos": "Pedidos", "hora": "Hora"})
        fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

with st.container(border=True):
    st.subheader("Tabela de desempenho", icon=":material/table_chart:")
    table = sales_ranking(pizzas, sales)
    if table.empty:
        st.caption("Sem dados.")
    else:
        st.dataframe(
            table,
            width="stretch",
            hide_index=True,
            column_config={
                "faturamento": st.column_config.NumberColumn(format="R$ %.2f"),
                "custo": st.column_config.NumberColumn(format="R$ %.2f"),
                "lucro": st.column_config.NumberColumn(format="R$ %.2f"),
            },
        )
