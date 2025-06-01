import http.client

conn = http.client.HTTPSConnection("id-game-checker.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "5d46ed477amsha7589e64e74f3a5p16dde7jsncf0b8254d187",
    'x-rapidapi-host': "id-game-checker.p.rapidapi.com"
}

conn.request("GET", "/ff-player-info/1662626173/SG", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))