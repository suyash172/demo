# Dockerfile templates (copy into your service folder, adjust port)

Rules for every service:
- Listen on 0.0.0.0 (not 127.0.0.1) or other containers can't reach it
- Fixed port from docs/api-contract.md
- Has GET /health
- All config via env vars (set in docker-compose.yml)
- Talk to other services by compose service name (http://backend:8000), NEVER localhost
- Has a .dockerignore

## Python / FastAPI (also for ML model serving)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

ML tips: pin the SAME scikit-learn/xgboost version used for training in requirements.txt
(a pickled model loaded with a different version is a classic hidden bug). Commit the model
file (small) or load it from a path inside the image. Heavy libs make big images: build once at home.

## Node / Express
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY . .
CMD ["node", "index.js"]

## Spring Boot (Maven, Java 17)
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn -q dependency:go-offline
COPY src ./src
RUN mvn -q package -DskipTests

FROM eclipse-temurin:17-jre
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]

In docker-compose.yml set: SERVER_PORT=8000 and e.g.
SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/app (host = service name, not localhost).

## React / Vite (build, then serve with nginx)
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html

Note: Vite bakes VITE_* vars at BUILD time, and the browser (not the container) calls the API,
so the URL must be one your browser can reach (http://localhost:8000), not http://backend:8000.

## Postgres in compose (with a volume so data survives restarts)
  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=app
      - POSTGRES_PASSWORD=app
      - POSTGRES_DB=app
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      retries: 10
(and at the bottom of the compose file:  volumes:\n  pgdata:)
