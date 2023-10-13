import json

import uvicorn
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_collection(collection):
    client = MongoClient("mongodb://localroot:asjf84q24jtr@localhost:27017")
    return client.get_database('kafka').get_collection(collection)


@app.get("/customer", response_class=HTMLResponse)
async def customer_view(request: Request):
    orders = list(get_collection('all_orders').find({"CUSTOMER.ID":"eec0cc07-e20e-5460-bd9c-2e3afc2e25a1"}))
    customer = orders[0]['CUSTOMER']

    return templates.TemplateResponse(
        "customer.html", {"request": request, "customer": customer, "orders": orders}
    )


@app.get("/customer_ws")
async def customer_ws(websocket: WebSocket):
    await websocket.accept()
    while True:
        order = await websocket.receive_json()
        orders = list(get_collection('all_orders').find({"CUSTOMER.ID": "eec0cc07-e20e-5460-bd9c-2e3afc2e25a1"}))
        await websocket.send_json(json.dumps(orders[0]))

if __name__ == "__main__":
    uvicorn.run('main:app', host="127.0.0.1", port=8000, reload=True)
