from PIL import Image
from flask import Flask, request, jsonify
import datetime
import glob
import os
import base64
import julian
import requests
import cv2
import numpy as np
import json
from pillow_heif import register_heif_opener

import algo


class Server:
    def __init__(self):
        self.baseUrl = "http://localhost:8090/api/"
        self.datetime_format = "%Y-%m-%d %H:%M:%S"
        self.url_stelaction_list = "stelaction/list"
        self.url_stelaction_do = 'stelaction/do'
        self.url_location = 'location/setlocationfields'
        self.url_datetime = "main/time"
        self.url_fov = "main/fov"
        self.serverComputer = "ofekr"
        self.geocodingApiKey = "AIzaSyDWOCG7ITddc4d4LF75EJL_pwnoMAddGI0"

    def getStelactionList(self):
        try:
            list = requests.get(self.baseUrl + self.url_stelaction_list)
            print("list: ", list.status_code, list.content, list.text)
            return list
        except Exception as e:
            print("Error while getting stelaction list", e)

    def postLocation(self, latitude, longitude):
        args = {
            'longitude': longitude,
            'latitude': latitude,
        }

        try:
            resp = requests.post(self.baseUrl + self.url_location, data=args)
            if resp.status_code == 200:
                print('Location service request successful')
            else:
                print('Location service request failed:', resp.text)
        except Exception as e:
            print("Error while sending location POST request", e)

    def postDateTime(self, dateTime):
        print(f"dateTime = {dateTime}, type(dateTime) = {type(dateTime)}")
        parsed_datetime = datetime.datetime.strptime(dateTime, self.datetime_format)
        payload = {'time': str(julian.to_jd(parsed_datetime, fmt='jd'))}
        try:
            resp = requests.post(self.baseUrl + self.url_datetime, data=payload)
            if resp.status_code == 200:
                print("Date and time set successfully.")
            else:
                print("Failed to set the date and time.")
        except Exception as e:
            print("Error while sending date&time POST request", e)

    def postFOV(self, fov):
        try:
            param_fov = {'fov': fov}
            resp = requests.post(self.baseUrl + self.url_fov, data=param_fov)
            if resp.status_code == 200:
                print("FOV set successfully.")
            else:
                print("Failed to set the FOV.")
        except Exception as e:
            print("Error while sending FOV POST request", e)

    def getLastScreenshot(self):
        try:
            directory = f"C:/Users/{self.serverComputer}/Pictures/Stellarium"
            list_of_files = glob.glob(directory + '/*')
            if not list_of_files:
                return None
            latest_file = max(list_of_files, key=os.path.getctime)
            print(latest_file)
            return latest_file
        except Exception as e:
            print("Error while getting last saved screenshot", e)

    def showPlanets(self):
        try:
            requests.post(self.baseUrl + self.url_stelaction_do, data={'id': 'actionShow_Planets'})
            return True
        except Exception as e:
            print("Error showing planets", e)
            return False

    def showPlanetLabels(self):
        try:
            requests.post(self.baseUrl + self.url_stelaction_do, data={'id': 'actionShow_Planets_Labels'})
            return True
        except Exception as e:
            print("Error showing planet labels", e)
            return False

    def showStars(self):
        try:
            requests.post(self.baseUrl + self.url_stelaction_do, data={'id': 'actionShow_Stars'})
            return True
        except Exception as e:
            print("Error showing stars", e)
            return False

    def showGround(self):
        try:
            requests.post(self.baseUrl + self.url_stelaction_do, data={'id': 'actionShow_Ground'})
            return True
        except Exception as e:
            print("Error showing ground", e)
            return False

    def showGridlines(self):
        try:
            requests.post(self.baseUrl + self.url_stelaction_do, data={'id': 'actionShow_Gridlines'})
            return True
        except Exception as e:
            print("Error showing gridlines", e)
            return False

    def showEquaGrid(self):
        try:
            requests.post(self.baseUrl + self.url_stelaction_do, data={'id': 'actionShow_Equatorial_Grid'})
            return True
        except Exception as e:
            print("Error showing equa grid", e)
            return False

    def toggleGUI(self):
        try:
            requests.post(self.baseUrl + self.url_stelaction_do, data={'id': 'actionToggle_GuiHidden_Global'})
            return True
        except Exception as e:
            print("Error toggling GUI", e)
            return False

    def takeScreenshotsFromPosition(self, lat, lng, datetime, fov=60):
        self.postFOV(fov)
        self.postLocation(lat, lng)
        self.postDateTime(datetime)
        screenshotPaths = []
        path = self.takeScreenshot()
        screenshotPaths.append(path)
        self.lookNorth()
        path = self.takeScreenshot()
        screenshotPaths.append(path)
        self.lookSouth()
        path = self.takeScreenshot()
        screenshotPaths.append(path)
        self.lookEast()
        path = self.takeScreenshot()
        screenshotPaths.append(path)
        self.lookWest()
        path = self.takeScreenshot()
        screenshotPaths.append(path)
        self.lookUp()
        path = self.takeScreenshot()
        screenshotPaths.append(path)
        self.lookNP()
        path = self.takeScreenshot()
        screenshotPaths.append(path)
        self.lookSP()
        path = self.takeScreenshot()
        screenshotPaths.append(path)
        return screenshotPaths

    def takeScreenshot(self):
        try:
            screenshot = requests.post(self.baseUrl + self.url_stelaction_do,
                                       data={'id': 'actionSave_Screenshot_Global'})
            print("Screenshot: ", screenshot.status_code, screenshot.content, screenshot.text)
            return self.getLastScreenshot()
        except Exception as e:
            print("Error while getting screenshot", e)

    def lookEast(self):
        try:
            requests.post(self.baseUrl + self.url_stelaction_do, data={'id': 'actionLook_Towards_East'})
            return True
        except Exception as e:
            print("Error looking east", e)
            return False

    def lookWest(self):
        try:
            requests.post(self.baseUrl + self.url_stelaction_do, data={'id': 'actionLook_Towards_West'})
            return True
        except Exception as e:
            print("Error looking west", e)
            return False

    def lookNorth(self):
        try:
            requests.post(self.baseUrl + self.url_stelaction_do, data={'id': 'actionLook_Towards_North'})
            return True
        except Exception as e:
            print("Error looking North", e)
            return False

    def lookSouth(self):
        try:
            requests.post(self.baseUrl + self.url_stelaction_do, data={'id': 'actionLook_Towards_South'})
            return True
        except Exception as e:
            print("Error looking South", e)
            return False

    def lookUp(self):
        try:
            requests.post(self.baseUrl + self.url_stelaction_do, data={'id': 'actionLook_Towards_Zenith'})
            return True
        except Exception as e:
            print("Error looking up", e)
            return False

    def lookNP(self):
        try:
            requests.post(self.baseUrl + self.url_stelaction_do, data={'id': 'actionLook_Towards_NCP'})
            return True
        except Exception as e:
            print("Error looking NP", e)
            return False

    def lookSP(self):
        try:
            requests.post(self.baseUrl + self.url_stelaction_do, data={'id': 'actionLook_Towards_SCP'})
            return True
        except Exception as e:
            print("Error looking SP", e)
            return False

    def getScreenshotAsBase64(self, lat, lng, datetime, fov=60):
        screenshot_file_path = self.getScreenshot(lat, lng, datetime, fov)
        with open(screenshot_file_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')

    def addressToLatLng(self, adr):
        # URL-encode the address
        address = adr.replace(" ", "%20")

        # Build the URL
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={self.geocodingApiKey}"

        # Send a GET request
        response = requests.get(url)

        # Parse the response as JSON
        data = response.json()

        # Extract latitude and longitude from the response
        if data["results"]:
            lat = data["results"][0]["geometry"]["location"]["lat"]
            lng = data["results"][0]["geometry"]["location"]["lng"]
            print(f"Latitude: {lat}, Longitude: {lng}")
            print(f"({lat},{lng})")
            return lat, lng
        else:
            print("No results found")
            return None

    def process_circle_stars(self, img_str, size):
        img_np = np.frombuffer(base64.b64decode(img_str), np.uint8)
        img_original = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
        print("Image decoded.")

        img = cv2.cvtColor(img_original, cv2.COLOR_BGR2GRAY)
        print("Image converted to grayscale.")

        detectedStars = []
        circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 2, 20, param1=250, param2=1, minRadius=2,
                                   maxRadius=6)
        if circles is not None:
            print(f"Found {len(circles[0, :])} circles")
            desired_size = 20
            length = len(circles[0, :])
            if length > desired_size:
                for t in range(1, 6):
                    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 20, param1=250, param2=t,
                                               minRadius=2, maxRadius=6)
                    length = len(circles[0, :])
                    if length < desired_size:
                        break
            circles = np.uint16(np.around(circles))
            detectedStars = []
            for i in circles[0, :]:
                if i[0] < size[0] and i[1] < size[1]:
                    star = {
                        "x": int(i[0]),
                        "y": int(i[1]),
                        "r": i[2],
                        "b": int(img[i[0], i[1]])
                    }
                    detectedStars.append(star)
            print(f"Detected stars: {detectedStars}")

        for star in detectedStars:
            x = star['x']
            y = star['y']
            r = star['r']
            b = star['b']
            cv2.circle(img_original, (x, y), r + 10, (0, 255, 0), 3)

        retval, buffer = cv2.imencode('.jpg', img_original)
        img_str = base64.b64encode(buffer)
        print("Image encoded.")

        try:
            detectedStars = [{k: v.item() if isinstance(v, (np.int64, np.uint16, np.float64)) else v for k, v in
                              star.items()} for star in detectedStars]
            stars_json = json.dumps(detectedStars)
        except Exception as e:
            print(f"Error serializing detectedStars to JSON: {e}")
            return f"Error serializing detectedStars to JSON: {e}", 500

        return {
                   "image": img_str.decode("utf-8"),
                   "stars": stars_json
               }, 200


