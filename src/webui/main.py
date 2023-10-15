import json

import uvicorn
from fastapi import FastAPI, Request, WebSocket
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_pagination import add_pagination
from fastapi_pagination.ext.motor import paginate
from fastapi_pagination.links import Page
from motor import motor_asyncio

from models import Customer

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

mongo_client = motor_asyncio.AsyncIOMotorClient("mongodb://localroot:asjf84q24jtr@localhost:27017")
mongo_db = mongo_client.kafka


@app.get("/customers", response_class=HTMLResponse, response_model=Page[Customer])
async def all_customers_view(request: Request):
    # customer_collection = await mongo_db.customers.find().to_list(100)
    # customers_paged = paginate()
    customers_paged = await paginate(mongo_db.customers)

    return templates.TemplateResponse(
        name="all_customers.html",
        context={"request": request, "customers": jsonable_encoder(customers_paged)['items']}
    )


@app.get("/customer", response_class=HTMLResponse)
async def customer_view(request: Request):
    orders = await mongo_db['all_orders'].find({"CUSTOMER.ID": "eec0cc07-e20e-5460-bd9c-2e3afc2e25a1"})
    orders = list(orders)
    customer = orders[0]['CUSTOMER']

    return templates.TemplateResponse(
        "customer.html", {"request": request, "customer": customer, "orders": orders}
    )


# @app.get("/orders", response_class=HTMLResponse)
#     pass


@app.get("/customer_ws")
async def customer_ws(websocket: WebSocket):
    await websocket.accept()
    while True:
        order = await websocket.receive_json()
        orders = mongo_db['all_orders'].find({"CUSTOMER.ID": "eec0cc07-e20e-5460-bd9c-2e3afc2e25a1"})
        orders = list(orders)
        await websocket.send_json(json.dumps(orders[0]))


add_pagination(app)

if __name__ == "__main__":
    uvicorn.run('main:app', host="127.0.0.1", port=8000, reload=True)
