import json
import streamlit as st
from textcomplete import textcomplete, StrategyProps, TextcompleteResult

def st_textcomplete_autocomplete(
    label="Autocomplete Text Area",
    options=None,
    key="st_textcomplete_autocomplete",
    placeholder="Start typing...",
    height=120,
    help=None,
    max_count=10,
):
    """
    Render an autocomplete text area in Streamlit.

    Args:
        label: Label for text area.
        options: List of autocomplete options (strings).
        key: Streamlit key for session state.
        placeholder: Placeholder text.
        height: Height of the textarea.
        help: Help tooltip.
        max_count: Max autocomplete suggestions.

    Returns:
        The current query string.
    """
    
    if options is None:
        options = []

    # Session state init
    if f"{key}_query" not in st.session_state:
        st.session_state[f"{key}_query"] = ""
    if f"{key}_last_typed" not in st.session_state:
        st.session_state[f"{key}_last_typed"] = ""

    def on_change():
        st.session_state[f"{key}_last_typed"] = st.session_state[key]

    def on_select(res: TextcompleteResult):
        txt = res.get("text", "")
        st.session_state[f"{key}_query"] = txt
        st.session_state[f"{key}_last_typed"] = txt

    columns_js = json.dumps(options)
    stock_strategy = StrategyProps(
        id=f"{key}_strategy",
        match=r"(\w{1,})$",
        search=f"""(term, callback) => {{
            const opts = {columns_js};
            const matches = opts.filter(c =>
                c.toLowerCase().includes(term.toLowerCase())
            );
            callback(matches.map(m => [m]));
        }}""",
        replace="([col]) => col",
        template="([col]) => col",
    )

    # Optional: Custom CSS
    st.markdown("""
        <style>
        .textcomplete-dropdown {
            white-space: nowrap;
        }
        </style>
    """, unsafe_allow_html=True)

    txt = st.text_area(
        label=label,
        value=st.session_state[f"{key}_query"],
        key=key,
        height=height,
        help=help,
        placeholder=placeholder,
        on_change=on_change,
    )

    textcomplete(
        area_label=label,
        strategies=[stock_strategy],
        on_select=on_select,
        max_count=max_count,
        stop_enter_propagation=True,
        placement="auto",
        rotate=True,
        dynamic_width=True,
    )

    return st.session_state[f"{key}_last_typed"]