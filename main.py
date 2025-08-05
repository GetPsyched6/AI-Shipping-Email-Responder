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
    email_type: str


class State(TypedDict, total=False):
    data_file: str
    raw_emails: str
    formatted_emails: List[Email]
    categorized_emails: List[Email]


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


def categorize_emails(state: State) -> State:
    categorized_emails = []
    formatted_emails = state["formatted_emails"]
    for email in formatted_emails:
        prompt = (
            "The email is: {email}\n"
            "I want you to reply 'tracking' if it is a tracking email or 'booking' if it is a booking email."
        ).format(email=str(email))
        result = llm.invoke(prompt)
        email["email_type"] = result.content
        categorized_emails.append(email)
    return {"categorized_emails": categorized_emails}


graph = StateGraph(State)
graph.add_node("extract_emails", extract_emails)
graph.add_node("format_emails", format_emails)
graph.add_node("categorize_emails", categorize_emails)

graph.add_edge(START, "extract_emails")
graph.add_edge("extract_emails", "format_emails")
graph.add_edge("format_emails", "categorize_emails")
graph.add_edge("categorize_emails", END)

app = graph.compile()
final_state = app.invoke({"data_file": "testdata.txt"})
print(final_state["categorized_emails"])
