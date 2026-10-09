# Hackathon practice stack

Run:    docker compose up --build
Open:   http://localhost:3000
Test:   bash scripts/smoke.sh        (must print ALL GOOD)
Stop:   docker compose down

Folders: ml-service/, backend/, frontend/, docs/, scripts/
Team rule: one owner per folder, branch + small PRs, merge often.
GitHub runs the same build + smoke test on every PR (.github/workflows/ci.yml).
