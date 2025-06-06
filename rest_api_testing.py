from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn

# Source: https://chatgpt.com/c/6842bbc6-4d40-800a-aea3-e98a24b750f9

# 🔧 Create FastAPI app instance
app = FastAPI()

# 📦 Define the data model using Pydantic
class Item(BaseModel):
    id: int
    name: str
    description: str
    price: float

# 🗃️ Simulate a database using a list (for now this will reset when the server is restarted)
items_db: List[Item] = []

# Create a welcome message
@app.get("/")
def read_root():
    return {"message": "Welcome to the REST API Testing!"}

# 🧾 GET all items (Read)
@app.get("/items", response_model=List[Item])
def get_items():
    return items_db
# ✅ REST: This is a "Read" operation using HTTP GET

# 📥 POST a new item (Create)
@app.post("/items", response_model=Item)
def create_item(item: Item):

    # Check for duplicate IDs
    for existing_item in items_db:
        if existing_item.id == item.id:
            raise HTTPException(status_code=400, detail="Item with this ID already exists.")
        
    # Add the new item to the database
    items_db.append(item)
    return item
# ✅ REST: This is a "Create" operation using HTTP POST

# 🛠️ PUT to update an existing item (Update)
@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, updated_item: Item):
    for index, existing_item in enumerate(items_db):
        if existing_item.id == item_id:
            items_db[index] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found.")
# ✅ REST: This is an "Update" operation using HTTP PUT

# 🗑️ DELETE an item by ID (Delete)
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    for index, existing_item in enumerate(items_db):
        if existing_item.id == item_id:
            del items_db[index]
            return {"message": "Item deleted successfully."}
    raise HTTPException(status_code=404, detail="Item not found.")
# ✅ REST: This is a "Delete" operation using HTTP DELETE

# Run the app using uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

# # ================================ Testing using curl ================================

# # POST - Create new item
# curl -X POST "http://127.0.0.1:8000/items" -H "Content-Type: application/json" -d '{"id":1,"name":"Laptop","description":"Gaming laptop","price":1200.50}'

# # GET - Retrieve items
# curl -X GET "http://127.0.0.1:8000/items"

# # PUT - Update item with ID 1
# curl -X PUT "http://127.0.0.1:8000/items/1" -H "Content-Type: application/json" -d '{"id":1,"name":"Laptop Pro","description":"Updated","price":1400.00}'

# # DELETE - Delete item with ID 1
# curl -X DELETE "http://127.0.0.1:8000/items/1"

# # ================================ Testing using requests ================================

# import requests

# # POST
# response = requests.post("http://127.0.0.1:8000/items", json={
#     "id": 1,
#     "name": "Laptop",
#     "description": "Gaming laptop",
#     "price": 1200.50
# })
# print(response.json())

# # GET
# response = requests.get("http://127.0.0.1:8000/items")
# print(response.json())
