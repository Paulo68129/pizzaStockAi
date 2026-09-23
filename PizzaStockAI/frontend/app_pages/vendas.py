from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st
from sqlalchemy import select
from sqlalchemy.orm import joinedload

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.database import SessionLocal
from backend.models import Pizza, RecipeItem
from backend.services.sales import SaleRuleError, register_sale
from frontend.clock import format_brt, operational_now
from frontend.data import can_manage_stock, clear_data_cache, load_data, money

st.title("Vendas e cardápio", icon=":material/point_of_sale:")
st.caption("Registre pedidos e cadastre pizzas com receita. O estoque é atualizado automaticamente.")

ingredients, pizzas, recipes, sales = load_data()
perfil = st.session_state.user["perfil"]
last_added = st.session_state.pop("last_pizza_added", None)
last_sale_msg = st.session_state.pop("last_sale_msg", None)

if last_sale_msg:
    st.success(last_sale_msg, icon=":material/check_circle:")

tab_venda, tab_cardapio, tab_historico = st.tabs(["Registrar venda", "Cardápio e receitas", "Histórico"])

with tab_venda:
    if pizzas.empty:
        st.warning("Cadastre uma pizza antes de vender.")
    else:
        options = dict(zip(pizzas["nome"], pizzas["id"]))
        left, right = st.columns([1, 1.2], gap="large")
        with left, st.container(border=True):
            st.subheader("Novo pedido")
            sale_clock = operational_now().replace(second=0, microsecond=0)
            st.caption(f"Horário da venda: **{format_brt(sale_clock)}** (Brasília)")
            with st.form("form_venda"):
                pizza_name = st.selectbox("Pizza", list(options))
                quantity = st.number_input("Quantidade", min_value=1, value=1, step=1)
                submitted = st.form_submit_button("Confirmar venda", type="primary", width="stretch")
            pizza_row = pizzas[pizzas["id"] == options[pizza_name]].iloc[0]
            st.metric("Total do pedido", money(float(pizza_row["preco"]) * quantity))
            if submitted:
                sale_at = operational_now().replace(second=0, microsecond=0)
                with SessionLocal() as db:
                    try:
                        sale = register_sale(db, int(options[pizza_name]), int(quantity))
                        # sincroniza explicitamente com o relógio de Brasília da sidebar
                        sale.criada_em = sale_at
                        db.add(sale)
                        db.commit()
                        db.refresh(sale)
                    except SaleRuleError as error:
                        st.error(str(error))
                    else:
                        clear_data_cache()
                        st.session_state.last_sale_msg = (
                            f"Venda #{sale.id} registrada às {format_brt(sale.criada_em)} "
                            f"— {pizza_name} x{quantity} ({money(sale.valor_total)})"
                        )
                        st.rerun()
        with right, st.container(border=True):
            st.subheader("Receita da pizza")
            pizza_id = int(options[pizza_name])
            recipe = recipes[recipes["pizza_id"] == pizza_id]
            if recipe.empty:
                st.caption("Sem receita cadastrada.")
            else:
                merged = recipe.merge(
                    ingredients[["id", "nome", "unidade"]], left_on="ingrediente_id", right_on="id"
                )
                for row in merged.itertuples():
                    st.markdown(f"- {row.quantidade:g} {row.unidade} de **{row.nome}**")

