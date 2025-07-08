from app_fastapi.schemas.event import EventSchema


def handle_event_logic(data: EventSchema):
    """
    This is where you would implement the core business logic for handling the event.
    For example, processing data, triggering other services, etc.
    """
    # Print the data
    print("Event received in service layer:")
    print(data)

    # The service can return a result, which the endpoint can then use in its response.
    return {"message": "Data received and processed by the service!"} 