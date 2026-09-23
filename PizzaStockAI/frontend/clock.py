from __future__ import annotations

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import streamlit as st

BRT = ZoneInfo("America/Sao_Paulo")


def brasilia_now() -> datetime:
    """Horário oficial atual em Brasília (naive, para gravar no banco)."""
    return datetime.now(BRT).replace(tzinfo=None)


def ensure_clock_state() -> None:
    st.session_state.setdefault("clock_manual", False)


def operational_now() -> datetime:
    """Horário operacional sincronizado com o relógio da sidebar."""
    ensure_clock_state()
    if st.session_state.clock_manual and "clock_applied_value" in st.session_state:
        elapsed = brasilia_now() - st.session_state.clock_applied_real
        return st.session_state.clock_applied_value + elapsed
    return brasilia_now()


def operational_today() -> date:
    return operational_now().date()


def set_clock_to(target: datetime) -> None:
    """Define o relógio operacional e deixa o tempo avançar a partir desse ponto."""
    ensure_clock_state()
    clean = target.replace(second=0, microsecond=0)
    st.session_state.clock_applied_value = clean
    st.session_state.clock_applied_real = brasilia_now()
    st.session_state.clock_manual = True


def reset_clock() -> None:
    ensure_clock_state()
    st.session_state.clock_manual = False
    st.session_state.pop("clock_applied_value", None)
    st.session_state.pop("clock_applied_real", None)


def format_brt(dt: datetime | None = None) -> str:
    return (dt or operational_now()).strftime("%d/%m/%Y %H:%M")


def render_clock_sidebar() -> None:
    """Relógio de Brasília ajustável — a venda usa exatamente este horário."""
    ensure_clock_state()
    now = operational_now()
    real = brasilia_now()
    label = "ajustado" if st.session_state.clock_manual else "oficial"

    st.markdown(f"### :material/schedule: {now.strftime('%H:%M:%S')}")
    st.caption(f"{now.strftime('%d/%m/%Y')} · Brasília ({label})")

    def _apply_from_widgets() -> None:
        d = st.session_state.clock_date
        t = st.session_state.clock_time
        set_clock_to(datetime.combine(d, t))

    with st.expander("Ajustar horário de Brasília", icon=":material/edit_calendar:"):
        st.date_input("Data", value=now.date(), key="clock_date", on_change=_apply_from_widgets)
        st.time_input(
            "Hora",
            value=time(now.hour, now.minute),
            step=60,
            format="24h",
            key="clock_time",
            on_change=_apply_from_widgets,
        )
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Aplicar", type="primary", width="stretch", icon=":material/check:"):
                _apply_from_widgets()
                st.rerun()
        with col_b:
            if st.button("Resetar", width="stretch", icon=":material/restart_alt:"):
                reset_clock()
                # alinha widgets ao horário oficial
                st.session_state.clock_date = real.date()
                st.session_state.clock_time = time(real.hour, real.minute)
                st.rerun()
        if st.session_state.clock_manual:
            st.caption(f"Oficial: {real.strftime('%H:%M:%S')} · vendas usam o horário ajustado")
        else:
            st.caption("Vendas gravadas no horário oficial de Brasília")
