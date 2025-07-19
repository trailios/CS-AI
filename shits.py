import requests

r = requests.post(
    "http://127.0.0.1:82/admin/generate",
    headers={
        "user-agent": "cai/admin/staff#7e1bcd88-6304-4f9f-9df9-52d642399d97"
    },
    json={
        "bought": 0.6
    }
)

rjson = r.json()
print(rjson["key"], rjson["bought"])

r2 = requests.post(
    "http://127.0.0.1:82/admin/key/stats",
    headers={
        "user-agent": "data/key/stats#0e3eae2a-ec61-4fe0-87f2-4476d159d197"
    },
    json={
        "key": rjson["key"]
    }
)

print(r2.json())