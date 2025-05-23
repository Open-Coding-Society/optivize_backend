from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import date

app = FastAPI()

class CalendarEvent(BaseModel):
    title: str
    date: date
    description: str

@app.get("/api/calendartest", response_model=List[CalendarEvent])
async def get_calendar_test():
    return [
        {
            "title": "Morning Shift - Sarah",
            "date": "2025-05-21",
            "description": "Sarah covers the register and front counter."
        },
        {
            "title": "Midday Delivery",
            "date": "2025-05-21",
            "description": "Flour and chocolate chip delivery from supplier."
        },
        {
            "title": "Inventory Audit",
            "date": "2025-05-22",
            "description": "Weekly inventory check with Alex."
        },
        {
            "title": "Evening Shift - Jason",
            "date": "2025-05-22",
            "description": "Jason manages closing shift and cleanup."
        },
        {
            "title": "Weekly Staff Meeting",
            "date": "2025-05-23",
            "description": "All hands meeting to discuss workflow improvements."
        },
        {
            "title": "Restock: Packaging Materials",
            "date": "2025-05-23",
            "description": "Restocking boxes, wrappers, and stickers."
        },
        {
            "title": "Monthly Performance Review",
            "date": "2025-05-24",
            "description": "1-on-1 reviews with team members."
        },
        {
            "title": "POS System Update",
            "date": "2025-05-25",
            "description": "Backend update scheduled at 2 AM. Downtime expected."
        },
        {
            "title": "Training Session - New Hires",
            "date": "2025-05-25",
            "description": "Training session for newly hired employees."
        },
        {
            "title": "Special Promotion Launch",
            "date": "2025-05-26",
            "description": "Start of Memorial Day promo for cookie bundles."
        }
    ]
