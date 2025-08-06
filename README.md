# Project: Email Categorization & Response Generation Using LangChain + FastAPI

## Objective

Build an AI-powered system that automates customer email handling for shipment services
using LangChain and FastAPI.
Project Workflow:

- Extract booking or tracking information (like tracking number, booking ID, customer
name) from incoming emails using an LLM.
- Categorize the email into one of two classes:
  - Shipment Booking
  - Shipment Tracking Status
- Call a mock FastAPI endpoint:
  - If booking → Call dummy booking API
  - If tracking → Call dummy tracking status API
- Feed the API response to an LLM with a system prompt to generate a customer-facing reply.
- Return the final generated response as an email reply.

### Tech Stack & Tools

- LangChain (prompt templates, tools, chains)
- FastAPI (for dummy backend APIs)
- LLM (OpenAI/Gemini for extraction & response)
- Optional: Use LangGraph if you'd like to structure the flow agentically
