import streamlit as st
import json
from copy import deepcopy



def start_configurator():
    st.session_state['configurator_in_progress'] = True
    st.session_state['configurator'] = json.load(open('configurator.json', 'r'))
    st.session_state['session_data'] = {}
    st.session_state['translatioins'] = json.load(open('translations.json', 'r'))


def process_choice(field, value):
    st.session_state['session_data'][field] = value


def condition_is_met(condition) -> bool:
    if condition == None:
        return True
    if condition['type'] == 'equals':
        return st.session_state['session_data'].get(condition['field']) == condition['value']
    if condition['type'] == 'and':
        return all((condition_is_met(c) for c in condition['conditions']))


def translate(key):
    parts = key.split('.')
    translations = deepcopy(st.session_state['translatioins'])
    for k in parts:
        translations = translations.get(k)
        if translations == None:
            return key
    return translations
