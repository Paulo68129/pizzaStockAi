from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import sys

import pandas as pd
import streamlit as st
from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.database import SessionLocal
from backend.models import Ingredient
from frontend.data import can_delete, can_manage_stock, clear_data_cache, load_data, money


def format_validade(series: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(series, errors="coerce")
    return parsed.dt.strftime("%d/%m/%Y").fillna("—")


st.title("Estoque", icon=":material/inventory_2:")
st.caption("Cadastro de ingredientes, validade e recomendações de compra.")

ingredients, pizzas, recipes, sales = load_data()
perfil = st.session_state.user["perfil"]

stock_value = float((ingredients["estoque"] * ingredients["custo_unitario"]).sum()) if not ingredients.empty else 0.0
critical = ingredients[ingredients["estoque"] <= ingredients["estoque_minimo"]] if not ingredients.empty else ingredients

with st.container(horizontal=True):
    st.metric("Valor em estoque", money(stock_value), border=True)
    st.metric("Itens", str(len(ingredients)), border=True)
    st.metric("Críticos", str(len(critical)), border=True)

tab_lista, tab_form, tab_edit = st.tabs(["Ingredientes", "Adicionar", "Editar / excluir"])

with tab_lista:
    if ingredients.empty:
        st.info("Nenhum ingrediente cadastrado.")
    else:
        table = ingredients.copy()
        table["status"] = table.apply(
            lambda r: "Crítico" if r.estoque <= r.estoque_minimo else "Saudável", axis=1
        )
        if "data_validade" in table.columns:
            table["validade"] = format_validade(table["data_validade"])
        display_cols = ["nome", "estoque", "unidade", "estoque_minimo", "custo_unitario", "status"]
        if "validade" in table.columns:
            display_cols.insert(-1, "validade")
        st.dataframe(
            table[display_cols],
            width="stretch",
            hide_index=True,
            column_config={
                "custo_unitario": st.column_config.NumberColumn("Custo unitário", format="R$ %.2f"),
                "estoque": st.column_config.NumberColumn("Estoque", format="%.2f"),
                "estoque_minimo": st.column_config.NumberColumn("Mínimo", format="%.2f"),
            },
        )
    with st.container(border=True):
        st.subheader("Recomendação de compras", icon=":material/local_shipping:")
        if critical.empty:
            st.success("Nenhuma compra urgente.")
        else:
            for row in critical.itertuples():
                suggested = max(row.estoque_minimo * 2 - row.estoque, 0)
                st.markdown(f"**{row.nome}:** comprar {suggested:.1f} {row.unidade}")

with tab_form:
    if not can_manage_stock(perfil):
        st.warning("Apenas gerente ou administrador podem cadastrar ingredientes.")
    else:
        with st.form("novo_ingrediente"):
            nome = st.text_input("Nome")
            estoque = st.number_input("Estoque", min_value=0.0, step=0.1)
            minimo = st.number_input("Estoque mínimo", min_value=0.0, step=0.1)
            unidade = st.selectbox("Unidade", ["kg", "un", "l", "g"])
            custo = st.number_input("Custo unitário", min_value=0.0, step=0.1)
            validade = st.date_input("Data de validade", value=date.today())
            submitted = st.form_submit_button("Adicionar", type="primary")
        if submitted:
            if not nome.strip():
                st.error("Informe o nome.")
            else:
                with SessionLocal() as db:
                    if db.scalar(select(Ingredient).where(Ingredient.nome == nome.strip())):
                        st.error("Ingrediente já existe.")
                    else:
                        db.add(
                            Ingredient(
                                nome=nome.strip(),
                                estoque=estoque,
                                estoque_minimo=minimo,
                                unidade=unidade,
                                custo_unitario=custo,
                                data_validade=datetime.combine(validade, datetime.min.time()),
                            )
                        )
                        db.commit()
                        clear_data_cache()
                        st.success("Ingrediente adicionado.")
                        st.rerun()

with tab_edit:
    if ingredients.empty:
        st.info("Cadastre ingredientes primeiro.")
    elif not can_manage_stock(perfil):
        st.warning("Sem permissão para editar estoque.")
    else:
        options = dict(zip(ingredients["nome"], ingredients["id"]))
        selected = st.selectbox("Selecionar ingrediente", list(options))
        row = ingredients[ingredients["id"] == options[selected]].iloc[0]
        units = ["kg", "un", "l", "g"]
        unit_index = units.index(row["unidade"]) if row["unidade"] in units else 0
        with st.form("editar_ingrediente"):
            nome = st.text_input("Nome", value=row["nome"])
            estoque = st.number_input("Estoque", min_value=0.0, value=float(row["estoque"]), step=0.1)
            minimo = st.number_input("Estoque mínimo", min_value=0.0, value=float(row["estoque_minimo"]), step=0.1)
            unidade = st.selectbox("Unidade", units, index=unit_index)
            custo = st.number_input("Custo unitário", min_value=0.0, value=float(row["custo_unitario"]), step=0.1)
            save = st.form_submit_button("Salvar alterações", type="primary")
        if save:
            with SessionLocal() as db:
                item = db.get(Ingredient, int(row["id"]))
                item.nome = nome.strip()
                item.estoque = estoque
                item.estoque_minimo = minimo
                item.unidade = unidade
                item.custo_unitario = custo
                db.commit()
            clear_data_cache()
            st.success("Ingrediente atualizado.")
            st.rerun()
        if can_delete(perfil) and st.button("Excluir ingrediente", type="secondary", icon=":material/delete:"):
            with SessionLocal() as db:
                item = db.get(Ingredient, int(row["id"]))
                if item:
                    db.delete(item)
                    db.commit()
            clear_data_cache()
            st.success("Ingrediente excluído.")
            st.rerun()
