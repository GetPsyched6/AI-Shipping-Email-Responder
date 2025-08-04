from typing import Annotated, List

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

import os
from langchain.chat_models import init_chat_model

from dotenv import load_dotenv

load_dotenv()  # loads OPENAI_API_KEY

llm = init_chat_model("openai:gpt-4o-mini")

f = open("testdata.txt", "r")
content = f.read()
f.close()

raw_emails = content.split("---\n")
formatted_emails = []

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

print(formatted_emails)
