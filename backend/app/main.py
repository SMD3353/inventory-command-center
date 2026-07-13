from contextlib import asynccontextmanager
from math import sqrt
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlmodel import Field as SQLField, Session, SQLModel, create_engine, select

DB_PATH = Path(os.environ.get("INVENTORY_DB_PATH", Path(__file__).resolve().parents[1] / "inventory_learning.db"))
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})

class Progress(SQLModel, table=True):
    id: int | None = SQLField(default=None, primary_key=True)
    mission_id: int = SQLField(index=True, unique=True)
    status: str = "available"
    score: int = 0
    reflection: str = ""

class RewardClaim(SQLModel, table=True):
    id: int | None = SQLField(default=None, primary_key=True)
    reward_id: int = SQLField(index=True, unique=True)

class Completion(BaseModel):
    score: int = Field(ge=0, le=100)
    reflection: str = Field(default="", max_length=1000)

class SimulationInput(BaseModel):
    daily_demand: float = Field(gt=0, le=100000)
    lead_time: float = Field(gt=0, le=365)
    demand_std: float = Field(ge=0, le=100000)
    service_z: float = Field(ge=0, le=4)
    review_period: float = Field(ge=0, le=365)

MISSIONS = [
 {"id":1,"day":"01","title":"Map the inventory flow","type":"Foundation","duration":50,"xp":80,"status":"available","brief":"Trace one SKU from supplier purchase order through receiving, storage, sale, return and adjustment.","deliverable":"Inventory-flow worksheet and five operational observations.","concepts":["SKU","purchase order","receipt","transfer","adjustment"]},
 {"id":2,"day":"02","title":"Decode the item master","type":"Data lab","duration":55,"xp":85,"status":"locked","brief":"Audit a noisy item master and identify records that would break replenishment.","deliverable":"Cleaned item-master table and exception log.","concepts":["item master","UOM","case pack","MOQ"]},
 {"id":3,"day":"03","title":"Reconcile stock movement","type":"Excel lab","duration":60,"xp":90,"status":"locked","brief":"Rebuild closing inventory from opening balance and transactions.","deliverable":"Excel reconciliation with variance flags.","concepts":["on hand","receipts","issues","adjustments"]},
 {"id":4,"day":"04","title":"Investigate phantom inventory","type":"Exception case","duration":55,"xp":95,"status":"locked","brief":"Compare system stock with cycle counts and isolate likely causes.","deliverable":"Root-cause memo and recount priority.","concepts":["cycle count","shrinkage","accuracy"]},
 {"id":5,"day":"05","title":"Write the operations update","type":"Communication","duration":45,"xp":75,"status":"locked","brief":"Convert analysis into a concise update for warehouse leadership.","deliverable":"Professional escalation email.","concepts":["impact","evidence","action owner"]},
 {"id":6,"day":"06","title":"Week 1 readiness review","type":"Review","duration":45,"xp":70,"status":"locked","brief":"Retrieve core concepts and correct earlier errors.","deliverable":"Review score and correction log.","concepts":["inventory flow","master data","accuracy"]},
 {"id":7,"day":"07","title":"Boss case: Warehouse 07","type":"Boss case","duration":60,"xp":150,"status":"locked","brief":"Resolve stockouts despite apparently healthy on-hand inventory.","deliverable":"Workbook, findings and prioritized action plan.","concepts":["inventory position","phantom stock","escalation"]},
]
COMPETENCIES = [
 {"name":"Inventory operations","level":1,"score":34,"target":80,"accent":"cyan"},
 {"name":"Excel analysis","level":1,"score":22,"target":80,"accent":"amber"},
 {"name":"Inventory KPIs","level":1,"score":18,"target":80,"accent":"cyan"},
 {"name":"Replenishment","level":1,"score":12,"target":80,"accent":"red"},
 {"name":"Inventory health","level":1,"score":20,"target":80,"accent":"amber"},
 {"name":"Demand analysis","level":1,"score":8,"target":80,"accent":"red"},
 {"name":"SQL","level":1,"score":5,"target":80,"accent":"red"},
 {"name":"Business communication","level":1,"score":26,"target":80,"accent":"cyan"},
]
REWARDS = [
 {"id":1,"title":"First Signal","description":"Verify your first mission","cost":0,"unlocked":False,"kind":"badge"},
 {"id":2,"title":"Five-Day Operator","description":"Complete five verified missions","cost":0,"unlocked":False,"kind":"badge"},
 {"id":3,"title":"Movie Protocol","description":"A pre-planned movie night","cost":450,"unlocked":False,"kind":"real-life"},
 {"id":4,"title":"Analyst Field Meal","description":"A planned favorite meal after Week 1","cost":700,"unlocked":False,"kind":"real-life"},
]
PORTFOLIO = [{"id":1,"title":"Warehouse Inventory Reconciliation","status":"in-progress","evidence":2,"required":5,"skills":["Excel","Inventory accuracy","Root cause analysis"],"summary":"Reconcile stock movement and explain material variances."}]
MANAGER_CASES = [{"id":1,"severity":"critical","title":"A-item stockout risk","deadline":"4 hours","situation":"SKU AX-104 is projected to stock out at three locations while 420 units remain at a low-velocity warehouse.","actions":["Reallocate stock","Expedite open PO","Offer substitute","Escalate revenue risk"]}]
LEARNING_MAP = [
 {"week":1,"name":"Receiving Dock","status":"active","x":12,"y":72},
 {"week":2,"name":"Data Bay","status":"locked","x":28,"y":55},
 {"week":3,"name":"KPI Tower","status":"locked","x":45,"y":64},
 {"week":4,"name":"Segmentation Yard","status":"locked","x":62,"y":42},
 {"week":5,"name":"Replenishment Hub","status":"locked","x":78,"y":52},
 {"week":6,"name":"Control Tower","status":"locked","x":90,"y":25},
]

