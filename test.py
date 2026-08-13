import urllib.request
try:
    req = urllib.request.Request("https://schedule-api.nwero.net/schedule", headers={'User-Agent': 'Mozilla/5.0', 'Accept': '*/*'})
    with urllib.request.urlopen(req, timeout=5) as response:
        print(response.read().decode())
except Exception as e:
    print("Error:", e)
