from typing import Annotated, List

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langchain.chat_models import init_chat_model

from dotenv import load_dotenv

load_dotenv()  # loads OPENAI_API_KEY

llm = init_chat_model("openai:gpt-4.1-mini")


class Email(TypedDict):
    key: str
    subject: str
    body: str
    customer_name: str
    email_type: str
    key_details: List[str]


class State(TypedDict, total=False):
    data_file: str
    raw_emails: str
    formatted_emails: List[Email]
    parsed_and_categorized_emails: List[Email]


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
        prompt = (
            "The email is: {email}\n"
            "I want you to reply 'tracking' if it is a tracking email or 'booking' if it is a booking email. Then in a new line I want you extract the following information if available (tracking number, booking ID, anything of that type) and write it as comma seperated values (no spaces)"
        ).format(email=str(email))
        result = llm.invoke(prompt)
        email_info = result.content.split("\n")
        email["email_type"] = email_info[0]
        email["key_details"] = email_info[1].split(",")
        parsed_and_categorized_emails.append(email)
    return {"parsed_and_categorized_emails": parsed_and_categorized_emails}


graph = StateGraph(State)
graph.add_node("extract_emails", extract_emails)
graph.add_node("format_emails", format_emails)
graph.add_node("parse_and_categorize_emails", parse_and_categorize_emails)

graph.add_edge(START, "extract_emails")
graph.add_edge("extract_emails", "format_emails")
graph.add_edge("format_emails", "parse_and_categorize_emails")
graph.add_edge("parse_and_categorize_emails", END)

app = graph.compile()
final_state = app.invoke({"data_file": "testdata.txt"})
print(final_state["parsed_and_categorized_emails"])
