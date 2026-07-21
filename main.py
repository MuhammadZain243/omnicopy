from datetime import datetime, timezone
from annotated_types import T
from fastapi import Depends, FastAPI, HTTPException 
from typing import Annotated, Generic, TypeVar

from fastapi.concurrency import asynccontextmanager
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, Session, create_engine, select

class Campaign(SQLModel, table=True):
    campaign_id : int = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    due_date: datetime | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=True, index=True)

class CampaignCreate(SQLModel):
    name: str
    due_date: datetime | None = None

sqlite_file_name = "database.db"
sql_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sql_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
    
SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(Campaign)).first():
            session.add_all([
                Campaign(name="Summer Launch", due_date=datetime.now(timezone.utc)),
                Campaign(name="Black Friday", due_date=datetime.now(timezone.utc))
            ])
            session.commit()
    yield

app = FastAPI(root_path="/api/v1", lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "Hello World"}


'''
Campaigns
 - campaign_id,
 - name,
 - due_date,
 - created_at,
'''
T = TypeVar("T")
class Response(BaseModel, Generic[T]):
    data: T

@app.get("/campaigns", response_model=Response[list[Campaign]])
async def get_campaigns(session: SessionDep):
    campaigns = session.exec(select(Campaign)).all()
    return {"data": campaigns}

@app.get("/campaigns/{campaign_id}", response_model=Response[Campaign])
async def get_campaign(campaign_id: int, session: SessionDep):
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404)
    return {"data": campaign}

@app.post("/campaigns", status_code=201, response_model=Response[Campaign])
async def create_campaign(campaign: CampaignCreate, session: SessionDep):
    db_campaign = Campaign.model_validate(campaign)
    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)
    return {"data": db_campaign}

@app.put("/campaigns/{campaign_id}", response_model=Response[Campaign])
async def update_campaign(campaign_id: int, campaign: CampaignCreate, session: SessionDep):
    db_campaign = session.get(Campaign, campaign_id)
    if not db_campaign:
        raise HTTPException(status_code=404)
    db_campaign.name = campaign.name
    db_campaign.due_date = campaign.due_date
    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)
    return {"data": db_campaign}

@app.delete("/campaigns/{campaign_id}", status_code=204)
async def delete_campaign(campaign_id: int, session: SessionDep):
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404)
    session.delete(campaign)
    session.commit()

    