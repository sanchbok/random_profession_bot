#!/bin/bash
docker build -t my_bot .
docker-compose --env-file .env up
