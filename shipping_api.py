# Copyright 2025 (c) Roshin Nishad. All rights reserved.
# Use of this source code is governed by the Apache 2.0 License that can be
# found in the LICENSE file.

from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date

class BookingRequest(BaseModel):
    origin: str
    destination: str
    pickup_date: date
    weight_kg: float
    
class TrackingRequest(BaseModel):
    tracking_id: str
    
class BookingResponse(BaseModel):
    confirmation_id: str
    eta_days: int
    
class TrackingResponse(BaseModel):
    status: str
    last_seen: str
    
# >* PICK RANDOM OPTION FROM LIST IN TRANSIT LOST MUMBAI DELHI ETC