import streamlit as st
from process import (
    start_configurator,
    condition_is_met,
    restart_configurator,
    process_choice,
    translate,
    is_selected,
    process_next,
    process_back,
    process_skip,
)


st.markdown(
    """
<style>
button {
    height: 150px;
    width: 200px !important;
}
</style>
""",
    unsafe_allow_html=True,
)


tab1, tab2 = st.tabs(["configurator", "result"])
with tab1:
    if not st.session_state.get("configurator_in_progress"):
        st.text_input("Token", key="token", placeholder="ID token")
        st.markdown("""---""")
        cols = st.columns([1, 1])
        with cols[0]:
            st.text("Start a new configuration")
            st.text_input("Reference", key="reference", placeholder="your reference")
            st.button("Start Configurator", on_click=start_configurator)
        with cols[1]:
            st.text("Restart an existing configuration")
            st.text_input("Configuration ID", key="configuration")
            st.button("Restart Configurator", on_click=restart_configurator)

    if st.session_state.get("configurator_in_progress"):
        st.title(translate(st.session_state["configurator"]["title"]))

        for c in st.session_state["configurator"]["content"]:
            if condition_is_met(c["condition"]):
                if c["title"]:
                    st.header(translate(c["title"]))
                if c["subtitle"]:
                    st.subheader(translate(c["subtitle"]))
                if c["type"] == "choice":
                    if c["meta"]["type"] == "button":
                        cols = st.columns([1] * len(c["meta"]["choices"]))
                        for i, choice in enumerate(c["meta"]["choices"]):
                            with cols[i]:
                                st.button(
                                    translate(choice["title"]),
                                    on_click=process_choice,
                                    args=(c["id"], choice["value"]),
                                    disabled=is_selected(c["id"], choice["value"]),
                                )
                    if c["meta"]["type"] == "dropdown":
                        st.selectbox(
                            "choose",
                            options=c["meta"]["options"],
                            on_change=process_choice,
                            args=(c["id"],),
                            key=c["id"],
                        )
                    if c["meta"]["type"] == "radio":
                        st.radio(
                            "choose",
                            options=[
                                translate(o["title"]) for o in c["meta"]["choices"]
                            ],
                            on_change=process_choice,
                            args=(c["id"],),
                            key=c["id"],
                        )

                if c["type"] == "input":
                    st.number_input(
                        translate(c["meta"]["label"]),
                        placeholder=translate(c["meta"]["placeholder"]),
                        min_value=c["meta"]["range"]["min"],
                        max_value=c["meta"]["range"]["max"],
                        on_change=process_choice,
                        args=(c["id"],),
                        key=c["id"],
                    )
                if c["type"] == "products":
                    st.subheader("Products:")
                    for product in c["meta"]["products"]:
                        st.text(f"{product['name']} - {product['article_number']}")
                if c["type"] == "filters":
                    st.subheader("Filters:")
                    if "category" in c["meta"]:
                        st.text(f"Category: {c['meta']['category']}")
                    if c["meta"]["filters"]:
                        for k, v in c["meta"]["filters"].items():
                            st.text(f"{k}: {v}")

        with st.sidebar:
            st.button("Back", on_click=process_back)
            st.button("Next", on_click=process_next)
            st.button("Skip", on_click=process_skip)


with tab2:
    for k, v in st.session_state.get("session_data", {}).items():
        st.text(f'{k}: "{v}"')
