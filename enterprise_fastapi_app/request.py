import requests
import json
import uuid


def send_test_event():
    # API endpoint URL
    url = "http://localhost:8000/events/"

    # Sample event data
    event_data = {
        "event_id": str(uuid.uuid4()),
        "event_type": "test_event",
        "event_data": {
            "message": "Can you explain how to use FastAPI in an enterprise app?",
        },
    }

    # Headers for JSON content
    headers = {"Content-Type": "application/json"}

    print("--- Sending Test Event ---")
    # Send POST request to the endpoint
    try:
        response = requests.post(url=url, data=json.dumps(event_data), headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Print response information
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def create_test_user():
    # API endpoint URL
    url = "http://localhost:8000/users/"

    # Sample user data
    user_data = {
        "email": "test@example.com",
        "password": "a_very_secret_password",
        "full_name": "Test User",
    }

    # Headers for JSON content
    headers = {"Content-Type": "application/json"}

    print("\n--- Creating Test User ---")
    # Send POST request to the endpoint
    try:
        response = requests.post(url=url, data=json.dumps(user_data), headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Print response information
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    send_test_event()
    create_test_user()