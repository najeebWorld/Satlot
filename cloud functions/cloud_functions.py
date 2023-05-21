import cv2
import numpy as np
import matplotlib.pyplot as plt
import base64


def circle_stars(request):
    try:
        print(f"Entered circle_stars func with: {request.get_data()}")
        try:
            request_json = request.get_json()
            print(f"Parsed JSON: {request_json}")
        except Exception as e:
            print(f"Error while parsing JSON: {e}")
            return f"Error: {e}", 500
        request_json = request.get_json()
        print(f"Request JSON: {request_json}")
        if request_json and 'img_str' in request_json and 'size' in request_json:
            img_str = request_json['img_str']
            size = request_json['size']
            print(f"Size: {size}, Image string: {img_str[:50]}...")  # prints first 50 characters
            print("Parsing size...")
            size = tuple(map(int, size.strip("()").split(',')))
            print(f"Parsed size: {size}")

            # Convert base64 string to a numpy array
            print("Decoding image from base64...")
            img_np = np.frombuffer(base64.b64decode(img_str), np.uint8)

            # Decode the numpy array into an image
            print("Decoding image with OpenCV...")
            img_original = cv2.imdecode(img_np, cv2.IMREAD_COLOR)
            print("Image decoded.")

            # gray image
            print("Converting image to grayscale...")
            img = cv2.cvtColor(img_original, cv2.COLOR_BGR2GRAY)
            print("Image converted to grayscale.")

            detectedStars = []
            print("Detecting circles...")
            circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 2, 20, param1=250, param2=1, minRadius=2, maxRadius=6)
            if circles is not None:
                print(f"Found {len(circles[0, :])} circles")
                desired_size = 20
                length = len(circles[0, :])
                if length > desired_size:
                    for t in range(1, 6):
                        circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 20, param1=250, param2=t, minRadius=2, maxRadius=6)
                        length = len(circles[0, :])
                        if length < desired_size:
                            break
                circles = np.uint16(np.around(circles))
                detectedStars = []
                for i in circles[0, :]:
                    if i[0] < size[0] and i[1] < size[1]:
                        detectedStars.append((int(i[0]), int(i[1]), i[2] + 5, int(img[i[0], i[1]])))
                print(f"Detected stars: {detectedStars}")

            # Draw circles on the image
            for (x, y, r, b) in detectedStars:
                cv2.circle(img_original, (x, y), r + 5, (0, 255, 0), 3)

            # Convert image to base64 string
            print("Encoding image to base64...")
            retval, buffer = cv2.imencode('.jpg', img_original)
            img_str = base64.b64encode(buffer)
            print("Image encoded.")

            # Return base64 string
            return img_str.decode("utf-8")
        else:
            return 'Invalid input!', 400
    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}", 500
