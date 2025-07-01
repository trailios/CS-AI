import requests
import time, threading

BASE_URL = "http://193.124.138.8:80"
def send():
    while True:
        create_payload = {
            "key": "my-secret-key",
            "task": {
                "type": "FunCaptcha",
                "extraData": {
                    "data[blob]": "a1b2c3d4e5"
                },
                "site_url": "https://example.com",
                "action": "start",
                "proxy": "http://127.0.0.1:8080"
            }
        }

        create_response = requests.post(f"{BASE_URL}/createTask", json=create_payload)

        if create_response.status_code == 200:
            data = create_response.json()
            task_id = data["task_id"]
            print(f"[+] Task created: {task_id}")
        else:
            print(f"[!] Failed to create task: {create_response.status_code}")
            print(create_response.text)
            exit(1)

        while True:
            result_response = requests.get(f"{BASE_URL}/getTaskResult/{task_id}")
            
            if result_response.status_code != 200:
                print(f"[!] Failed to fetch result: {result_response.text}")
                break

            result_data = result_response.json()
            status = result_data["status"]
            print(f"[i] Status: {status}")

            if status == "success":
                print("[+] Task completed successfully!")
                print("Result:", result_data["result"])
                break
            elif status == "failure":
                print("[x] Task failed.")
                print("Error:", result_data["result"])
                break
            else:
                time.sleep(0.5)

if __name__ == "__main__":
    threads = []
    for _ in range(10):
        thread = threading.Thread(target=send)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print("[*] All tasks completed.")