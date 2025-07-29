"""
Small helper for Streamlit pagination widgets.
"""
import math
import streamlit as st


def init(total_rows: int, page_size: int) -> None:
    """Store total pages in session_state (called once each run)."""
    if "page_no" not in st.session_state:
        st.session_state.page_no = 1
    st.session_state.max_page = max(1, math.ceil(total_rows / page_size))


def _prev() -> None:
    st.session_state.page_no -= 1


def _next() -> None:
    st.session_state.page_no += 1


def ui(page_size: int) -> tuple[int, int]:
    """
    Render ‹Prev / Page-X-of-Y / Next› bar  
    and return the slice (start, end) for the current page.
    """
    col_prev, col_page, col_next = st.columns([1, 2, 1])

    with col_prev:
        st.button("⬅ Prev", on_click=_prev, disabled=st.session_state.page_no == 1)

    with col_next:
        st.button(
            "Next ➡",
            on_click=_next,
            disabled=st.session_state.page_no == st.session_state.max_page,
        )

    with col_page:
        st.markdown(
            f"<div style='text-align:center'>Page "
            f"{st.session_state.page_no} / {st.session_state.max_page}</div>",
            unsafe_allow_html=True,
        )

    start = (st.session_state.page_no - 1) * page_size
    end = start + page_size
    return start, end

