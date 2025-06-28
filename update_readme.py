import requests
import base64
import os
from datetime import datetime
import pytz

# Secret'lar
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")
GH_ACCESS_TOKEN = os.getenv('GH_ACCESS_TOKEN')

# Access Token al
def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }
    res = requests.post(url, headers=headers, data=data)
    return res.json().get("access_token")

# Dinlenilen şarkıyı al
def get_now_playing(token):
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers)

    if res.status_code == 204:
        return "Not listening to anything right now ❌"
    try:
        data = res.json()
        artist = data["item"]["artists"][0]["name"]
        track = data["item"]["name"]
        return f"**{track}** by *{artist}* 🎶"
    except:
        return "Not available 🎧"

# Hava durumu
def get_weather():
    try:
        r = requests.get("https://wttr.in/Istanbul?format=3&m")
        return r.text.split(":", 1)[-1].strip()
    except:
        return "Unavailable 🌫️"

# Motivasyon sözü
def get_quote():
    try:
        r = requests.get("https://zenquotes.io/api/random")
        data = r.json()[0]
        return f'{data["q"]} — *{data["a"]}*'
    except:
        return "Stay strong. Keep coding. 💪"


# Tarih (İstanbul)
def get_date():
    tz = pytz.timezone('Europe/Istanbul')
    now = datetime.now(tz)
    return now.strftime("%A, %d %B %Y")

# GitHub katkısı (örnek statik, API entegresi ayrı yapılabilir)
def get_contribs():
    query = """
    query {
      user(login: "kekn9ne") {
        contributionsCollection {
          contributionCalendar {
            totalContributions
          }
        }
      }
    }
    """

    headers = {
        "Authorization": f"Bearer {GH_ACCESS_TOKEN}"
    }

    try:
        r = requests.post("https://api.github.com/graphql", json={"query": query}, headers=headers)
        data = r.json()
        print(data)
        count = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
        
        return str(count)
    except:
        return "Unavailable"


# README güncelle
def update_readme():
    with open("TEMPLATE.md", "r", encoding="utf-8") as f:
        content = f.read()

    content = content.replace("{{DATE}}", get_date())
    content = content.replace("{{WEATHER}}", get_weather())
    content = content.replace("{{QUOTE}}", get_quote())
    content = content.replace("{{NOW_PLAYING}}", get_now_playing(get_spotify_token()))
    content = content.replace("{{CONTRIBS}}", get_contribs())

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    update_readme()
