#!/bin/bash
docker build -t ccc_proj .
docker run -d --name my_ccc_proj -p 5566:5566 -v ./logs:/app/logs ccc_proj