#!/bin/bash 
cd "/home/duong28/Documents/Big_project_1_Duong_Danny" ||exit 1 
export GCP_KEY_PATH="/home/duong28/Documents/Big_project_1_Duong_Danny/storage.json" 
myenv/bin/python3 main.py >> pipeline_cron.log 2>&1 