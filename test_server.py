import requests

url = 'http://localhost:5000/screenshot'
data = {
    # 'lat': 37.7749,  # Latitude
    # 'lng': -122.4194,  # Longitude
    'address': "Ramat Hagolan 3, Ariel, Israel",
    'datetime': '2023-06-10 23:00:00',  # Date and time
    'size': '(600,600)',
    'fov': 60  # Field of view (optional, default value is 60)
}

response = requests.post(url, json=data)
if response.status_code == 200:
    screenshots = response.json()['Screenshots']
    print("Screenshots:", screenshots)
else:
    print("Error:", response.text)