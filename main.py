import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import TopupProduct, SosmedService, EmptyNumber, Order

app = FastAPI(title="Top-up & Sosmed Services API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IDModel(BaseModel):
    id: str


@app.get("/")
def read_root():
    return {"message": "Top-up & Sosmed Services API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


# Helper to map Mongo docs

def map_docs(docs):
    mapped = []
    for d in docs:
        d = dict(d)
        d["id"] = str(d.pop("_id", ""))
        mapped.append(d)
    return mapped


# Catalog Endpoints
@app.get("/api/topup")
def list_topup_products():
    docs = get_documents("topupproduct", {}, limit=100)
    return map_docs(docs)


@app.post("/api/topup", status_code=201)
def create_topup_product(item: TopupProduct):
    _id = create_document("topupproduct", item)
    return {"id": _id}


@app.get("/api/sosmed")
def list_sosmed_services():
    docs = get_documents("sosmedservice", {}, limit=100)
    return map_docs(docs)


@app.post("/api/sosmed", status_code=201)
def create_sosmed_service(item: SosmedService):
    _id = create_document("sosmedservice", item)
    return {"id": _id}


@app.get("/api/numbers")
def list_empty_numbers():
    docs = get_documents("emptynumber", {"available": True}, limit=100)
    return map_docs(docs)


@app.post("/api/numbers", status_code=201)
def create_empty_number(item: EmptyNumber):
    _id = create_document("emptynumber", item)
    return {"id": _id}


# Orders
@app.post("/api/orders", status_code=201)
def create_order(order: Order):
    total = order.total_price
    if total is None:
        coll_map = {
            "topup": ("topupproduct",),
            "sosmed": ("sosmedservice",),
            "number": ("emptynumber",),
        }
        coll = coll_map[order.category][0]
        try:
            obj_id = ObjectId(order.product_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid product_id")
        docs = get_documents(coll, {"_id": obj_id}, limit=1)
        if not docs:
            raise HTTPException(status_code=404, detail="Product not found")
        product = docs[0]
        price = float(product.get("price", 0))
        total = price * order.quantity

    payload = order.model_dump()
    payload["total_price"] = total

    _id = create_document("order", payload)
    return {"id": _id, "status": "pending", "total_price": total}


@app.get("/api/orders")
def list_orders(limit: int = 50):
    docs = get_documents("order", {}, limit=limit)
    for d in docs:
        d["id"] = str(d.pop("_id", ""))
    return docs


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
