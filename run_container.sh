#!/bin/bash
docker build -t my_bot .
docker run --rm -d --env-file .env my_bot