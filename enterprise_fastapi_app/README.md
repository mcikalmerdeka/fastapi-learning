# FastAPI Enterprise Application Example

This project demonstrates a structured, enterprise-style layout for a FastAPI application. It is designed to be scalable, maintainable, and easy for teams to collaborate on.

## Project Structure

The application is broken down into several directories, each with a specific responsibility (Separation of Concerns).

```
app_fastapi/
│
├── api/
│   ├── events.py       # Handles API endpoints related to events
│   └── users.py        # Handles API endpoints related to users
│
├── core/
│   └── config.py       # Manages application-wide settings and configuration
│
├── schemas/
│   ├── event.py        # Pydantic schema for event data validation
│   └── user.py         # Pydantic schemas for user data (creation, response)
│
├── services/
│   └── event_service.py # Contains the core business logic for handling events
│
└── main.py             # The main entry point for the application
```

### Component Breakdown

- **`main.py`**: This is the heart of the application. It initializes the `FastAPI` app, loads the configuration from `core/config.py`, and includes the API routers from the `api/` directory. Its main job is to assemble the application from its various components.
- **`api/`**: This directory contains all the API endpoint logic. Each file (`events.py`, `users.py`) uses an `APIRouter` to group related endpoints. These files are responsible for handling HTTP requests, validating incoming data using schemas, and returning responses. They delegate the actual business logic to the `services/` layer.
- **`schemas/`**: This directory holds all the Pydantic models, which are used for data validation and serialization. Defining schemas ensures that the data flowing into and out of your API has a consistent and expected structure.
- **`services/`**: This is where the core business logic lives. For example, `event_service.py` contains the logic for what should happen when an event is received. By keeping business logic separate from the API endpoints, the code becomes more modular, easier to test, and reusable.
- **`core/`**: This directory is for application-wide concerns. `config.py` uses `pydantic-settings` to manage configuration variables (like the project name or database URLs), allowing you to easily manage settings for different environments (development, production).

## How to Run the Application

Follow these steps to get the application running on your local machine.

### 1. Install Dependencies

First, you need to install all the required Python packages. Navigate to the root directory of the project (`FastAPI Learning`) in your terminal and run:

```bash
pip install -r requirements.txt
```

### 2. Run the Server

Once the dependencies are installed, you can start the web server using `uvicorn`. This command tells `uvicorn` to run the `app` object from the `app_fastapi.main` module.

```bash
uvicorn app_fastapi.main:app --host 127.0.0.1 --port 8000 --reload
```

- `--host`: Specifies the IP address to run on.
- `--port`: Specifies the port to listen on.
- `--reload`: Automatically restarts the server whenever you make changes to the code.

The server is now running and ready to accept requests.

## How to Test the Endpoints

A simple Python script, `request.py`, is provided to test the API endpoints.

In a **new terminal window** (while the server is still running), execute the script:

```bash
python app_fastapi/request.py
```

This script will:

1. Send a POST request to the `/events/` endpoint with sample event data.
2. Send a POST request to the `/users/` endpoint to create a new user.

You will see the output from the script in your terminal, including the status codes and JSON responses from the server. You will also see the print statement from `event_service.py` in the terminal where the `uvicorn` server is running, demonstrating that the service layer was successfully called.