app = Flask(__name__)
server = Server()


@app.route('/screenshot', methods=['POST'])
def get_screenshot():
    data = request.get_json()
    img_str = data['img_str']
    size = data.get('size', "(600,600)")
    size = tuple(map(int, size.strip("()").split(',')))
    print(f"Parsed size: {size}")
    lat = data.get('lat')
    lng = data.get('lng')
    datetime = data.get('datetime')
    fov = data.get('fov', 60)

    # If 'lat' and 'lng' are not provided, check for 'address'
    if not lat and not lng:
        address = data.get('address')
        if address:
            lat, lng = server.addressToLatLng(address)
        else:
            return jsonify({'error': 'Either lat,lng or address must be provided'}), 400

    if lat and lng:
        file_paths = server.takeScreenshotsFromPosition(lat, lng, datetime, fov)
        print(file_paths)
        max_matches = -1
        max_matches_path = None
        for path in file_paths:
            matches = algo.get_image_difference(img_str, path, size)
            print(f"Matches: {matches}, Path: {path}")
            if matches > max_matches:
                max_matches = matches
                max_matches_path = path

        print(f"max matches: {max_matches}, path: {max_matches_path}")
        return jsonify({'max': max_matches_path})
    else:
        return jsonify({'error': 'Could not get valid coordinates'}), 400


@app.route('/circle_stars', methods=['POST'])
def circle_stars():
    data = request.get_json()
    print(f"Data: {data}")
    if data and 'img_str' in data and 'size' in data:
        img_str = data['img_str']
        size = data['size']
        print(f"Size: {size}, Image string: {img_str[:50]}...")  # prints first 50 characters
        size = tuple(map(int, size.strip("()").split(',')))
        print(f"Parsed size: {size}")
        return jsonify(server.process_circle_stars(img_str, size))
    return "Error circling stars!", 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
