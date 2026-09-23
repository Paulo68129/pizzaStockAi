from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st
from sqlalchemy import select

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.auth import verify_password
from backend.database import SessionLocal
from backend.models import User
from frontend.clock import ensure_clock_state, render_clock_sidebar
from seed import seed

st.set_page_config(
    page_title="PizzaStockAI",
    page_icon=":material/local_pizza:",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def bootstrap():
    seed(include_history=True)


bootstrap()

if "daily_target" not in st.session_state:
    st.session_state.daily_target = 2000.0
ensure_clock_state()


def render_login() -> None:
    left, center, right = st.columns([1, 1.2, 1])
    with center:
        st.markdown("# PizzaStockAI")
        st.caption("Estoque, vendas e inteligência operacional para pizzarias.")
        with st.form("login_form"):
            email = st.text_input("E-mail", value="admin@pizzastock.local")
            password = st.text_input("Senha", type="password", value="123456")
            submitted = st.form_submit_button("Entrar", type="primary", width="stretch")
        if submitted:
            with SessionLocal() as db:
                user = db.scalar(select(User).where(User.email == email.lower().strip()))
                if user and user.ativo and verify_password(password, user.senha_hash):
                    st.session_state.user = {
                        "id": user.id,
                        "nome": user.nome,
                        "email": user.email,
                        "perfil": user.perfil,
                    }
                    st.rerun()
                st.error("E-mail ou senha inválidos")
        with st.expander("Contas de demonstração"):
            st.markdown(
                "- **admin@pizzastock.local** / 123456 — administrador\n"
                "- **gerente@pizzastock.local** / 123456 — gerente\n"
                "- **atendente@pizzastock.local** / 123456 — atendente"
            )


if "user" not in st.session_state:
    render_login()
    st.stop()

pages = {
    "Operação": [
        st.Page("app_pages/home.py", title="Central", icon=":material/dashboard:"),
        st.Page("app_pages/vendas.py", title="Vendas", icon=":material/point_of_sale:"),
        st.Page("app_pages/estoque.py", title="Estoque", icon=":material/inventory_2:"),
    ],
    "Análises": [
        st.Page("app_pages/financeiro.py", title="Financeiro", icon=":material/payments:"),
        st.Page("app_pages/metricas.py", title="Métricas", icon=":material/monitoring:"),
        st.Page("app_pages/previsoes.py", title="Previsões", icon=":material/psychology:"),
    ],
}

with st.sidebar:
    st.markdown(f"**{st.session_state.user['nome']}**")
    st.caption(st.session_state.user["perfil"].capitalize())
    st.divider()
    render_clock_sidebar()
    st.divider()
    if st.button("Sair", icon=":material/logout:", width="stretch"):
        del st.session_state.user
        st.rerun()

page = st.navigation(pages, position="sidebar")
page.run()
