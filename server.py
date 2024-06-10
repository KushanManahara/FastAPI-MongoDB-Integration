from fastapi import FastAPI, HTTPException
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# MongoDB Atlas Data API details
API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("MONGODB_API_KEY")

HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Request-Headers": "*",
    "api-key": API_KEY,
}

DATABASE = "fastapi"
COLLECTION = "products"
DATA_SOURCE = "Atlas-cluster-01"

# Base payload object
BASE_PAYLOAD = {
    "collection": COLLECTION,
    "database": DATABASE,
    "dataSource": DATA_SOURCE,
}


# Create (Insert One) Operation
@app.post("/add_product/")
async def add_product(product: dict):
    url = f"{API_BASE_URL}insertOne"
    payload = BASE_PAYLOAD.copy()  # Create a copy of the base payload
    payload["document"] = product  # Add document field

    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


# Read (Find One) Operation
@app.get("/get_product/{product_id}")
async def get_product(product_id: str):
    url = f"{API_BASE_URL}findOne"
    payload = BASE_PAYLOAD.copy()  # Create a copy of the base payload
    payload["filter"] = {"productid": product_id}  # Add filter field

    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


# Update (Update One) Operation
@app.put("/update_product/{product_id}")
async def update_product(product_id: str, product: dict):
    url = f"{API_BASE_URL}updateOne"
    payload = BASE_PAYLOAD.copy()  # Create a copy of the base payload
    payload["filter"] = {"productid": product_id}  # Add filter field
    payload["update"] = {"$set": product}  # Add update field

    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


# Delete (Delete One) Operation
@app.delete("/delete_product/{product_id}")
async def delete_product(product_id: str):
    url = f"{API_BASE_URL}deleteOne"
    payload = BASE_PAYLOAD.copy()  # Create a copy of the base payload
    payload["filter"] = {"productid": product_id}  # Add filter field

    response = requests.post(url, headers=HEADERS, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


@app.post("/add_purchase/")
async def add_purchase(customer_id: str, product_id: str, quantity: int):
    # Add purchase to sells collection
    sells_payload = {
        "collection": SELLS_COLLECTION,
        "document": {
            "customer_id": customer_id,
            "product_id": product_id,
            "quantity": quantity,
        },
    }
    sells_response = requests.post(
        f"{API_BASE_URL}insertOne", headers=HEADERS, json=sells_payload
    )
    if sells_response.status_code != 200:
        raise HTTPException(
            status_code=sells_response.status_code, detail=sells_response.text
        )

    # Update customer table with bought products, quantity, and amount
    customer_payload = {
        "collection": CUSTOMER_COLLECTION,
        "filter": {"customer_id": customer_id},
        "update": {
            "$push": {"purchases": {"product_id": product_id, "quantity": quantity}}
        },
    }
    customer_response = requests.post(
        f"{API_BASE_URL}updateOne", headers=HEADERS, json=customer_payload
    )
    if customer_response.status_code != 200:
        raise HTTPException(
            status_code=customer_response.status_code, detail=customer_response.text
        )

    return {"message": "Purchase added successfully and customer updated."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
