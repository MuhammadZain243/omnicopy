from datetime import datetime
from math import dist
from random import randint
from fastapi import FastAPI, HTTPException, Response
from typing import Any

app = FastAPI(root_path="/api/v1")

@app.get("/")
async def root():
    return {"message": "Hello World"}


data : Any = [
    {
        "campaign_id": 1,
        "name": "Campaign 1",
        "due_date": datetime.now(),
        "created_at": datetime.now()
    },
    {
        "campaign_id": 2,
        "name": "Campaign 2",
        "due_date": datetime.now(),
        "created_at": datetime.now()
    }
]

'''
Campaigns
 - campaign_id,
 - name,
 - due_date,
 - created_at,
'''

@app.get("/campaigns")
async def read_campaigns():
    return {"campaigns": data}

@app.get("/campaigns/{id}")
async def read_campaign(id: int):
    for campaign in data:
        if campaign["campaign_id"] == id:
            return {"campaign": campaign}
    raise HTTPException(status_code=404, detail="Campaign not found")

@app.post("/campaigns", status_code=201)
async def create_campaign(body: dict[str, Any]):
    
    new_campaign = {
        "campaign_id": randint(1, 1000),
        "name": body.get("name"),
        "due_date": datetime.now(),
        "created_at": datetime.now()
    }

    data.append(new_campaign)
    return {"campaign": new_campaign}

@app.put("/campaigns/{id}")
async def update_campaign(id: int, body: dict[str, Any]):
    for index, campaign in enumerate(data):
        if campaign["campaign_id"] == id:
            updated_campaign: Any = {
                "campaign_id": id,
                "name": body.get("name", campaign["name"]),
                "due_date": body.get("due_date", campaign["due_date"]),
                "created_at": campaign["created_at"]
            }

            data[index] = updated_campaign
            return {"campaign": updated_campaign}
    raise HTTPException(status_code=404, detail="Campaign not found")

@app.delete("/campaigns/{id}")
async def delete_campaign(id: int):
    for i, campaign in enumerate(data):
        if campaign["campaign_id"] == id:
            del data[i]
            return Response(status_code=204)
    raise HTTPException(status_code=404, detail="Campaign not found")