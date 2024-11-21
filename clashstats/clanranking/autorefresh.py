import requests
import time
from dotenv import load_dotenv
load_dotenv()
import os


while True:
    url = f'http://{os.environ.get("HOST", "127.0.0.1")}:{os.environ.get("PORT", "8000")}/clanrefresh/G9JVLC2C'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("View called successfully.")
        else:
            print(f"Error calling view: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    print(f"Waiting for 1 hour.")
    time.sleep(3600)
