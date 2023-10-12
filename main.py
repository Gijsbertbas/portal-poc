import streamlit as st
from process import start_configurator, condition_is_met, process_choice, translate, is_selected


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
        st.button("Start Configurator", on_click=start_configurator)

    if st.session_state.get("configurator_in_progress"):
        st.title(translate(st.session_state["configurator"]["title"]))

        for c in st.session_state["configurator"]["content"]:
            if condition_is_met(c["condition"]):
                if c["title"]:
                    st.header(translate(c["title"]))
                if c["subtitle"]:
                    st.subheader(translate(c["subtitle"]))
                if c["type"] == "choice":
                    cols = st.columns([1, 1, 1])
                    for i, choice in enumerate(c["meta"]["choices"]):
                        with cols[i]:
                            st.button(
                                translate(choice["title"]),
                                on_click=process_choice,
                                args=(c["id"], choice["value"]),
                                disabled=is_selected(c["id"], choice["value"])
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

with tab2:
    for k, v in st.session_state.get("session_data", {}).items():
        st.text(f'{k}: "{v}"')
