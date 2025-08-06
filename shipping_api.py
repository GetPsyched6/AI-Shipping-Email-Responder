# Copyright 2025 (c) Roshin Nishad. All rights reserved.
# Use of this source code is governed by the Apache 2.0 License that can be
# found in the LICENSE file.

from fastapi import FastAPI
from pydantic import BaseModel
import random

app = FastAPI()


class BookingRequest(BaseModel):
    origin: str
    destination: str
    pickup_date: str
    weight: str


class TrackingRequest(BaseModel):
    tracking_id: str


class BookingResponse(BaseModel):
    confirmation_id: str
    quote: str
    eta_days: int


class TrackingResponse(BaseModel):
    status: str
    last_seen: str


@app.post("/book_shipment", response_model=BookingResponse)
def book_shipment(req: BookingRequest):
    return BookingResponse(
        confirmation_id=f"BK{random.randint(10000, 99999)}",
        quote=f"${random.randint(200, 1000)}",
        eta_days=random.randint(1, 50),
    )


@app.post("/track_shipment", response_model=TrackingResponse)
def track_shipment(req: TrackingRequest):
    return TrackingResponse(
        status=random.choice(
            ["IN TRANSIT", "LOST", "DELAYED", "SHIPPED", "OUT FOR DELIVERY"]
        ),
        last_seen=f"{random.choice(["Mumbai", "Delhi", "Bangalore", "Noida", "Goa"])} warehouse",
    )
