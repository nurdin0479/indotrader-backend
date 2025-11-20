#!/bin/bash
cd /srv/indotrader
git pull origin main

docker compose down
docker compose build
docker compose up -d

echo "Deployed at $(date)" >> /srv/deploy-logs/backend.log
