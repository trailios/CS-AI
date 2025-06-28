import time
import requests

task_data = {"task_data": "example"}
res = requests.post("http://localhost:80/createTask", json=task_data)
task_id = res.json()["task_id"]

for _ in range(10):
    result = requests.get(f"http://localhost:80/getTaskResult/{task_id}").json()
    print("Status:", result["status"], "| Result:", result["result"])
    if result["status"] == "completed":
        break
    time.sleep(1)
