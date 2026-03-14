import os
import time
import json
from app.core.dependencies import ingest

JOB_DIR = "jobs"

while True:
    jobs = os.listdir(JOB_DIR)
    for job_file in jobs:
        path = f"{JOB_DIR}/{job_file}"
        with open(path) as f:
            job = json.load(f)
        ingest.execute(job["files"])
        os.remove(path)
    time.sleep(2)