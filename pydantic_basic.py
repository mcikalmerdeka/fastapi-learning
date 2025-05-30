from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional

"""
One of the biggest problem with python is that it is a dynamically typed language.
This means that you can pass a string to a function that expects an int and it will not throw an error.
The biggest downside of using a dynamic type is tha tit allows you to accidentally create an invalid object.

example:
alice = Person(name="Alice", age=25) # This is valid
alice = Person(name="Alice", age="25") # This is invalid

Luckily, these days python has a lot of tools to solve these problems like using dataclasses, type hints, and type checking.

But, Pydantic is the one that is most popular and easiest to use.
"""

"""
Pydantic is a data validation and settings management library for Python.
Some notable libraries that depend on pydantic:
- huggingface/transformers
- tiangolo/FastAPI
- hwchase17/langchain
- apache/airflow

Main features:
- IDE Type Hints
- Data Validation
- JSON Serialization
- Customizable Error Messages
- Extensible

"""

# Using Pydantic
class User(BaseModel):
    name: str
    email: EmailStr
    account_id: int

    ## Custom validation
    @field_validator("account_id")
    @classmethod
    def validate_account_id(cls, value):
        if value <= 0:
            raise ValueError(f"Account ID must be positive, Your input was: {value}")
        return value
    
# Create an instance of the class
user_1 = User(name="John", email="john@example.com", account_id=123)
print(user_1.name)

# ## Another way to do it is by unpacking a dictionary (useful when you get data from an API)
# user_data = {
#     "name": "John",
#     "email": "john@example.com",
#     "account_id": 123
# }

# user = User(**user_data)
# print(user.name)

# ## Data validation (with wrong input for account_id)
# user_2 = User(name="John", email="john@example.com", account_id="hello")
# print(user_2.name)

# ## Data validation (catch error in field_validator)
# user_3 = User(name="John", email="john@example.com", account_id=0)
# print(user_3.name)

## JSON Serialization
user_json_serialized = user_1.model_dump_json()
print(user_json_serialized)

## JSON Deserialization (turn back json string to pydantic object)
user_json_deserialized = User.model_validate_json(user_json_serialized)
print(user_json_deserialized)

## Python dict
user_dict = user_1.model_dump()
print(user_dict)

# ================================ Comparison with other libraries/approaches ================================

# Python 3.6+
x: int = 0
y: str = "hello"

# Dataclasses
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: EmailStr
    account_id: int