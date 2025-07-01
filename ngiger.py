from curl_cffi import requests
from faker import Faker

faker = Faker()
headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7',
    'content-type': 'application/json',
    'origin': 'https://puter.com/',
    'priority': 'u=1, i',
    'referer': 'https://puter.com/',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

json_data = {
    'username': faker.user_name(),
    'email': faker.email(safe=True, domain="gmail.com"),
    'password': faker.password(),
    'send_confirmation_code': False,
    'p102xyzname': '',
}

response = requests.post('https://puter.com/signup', headers=headers, json=json_data, impersonate="chrome")
if response.status_code == 200:
    data = response.json()
    if data.get('token', None) is not None and data["token"] != "":
        cookie = data["token"]
        import json
        with open("auth_token.json", "r") as f:
            data = json.load(f)
            data["tokens"].append(cookie)
        with open("auth_token.json", "a") as f:
            json.dump(data, f)

        headers["Authorization"] = f"Bearer {cookie}"
        ai = requests.post(
            "https://api.puter.com/drivers/call",
            headers=headers,
            json = {
                "interface": "puter-chat-completion",
                "driver": "openai-completion",
                "test_mode": False,
                "method": "complete",
                "args": {
                    "messages": [
                        {"role": "user", "content": "hi!"}
                    ],
                    "model": "gpt-4o-mini",
                    "stream": False,
                }
            }
        )
        print(ai.text)
        print(ai.status_code)
    else:
        print("No token found")
else:
    print("Failed to sign up")
    print(response.text)