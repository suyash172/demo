from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Txn(BaseModel):
    amount: float
    merchant: str
    country: str = "IN"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(t: Txn):
    # Toy rules standing in for a real ML model
    score = min(t.amount / 100000, 1.0)
    reasons = []
    if t.amount > 50000:
        reasons.append("High amount")
    if t.country != "IN":
        score = min(score + 0.3, 1.0)
        reasons.append("Foreign transaction")
    decision = "block" if score > 0.7 else "allow"
    return {"fraud_score": round(score, 2), "decision": decision, "reasons": reasons}
