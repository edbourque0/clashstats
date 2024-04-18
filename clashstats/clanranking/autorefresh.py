import requests
import time

while True:
    url = 'http://192.168.2.39:8000/clanrefresh/G9JVLC2C'
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