with tab_cardapio:
    if last_added:
        st.success(f"Pizza **{last_added}** salva e disponível no cardápio.", icon=":material/check_circle:")

    st.subheader("Cardápio atual", icon=":material/menu_book:")
    if pizzas.empty:
        st.info("Nenhuma pizza cadastrada ainda.")
    else:
        active = pizzas[pizzas["ativa"] == True] if "ativa" in pizzas.columns else pizzas  # noqa: E712
        rows = list(active.sort_values("nome").iterrows())
        for start in range(0, len(rows), 3):
            cols = st.columns(3)
            for column, (_, pizza) in zip(cols, rows[start : start + 3]):
                with column, st.container(border=True):
                    highlight = last_added and pizza["nome"] == last_added
                    title = f"### :material/local_pizza: {pizza['nome']}"
                    if highlight:
                        title = f"### :material/star: {pizza['nome']}"
                    st.markdown(title)
                    st.write(money(pizza["preco"]))
                    recipe = recipes[recipes["pizza_id"] == pizza["id"]]
                    if recipe.empty:
                        st.caption("Sem receita.")
                    else:
                        merged = recipe.merge(
                            ingredients[["id", "nome", "unidade"]],
                            left_on="ingrediente_id",
                            right_on="id",
                        )
                        for r in merged.itertuples():
                            st.caption(f"{r.quantidade:g} {r.unidade} · {r.nome}")

    st.divider()
    if not can_manage_stock(perfil):
        st.info("Gerentes e administradores podem cadastrar novas pizzas.")
    elif ingredients.empty:
        st.warning("Cadastre ingredientes antes de criar receitas.")
    else:
        st.subheader("Cadastrar nova pizza", icon=":material/add_circle:")
        # multiselect fora do form para as quantidades aparecerem na hora
        selected = st.multiselect(
            "Ingredientes da receita",
            ingredients["nome"].tolist(),
            key="nova_pizza_ings",
            help="Escolha os itens e depois informe as quantidades.",
        )
        with st.form("nova_pizza", clear_on_submit=True):
            nome = st.text_input("Nome da pizza")
            preco = st.number_input("Preço de venda", min_value=0.01, step=1.0, value=39.90)
            quantities: dict[str, float] = {}
            if selected:
                st.markdown("**Quantidades por porção**")
                for item in selected:
                    unit = ingredients.loc[ingredients.nome == item, "unidade"].iloc[0]
                    quantities[item] = st.number_input(
                        f"{item} ({unit})",
                        min_value=0.01,
                        step=0.01,
                        value=0.10,
                        key=f"qty_form_{item}",
                    )
            else:
                st.caption("Selecione ao menos um ingrediente acima.")
            submitted = st.form_submit_button("Salvar no cardápio", type="primary", width="stretch")

        if submitted:
            if not nome.strip():
                st.error("Informe o nome da pizza.")
            elif not selected:
                st.error("Selecione pelo menos um ingrediente.")
            else:
                with SessionLocal() as db:
                    if db.scalar(select(Pizza).where(Pizza.nome == nome.strip())):
                        st.error("Essa pizza já existe.")
                    else:
                        pizza = Pizza(nome=nome.strip(), preco=float(preco), ativa=True)
                        pizza.receita_itens = [
                            RecipeItem(
                                ingrediente_id=int(
                                    ingredients.loc[ingredients.nome == item, "id"].iloc[0]
                                ),
                                quantidade=float(value),
                            )
                            for item, value in quantities.items()
                        ]
                        db.add(pizza)
                        db.commit()
                        db.refresh(pizza)
                        saved_name = pizza.nome
                        # confirma persistência da receita
                        saved = db.scalar(
                            select(Pizza)
                            .options(joinedload(Pizza.receita_itens))
                            .where(Pizza.id == pizza.id)
                        )
                        recipe_count = len(saved.receita_itens) if saved else 0
                clear_data_cache()
                if "nova_pizza_ings" in st.session_state:
                    del st.session_state["nova_pizza_ings"]
                st.session_state.last_pizza_added = saved_name
                st.toast(f"{saved_name} adicionada ({recipe_count} itens na receita)")
                st.rerun()

with tab_historico:
    if sales.empty:
        st.info("Nenhuma venda registrada.")
    else:
        recent = sales.sort_values("criada_em", ascending=False).head(50).copy()
        recent = recent.merge(pizzas[["id", "nome"]], left_on="pizza_id", right_on="id", how="left")
        recent["horário"] = pd.to_datetime(recent["criada_em"]).dt.strftime("%d/%m/%Y %H:%M")
        recent["total"] = recent["valor_total"].map(money)
        recent["custo"] = recent["custo_total"].map(money)
        st.dataframe(
            recent[["horário", "nome", "quantidade", "total", "custo"]].rename(columns={"nome": "pizza"}),
            width="stretch",
            hide_index=True,
        )
