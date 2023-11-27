import streamlit as st
import json
from copy import deepcopy
import requests
from os import getenv


def start_configurator():
    st.session_state["configurator_in_progress"] = True
    st.session_state["client"] = PortalCLient(st.session_state["token"])
    response = st.session_state.client.initiate(st.session_state["reference"])
    st.session_state["configurator"] = response["state_definition"]
    st.session_state["configuration_id"] = response["configuration_id"]
    st.session_state["session_data"] = {}
    st.session_state["translations"] = json.load(open("translations.json", "r"))


def restart_configurator():
    st.session_state["configurator_in_progress"] = True
    st.session_state["client"] = PortalCLient(st.session_state["token"])
    response = st.session_state.client.back(
        st.session_state["configuration"], "cylinder.settings", {}
    )
    st.session_state["configurator"] = response["state_definition"]
    st.session_state["configuration_id"] = response["configuration_id"]
    st.session_state["session_data"] = {}
    st.session_state["translations"] = json.load(open("translations.json", "r"))


def process_choice(field, value=None):
    if value == None:
        value = st.session_state.get(field)
    st.session_state["session_data"][field] = value


def is_selected(field, value):
    return st.session_state["session_data"].get(field) == value


def condition_is_met(condition) -> bool:
    if condition == None:
        return True
    if condition["type"] == "equals":
        return (
            st.session_state["session_data"].get(condition["field"])
            == condition["value"]
        )
    if condition["type"] == "and":
        return all((condition_is_met(c) for c in condition["conditions"]))


def translate(key):
    parts = key.split(".")
    translations = deepcopy(st.session_state["translations"])
    for k in parts:
        translations = translations.get(k)
        if translations == None:
            return key
    return translations


def process_next():
    response = st.session_state.client.next(
        st.session_state["configuration_id"],
        st.session_state.configurator["id"],
        st.session_state["session_data"],
    )
    st.session_state["configurator"] = response["state_definition"]
    st.session_state["configuration_id"] = response["configuration_id"]
    st.session_state["session_data"] = {}
    if st.session_state.configurator["type"] == "productlist":
        if not has_products(st.session_state.configurator):
            filters = get_filters(st.session_state.configurator)
            response = st.session_state.client.get_products(filters)
            add_products(st.session_state.configurator, response["products"])


def process_back():
    response = st.session_state.client.back(
        st.session_state["configuration_id"],
        st.session_state.configurator["id"],
        st.session_state["session_data"],
    )
    st.session_state["configurator"] = response["state_definition"]
    st.session_state["configuration_id"] = response["configuration_id"]
    st.session_state["session_data"] = {}
    if st.session_state.configurator["type"] == "productlist":
        if not has_products(st.session_state.configurator):
            filters = get_filters(st.session_state.configurator)
            print(f"Collecting products with filters: {filters}")
            response = st.session_state.client.get_products(filters)
            add_products(st.session_state.configurator, response["products"])


def process_skip():
    response = st.session_state.client.skip(
        st.session_state["configuration_id"], st.session_state.configurator["id"]
    )
    st.session_state["configurator"] = response["state_definition"]
    st.session_state["configuration_id"] = response["configuration_id"]
    st.session_state["session_data"] = {}


def has_products(state_definition: dict) -> bool:
    for c in state_definition["content"]:
        if c["type"] == "products":
            return len(c["meta"]["products"]) > 0
    return False


def get_filters(state_definition: dict):
    if state_definition["type"] == "productlist":
        for c in state_definition["content"]:
            if c["type"] == "filters":
                return c["meta"]["filters"]


def add_products(state_definition: dict, products: list):
    for c in state_definition["content"]:
        if c["type"] == "products":
            c["meta"]["products"] = products


class PortalCLient:
    base_url = getenv("BASE_URL")

    def __init__(self, token):
        self.token = token

    def initiate(self, reference):
        response = requests.post(
            f"{self.base_url}/configurator/initiate",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"reference": reference},
        )
        return response.json()

    def next(self, configuration_id, state_id, data):
        data = {
            "configuration_id": configuration_id,
            "state_id": state_id,
            "configuration_data": [
                {"attribute_id": k, "value": v} for k, v in data.items()
            ],
        }
        response = requests.post(
            f"{self.base_url}/configurator/next",
            headers={"Authorization": f"Bearer {self.token}"},
            json=data,
        )
        return response.json()

    def back(self, configuration_id, state_id, data):
        data = {
            "configuration_id": configuration_id,
            "state_id": state_id,
            "configuration_data": [
                {"attribute_id": k, "value": v} for k, v in data.items()
            ],
        }
        response = requests.post(
            f"{self.base_url}/configurator/back",
            headers={"Authorization": f"Bearer {self.token}"},
            json=data,
        )
        return response.json()

    def skip(self, configuration_id, state_id):
        data = {
            "configuration_id": configuration_id,
            "state_id": state_id,
            "configuration_data": [],
        }
        response = requests.post(
            f"{self.base_url}/configurator/skip",
            headers={"Authorization": f"Bearer {self.token}"},
            json=data,
        )
        return response.json()

    def get_products(self, filters: dict):
        data = {"filters": filters}
        response = requests.post(
            f"{self.base_url}/products",
            headers={"Authorization": f"Bearer {self.token}"},
            json=data,
        )
        return response.json()
