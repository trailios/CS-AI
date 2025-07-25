import requests

r = requests.post(
    "http://127.0.0.1/admin/generate",
    headers={
        "user-agent": "cai/admin/staff#7e1bcd88-6304-4f9f-9df9-52d642399d97"
    },
    json={
        "bought": 9
    }
)

rjson = r.json()
print(rjson["key"], rjson["bought"])