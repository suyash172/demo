#!/usr/bin/env bash
# Run AFTER `docker compose up -d`. Exit code 0 = everything works end to end.
# Windows: run it in Git Bash or WSL.
FAIL=0

echo "Waiting for services (up to 60s)..."
for i in $(seq 1 30); do
    if curl -fs http://localhost:8000/health >/dev/null 2>&1 && curl -fs http://localhost:8001/health >/dev/null 2>&1 && curl -fs http://localhost:3000 >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

check() {
  if curl -fsS --max-time 5 "$2" >/dev/null 2>&1; then
    echo "PASS  $1"
  else
    echo "FAIL  $1  ($2)"
    FAIL=1
  fi
}

check "ml-service /health" http://localhost:8001/health
check "backend /health"    http://localhost:8000/health
check "frontend serves"    http://localhost:3000

RESP=$(curl -fsS --max-time 5 -X POST http://localhost:8000/check \
  -H "Content-Type: application/json" \
  -d '{"amount":90000,"merchant":"smoke","country":"US"}' 2>/dev/null)

if echo "$RESP" | grep -q '"decision":"block"'; then
  echo "PASS  end-to-end /check (backend -> redis -> ml-service)"
else
  echo "FAIL  end-to-end /check, got: $RESP"
  FAIL=1
fi

if [ "$FAIL" -eq 0 ]; then echo "ALL GOOD"; else echo "SOMETHING IS BROKEN"; fi
exit $FAIL
