#!/bin/bash

docker compose up -d

while true; do sleep 10m && docker compose down && docker compose up -d --build; done