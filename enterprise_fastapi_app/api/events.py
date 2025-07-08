import json
from http import HTTPStatus

from fastapi import APIRouter
from starlette.responses import Response

from app_fastapi.schemas.event import EventSchema
from app_fastapi.services import event_service

# Initialize the router
router = APIRouter()


@router.post("/", dependencies=[])
def handle_event(data: EventSchema) -> Response:
    """
    Endpoint to receive an event.
    It delegates the business logic to the event_service.
    """
    # Call the service layer to handle the logic
    result = event_service.handle_event_logic(data)

    # Return acceptance response
    return Response(
        content=json.dumps(result),
        status_code=HTTPStatus.ACCEPTED,
    ) 