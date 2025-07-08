from pydantic import BaseModel


# Define the event schema
class EventSchema(BaseModel):
    """Event Schema"""

    event_id: str
    event_type: str
    event_data: dict 