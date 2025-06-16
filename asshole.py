import requests, hashlib, time, os

version = 1.0
prev_api_hash = ""

def api():
    r = requests.get("https://client-api.arkoselabs.com/v2/C07CAFBC-F76F-4DFD-ABFA-A6B78ADC1F29/api.js")
    hashed = hashlib.sha256(r.content).hexdigest()
    return hashed, r.content  # Return bytes here for writing as binary

def main():
    global prev_api_hash, version

    api_hash, api_content = api()

    if prev_api_hash != api_hash:
        os.makedirs("api", exist_ok=True)

        filename = f"api/arkose_api-v{version:.1f}.js"
        with open(filename, "wb") as f:  # Write as binary
            f.write(api_content)

        print(f"Updated arkose_api.js to version {version} with hash {api_hash}")

        # Prepare payload fields (content + embeds as JSON string)
        payload = {
            "content": f"Updated arkose_api.js to version {version:.1f} with hash `{api_hash}` ||@everyone||",
            "username": "Arkose API Tracker",
            "embeds": [{
                "title": "Arkose API Update",
                "description": f"**Version**: {version:.1f} (UNOFFICIAL)\n**Hash**: `{api_hash}`",
                "color": 5814783
            }]
        }

        # Discord expects embeds as JSON string when using multipart/form-data
        import json
        multipart_data = {
            "payload_json": (None, json.dumps(payload), 'application/json')
        }

        # Open file to send as 'file'
        with open(filename, "rb") as file:
            files = {
                **multipart_data,
                "file": (os.path.basename(filename), file, "application/javascript")
            }

            response = requests.post(
                "https://discord.com/api/webhooks/1379554861175013446/GrzMzChQ9HVheFnJzyCtmjf5sbrymu0h_uZ3rm4PXYSeSBEmA1DaFHYslRKFLCu1YKsL",
                files=files
            )

        if response.status_code == 204:
            print("Webhook sent successfully with file.")
        else:
            print(f"Failed to send webhook, status code: {response.status_code}, response: {response.text}")

        prev_api_hash = api_hash
        version += 0.1
    else:
        print("No update needed, API content is unchanged.")

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print(f"An error occurred: {e}")
        time.sleep(500)
