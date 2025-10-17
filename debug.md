(.venv) jordan@jordan990301:~/projects/chat/backend$ cd ..
(.venv) jordan@jordan990301:~/projects/chat$ make dev
🚀 Starting development environment...
🛑 Stopping existing containers...
[+] Running 5/5
✔ Container frontend Removed 0.4s
✔ Container backend Removed 0.1s
✔ Container redis Removed 0.5s
✔ Container postgres_db Removed 0.4s
✔ Network chat_app-network Removed 0.4s
🔨 Building and starting services...
[+] Building 432.8s (25/25) FINISHED  
 => [internal] load local bake definitions 0.0s
=> => reading from stdin 719B 0.0s
=> [frontend internal] load build definition from Dockerfile 0.0s
=> => transferring dockerfile: 1.35kB 0.0s
=> [backend internal] load build definition from Dockerfile 0.0s
=> => transferring dockerfile: 1.40kB 0.0s
=> [backend internal] load metadata for docker.io/library/python:3.13-slim 2.2s
=> [frontend internal] load metadata for docker.io/library/node:22-alpine 0.1s
=> [auth] library/python:pull token for registry-1.docker.io 0.0s
=> CACHED [backend internal] load .dockerignore 0.0s
=> => transferring context: 417B 0.0s
=> [frontend base 1/3] FROM docker.io/library/node:22-alpine@sha256:1b2479dd35a99687d6638f5976fd235e26c5b37e8122f786fcd5fe231d63de5b 0.0s
=> => resolve docker.io/library/node:22-alpine@sha256:1b2479dd35a99687d6638f5976fd235e26c5b37e8122f786fcd5fe231d63de5b 0.0s
=> [frontend internal] load build context 1.7s
=> => transferring context: 165.67MB 1.7s
=> CACHED [frontend base 2/3] WORKDIR /app/frontend 0.0s
=> CACHED [frontend base 3/3] COPY ./frontend/package\*.json ./ 0.0s
=> CACHED [frontend development 1/2] RUN npm ci 0.0s
=> CACHED [frontend development 2/2] COPY ./frontend ./ 0.0s
=> [frontend] exporting to image 0.1s
=> => exporting layers 0.0s
=> => exporting manifest sha256:18f27eebf0c49d92366ec7bdbf18317844b9b8aabe4dc1a62302108a939d995e 0.0s
=> => exporting config sha256:ba54a25cb9afc5965b7407da23fde986e37c25105847e00ddeea34ab4df5a5cb 0.0s
=> => exporting attestation manifest sha256:4f5110034e29cf056a1bcd7af0ab64fee094814de57bce3859c7891d427ef5f5 0.0s
=> => exporting manifest list sha256:2752cd8a50d308fb9c4f719f65f9da2b9bd2b68f65a6500c4b5d7a48c3635e0f 0.0s
=> => naming to docker.io/library/chat-frontend:latest 0.0s
=> => unpacking to docker.io/library/chat-frontend:latest 0.0s
=> [frontend] resolving provenance for metadata file 0.0s
=> [backend base 1/3] FROM docker.io/library/python:3.13-slim@sha256:079601253d5d25ae095110937ea8cfd7403917b53b077870bccd8b026dc7c42f 0.0s
=> => resolve docker.io/library/python:3.13-slim@sha256:079601253d5d25ae095110937ea8cfd7403917b53b077870bccd8b026dc7c42f 0.0s
=> [backend internal] load build context 3.9s
=> => transferring context: 453.71MB 3.8s
=> CACHED [backend base 2/3] WORKDIR /app/backend 0.0s
=> [backend base 3/3] RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev build-essential curl && rm -rf /var/lib/ 198.4s
=> [backend dependencies 1/2] COPY ./backend/requirements.txt ./ 0.1s
=> [backend dependencies 2/2] RUN pip install --no-cache-dir -r requirements.txt 197.6s
=> [backend development 1/2] RUN pip install --no-cache-dir watchdog[watchmedo] debugpy 15.5s
=> [backend development 2/2] COPY ./backend ./ 2.2s
=> [backend] exporting to image 16.4s
=> => exporting layers 9.6s
=> => exporting manifest sha256:ec9d110c3671ffab25f855c2c784e46aebc6c87fa3f255dabc29e3564ecd0325 0.0s
=> => exporting config sha256:1c2f53d8b03267191c9d6bad07d28910d26831249435cfcd43254035922d2adf 0.0s
=> => exporting attestation manifest sha256:54f31e8bbae81d7e1c23d725017eb3b9034dee5160780653d63f969447d56985 0.0s
=> => exporting manifest list sha256:ad40d1e732bbf6b9270a70b9e2596442c174b63d9064ce3e8ee6da2be9405a3a 0.0s
=> => naming to docker.io/library/chat-backend:latest 0.0s
=> => unpacking to docker.io/library/chat-backend:latest 6.7s
=> [backend] resolving provenance for metadata file 0.0s
[+] Running 7/7
✔ backend Built 0.0s
✔ frontend Built 0.0s
✔ Network chat_app-network Created 0.0s
✔ Container redis Started 4.5s
✔ Container postgres_db Healthy 10.0s
✔ Container backend Started 9.7s
✔ Container frontend Started 7.3s
⏳ Waiting for services to be ready...
🏥 Checking service health...
NAME IMAGE COMMAND SERVICE CREATED STATUS PORTS
backend chat-backend "python main.py" backend 16 seconds ago Restarting (1) Less than a second ago  
frontend chat-frontend "docker-entrypoint.s…" frontend 13 seconds ago Up 5 seconds 0.0.0.0:5173->5173/tcp, [::]:5173->5173/tcp
postgres_db postgres:16-alpine "docker-entrypoint.s…" db 16 seconds ago Up 11 seconds (healthy) 0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp
redis redis:7-alpine "docker-entrypoint.s…" redis 16 seconds ago Up 11 seconds (healthy) 0.0.0.0:6379->6379/tcp, [::]:6379->6379/tcp

✅ Development environment is ready!

📝 Services:

- Frontend: http://localhost:5173
- Backend: http://localhost:5000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

📋 Useful commands:

- View logs: docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f
- Stop: docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
- Restart: docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart

(.venv) jordan@jordan990301:~/projects/chat$
