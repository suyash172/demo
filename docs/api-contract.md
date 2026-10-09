# API Contract (change only after telling the whole team)

## ml-service  (port 8001)
POST /predict
  in:  {"amount": 5000, "merchant": "demo-shop", "country": "IN"}
  out: {"fraud_score": 0.05, "decision": "allow|block", "reasons": ["..."]}

## backend  (port 8000)
POST /check   (same input as /predict)
  out: same as /predict + {"cached": true|false}
GET /health -> {"status": "ok"}
