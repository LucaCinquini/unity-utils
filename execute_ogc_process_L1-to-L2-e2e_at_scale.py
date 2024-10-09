# USAGE:
# export UNITY_USER=<unity username>
# export UNITY_PASSWORD=<unity password>
# export UNITY_OGC_API='http://unity-dev-httpd-alb-XXXXXXXX.us-west-2.elb.amazonaws.com:8080/unity/dev/ogc/'
#
import os
import time

from unity_sds_client.unity import Unity
from unity_sds_client.unity_services import UnityServices
from unity_sds_client.resources.job_status import JobStatus
from unity_sds_client.unity import UnityEnvironments

NUM_JOBS = 10

unity = Unity(UnityEnvironments.DEV)
unity.set_venue_id("")
process_service = unity.client(UnityServices.PROCESS_SERVICE)

process_service.endpoint = os.environ.get("UNITY_OGC_API", None)
procs = process_service.get_processes()

for p in procs:
    print(p)

process = process_service.get_process("cwl_dag")
print(process)

data = {
  "inputs": {
    "cwl_workflow": "https://raw.githubusercontent.com/unity-sds/sbg-workflows/refs/heads/main/L1-to-L2-e2e.scale.cwl",
    "cwl_args": "https://raw.githubusercontent.com/unity-sds/sbg-workflows/refs/heads/main/L1-to-L2-e2e.dev.scale.yml",
    "request_memory": "64Gi",
    "request_cpu": "32",
    "request_storage": "100Gi",
    "use_ecr": True
  },
  "outputs": {
    "result": {
      "transmissionMode": "reference"
    }
  }
}

jobs = []
status = []
for i in range(NUM_JOBS):
    jobs.append(process.execute(data))
    status.append(jobs[i].get_status().status)
    print(f"Job: {jobs[i].id} status: {status[i]}")
jobs_are_running = True

while jobs_are_running:
    jobs_are_running = False
    for i in range(NUM_JOBS):
        status[i] = jobs[i].get_status().status
        print(f"Job: {jobs[i].id} status: {status[i]}")
        if status[i] in [JobStatus.ACCEPTED, JobStatus.RUNNING]:
            jobs_are_running = True
    time.sleep(5)