def reward_unlocked(reward_id: int, verified: int, total_xp: int) -> bool:
    return {
        1: verified >= 1,
        2: verified >= 5,
        3: total_xp >= 450,
        4: total_xp >= 700,
    }.get(reward_id, False)


def seed():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        for m in MISSIONS:
            if not session.exec(select(Progress).where(Progress.mission_id == m["id"])).first():
                session.add(Progress(mission_id=m["id"], status=m["status"]))
        session.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed()
    yield

app = FastAPI(title="Inventory Command Center API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173","http://127.0.0.1:5173"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api/health")
def health(): return {"status":"operational","database":str(DB_PATH)}

@app.get("/api/dashboard")
def dashboard():
    seed()
    with Session(engine) as session:
        progress = {p.mission_id:p for p in session.exec(select(Progress)).all()}
        claims = {c.reward_id for c in session.exec(select(RewardClaim)).all()}
    missions=[]
    total_xp=0
    for m in MISSIONS:
        row=dict(m); p=progress[m["id"]]; row.update(status=p.status, score=p.score)
        if p.status=="verified": total_xp += m["xp"]
        missions.append(row)
    verified=sum(1 for m in missions if m["status"]=="verified")
    rewards=[]
    for reward in REWARDS:
        row=dict(reward)
        row.update(unlocked=reward_unlocked(reward["id"], verified, total_xp), claimed=reward["id"] in claims)
        rewards.append(row)
    return {
      "profile":{"name":"Mani","role":"Inventory Trainee","xp":total_xp,"level":1+total_xp//500,"streak":verified,"readiness":18+verified*3,"weekly_completed":verified},
      "missions":missions,"competencies":COMPETENCIES,"rewards":rewards,"portfolio":PORTFOLIO,"manager_cases":MANAGER_CASES,"learning_map":LEARNING_MAP,
      "alerts":[{"severity":"warning","text":"Cycle count variance exceeds tolerance in Zone C"},{"severity":"info","text":"Week 1 mission package is ready"}],
      "kpis":[{"label":"In-stock rate","value":"94.2%","delta":"-1.8%"},{"label":"Inventory accuracy","value":"91.6%","delta":"+0.7%"},{"label":"Weeks of supply","value":"7.4","delta":"+1.1"},{"label":"Open exceptions","value":"12","delta":"-3"}]
    }

@app.post("/api/missions/{mission_id}/complete")
def complete_mission(mission_id:int, body:Completion):
    if mission_id not in [m["id"] for m in MISSIONS]: raise HTTPException(404,"Mission not found")
    with Session(engine) as session:
        p=session.exec(select(Progress).where(Progress.mission_id==mission_id)).first()
        p.score=body.score; p.reflection=body.reflection; p.status="verified" if body.score>=70 else "needs-correction"
        session.add(p)
        if p.status=="verified" and mission_id < len(MISSIONS):
            nxt=session.exec(select(Progress).where(Progress.mission_id==mission_id+1)).first()
            if nxt and nxt.status=="locked": nxt.status="available"; session.add(nxt)
        session.commit(); session.refresh(p)
    return {"mission":{"id":mission_id,"status":p.status,"score":p.score}}

@app.post("/api/rewards/{reward_id}/claim")
def claim_reward(reward_id: int):
    reward = next((r for r in REWARDS if r["id"] == reward_id), None)
    if not reward:
        raise HTTPException(404, "Reward not found")
    with Session(engine) as session:
        progress = {p.mission_id: p for p in session.exec(select(Progress)).all()}
        verified = sum(1 for p in progress.values() if p.status == "verified")
        total_xp = sum(m["xp"] for m in MISSIONS if progress[m["id"]].status == "verified")
        if not reward_unlocked(reward_id, verified, total_xp):
            raise HTTPException(409, "Reward requirements not met")
        claim = session.exec(select(RewardClaim).where(RewardClaim.reward_id == reward_id)).first()
        if not claim:
            claim = RewardClaim(reward_id=reward_id)
            session.add(claim)
            session.commit()
        return {"reward": {**reward, "unlocked": True, "claimed": True}}

@app.post("/api/simulate")
def simulate(body:SimulationInput):
    horizon=body.lead_time+body.review_period
    safety=body.service_z*body.demand_std*sqrt(horizon)
    reorder=body.daily_demand*body.lead_time+safety
    target=body.daily_demand*horizon+safety
    return {"safety_stock":round(safety,1),"reorder_point":round(reorder,1),"order_up_to":round(target,1),"risk":"controlled" if safety/body.daily_demand>=1 else "elevated"}
