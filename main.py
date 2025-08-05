from typing import Annotated, List

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

import os
from langchain.chat_models import init_chat_model

from dotenv import load_dotenv

load_dotenv()  # loads OPENAI_API_KEY

llm = init_chat_model("openai:gpt-4o")


class Email(TypedDict):
    key: str
    subject: str
    body: str
    customer_name: str
    mail_type: str


class State(TypedDict, total=False):
    raw_emails: str
    formatted_emails = List[Email]


def extract_emails(state: State) -> State:
    f = open("testdata.txt", "r")
    content = f.read()
    f.close()
    return {"raw_emails": content.split("---\n")}


def format_emails(state: State) -> State:
    formatted_emails = []
    raw_emails = state["raw_emails"]
    for string in raw_emails:
        email_string = string.strip().split("\n\n")
        email = dict.fromkeys(["subject", "body", "cust_name"])
        body_text = ""
        for idx, i in enumerate(email_string):
            # > Subject info
            if idx == 0:
                # * Removes the "Subject: " part
                email["subject"] = i[len("Subject: ") :]

            # > Customer name
            elif idx == len(email_string) - 1:
                # * Removes the "Regards\n" part
                email["cust_name"] = i[len("Regards\n\n") :]

            # > Body
            else:
                body_text += f"{i}\n\n"

        email["body"] = body_text.strip()
        formatted_emails.append(email)
    return {"formatted_emails": formatted_emails}

def categorize_emails(state: State) -> State:
    pass
