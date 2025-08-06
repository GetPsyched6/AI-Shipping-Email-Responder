# Copyright 2025 (c) Roshin Nishad. All rights reserved.
# Use of this source code is governed by the Apache 2.0 License that can be
# found in the LICENSE file.

from typing import Annotated, List

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langchain.chat_models import init_chat_model

from dotenv import load_dotenv

import requests

load_dotenv()  # loads OPENAI_API_KEY

llm = init_chat_model("openai:gpt-4.1-mini")


class KeyDetails(TypedDict):
    tracking_id: str
    origin: str
    destination: str
    pickup_date: str
    weight: str


class Email(TypedDict):
    key: str
    subject: str
    body: str
    customer_name: str
    email_type: str
    key_details: KeyDetails
    api_response: dict


class State(TypedDict, total=False):
    data_file: str
    raw_emails: str
    formatted_emails: List[Email]
    parsed_and_categorized_emails: List[Email]
    api_response_emails: List[Email]


def extract_emails(state: State) -> State:
    file_name = state["data_file"]
    f = open(file_name, "r")
    content = f.read()
    f.close()
    return {"raw_emails": content.split("---\n")}


def format_emails(state: State) -> State:
    formatted_emails = []
    raw_emails = state["raw_emails"]
    for string in raw_emails:
        email_string = string.strip().split("\n\n")
        email = Email()
        body_text = ""
        for idx, i in enumerate(email_string):
            email["key"] = f"email_{idx}"
            # > Subject info
            if idx == 0:
                # * Removes the "Subject: " part
                email["subject"] = i[len("Subject: ") :]

            # > Customer name
            elif idx == len(email_string) - 1:
                # * Removes the "Regards\n\n" part
                email["customer_name"] = i[len("Regards\n\n") :]

            # > Body
            else:
                body_text += f"{i}\n\n"

        email["body"] = body_text.strip()
        formatted_emails.append(email)
    return {"formatted_emails": formatted_emails}


def parse_and_categorize_emails(state: State) -> State:
    parsed_and_categorized_emails = []
    formatted_emails = state["formatted_emails"]
    for email in formatted_emails:
        key_details = KeyDetails()
        prompt = (
            "The email is: {email}\n"
            "I want you to reply 'tracking' if it is a tracking email or 'booking' if it is a booking email. Then in a new line I want you extract the following information if available in this order (tracking number, origin, destination, pickup date, weight) and write it as comma seperated values (no spaces). If a specific value isn't available, just leave it blank like (,Mumbai,Bangalore,July 7,40)."
        ).format(email=str(email))
        result = llm.invoke(prompt)
        email_info = result.content.split("\n")
        email["email_type"] = email_info[0]
        raw_key_details = email_info[1].split(",")
        key_details["tracking_id"] = raw_key_details[0]
        key_details["origin"] = raw_key_details[1]
        key_details["destination"] = raw_key_details[2]
        key_details["pickup_date"] = raw_key_details[3]
        key_details["weight"] = raw_key_details[4]
        email["key_details"] = key_details
        parsed_and_categorized_emails.append(email)
    return {"parsed_and_categorized_emails": parsed_and_categorized_emails}


def call_api(state: State) -> State:
    api_response_emails = []
    parsed_and_categorized_emails = state["parsed_and_categorized_emails"]
    for email in parsed_and_categorized_emails:
        key_details = email["key_details"]
        if email["email_type"] == "booking":
            payload = {
                "origin": key_details["origin"],
                "destination": key_details["destination"],
                "pickup_date": key_details["pickup_date"],
                "weight": key_details["weight"],
            }
            resp = requests.post("http://127.0.0.1:8000/book_shipment", json=payload)
            data = resp.json()
            email["api_response"] = data

        if email["email_type"] == "tracking":
            payload = {"tracking_id": key_details["tracking_id"]}
            resp = requests.post("http://127.0.0.1:8000/track_shipment", json=payload)
            data = resp.json()
            email["api_response"] = data
        api_response_emails.append(email)
    return {"api_response_emails": api_response_emails}


graph = StateGraph(State)
graph.add_node("extract_emails", extract_emails)
graph.add_node("format_emails", format_emails)
graph.add_node("parse_and_categorize_emails", parse_and_categorize_emails)
graph.add_node("call_api", call_api)

graph.add_edge(START, "extract_emails")
graph.add_edge("extract_emails", "format_emails")
graph.add_edge("format_emails", "parse_and_categorize_emails")
graph.add_edge("parse_and_categorize_emails", "call_api")
graph.add_edge("call_api", END)

app = graph.compile()
final_state = app.invoke({"data_file": "testdata.txt"})
# print(
#     [
#         [email["email_type"], email["api_response"]]
#         for email in final_state["api_response_emails"]
#     ]
# )
print(final_state["api_response_emails"])
