import base64
import math
import random
import cv2
import numpy as np
from PIL import Image
from pillow_heif import register_heif_opener


def line_cor(a, b, c, xlim=(0, 600)):
    # Compute two points on the line
    x1 = xlim[0]
    y1 = (-a * x1 - c) / b
    x2 = xlim[1]
    y2 = (-a * x2 - c) / b
    return (int(x1), int(y1), int(x2), int(y2))


def ransac_line_fit(points, threshold=100, max_iterations=10000):
    """
    RANSAC line fitting algorithm.
    Arguments:
    - points: a list of 2D points in the form [(x1, y1), (x2, y2), ...]
    - threshold: the maximum distance allowed between a point and the fitted line
    - max_iterations: the maximum number of iterations to run the RANSAC algorithm
    Returns:
    - best_line: a tuple (m, b) representing the equation of the fitted line y = mx + b
    """

    # Convert the list of points to a numpy array for easier indexing
    best_line = None
    best_score = 0
    points_on_line = []
    for i in range(max_iterations):
        # Choose two random points from the list
        idx = random.sample(range(len(points)), 2)
        p1 = points[idx[0]]
        p2 = points[idx[1]]
        curr_points = []
        # Compute the equation of the line between the two points
        if p2[0] == p1[0]:
            continue  # avoid division by zero
        a = p2[1] - p1[1]
        b = p1[0] - p2[0]
        c = p2[0] * p1[1] - p1[0] * p2[1]
        print(a, b, a * 2 + b * 2)
        # Compute the distance between each point and the fitted line
        for point in points:
            d = abs(a * point[0] + b * point[1] + c) / math.sqrt(a * 2 + b * 2)
            if (d <= threshold):
                curr_points.append(point)

        # Update the best line if this iteration has more inliers than the previous best
        if len(curr_points) > best_score:
            best_line = line_cor(a, b, c)
            best_score = len(curr_points)
            points_on_line = curr_points

    return best_line, points_on_line


def get_stars(image: np.ndarray, size: tuple, threshold=127):
    circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 2, 20,
                               param1=250, param2=1, minRadius=2, maxRadius=6)

    # no need for more that 20 star, try to reduce the number
    desired_size = 20
    length = len(circles[0, :])
    if length > desired_size:
        for t in range(1, 6):
            circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 1, 20,
                                       param1=250, param2=t, minRadius=2, maxRadius=6)
            length = len(circles[0, :])
            if length < desired_size:
                break

    if circles is None:
        return []
    circles = np.uint16(np.around(circles))
    circles_cordinates = []
    for i in circles[0, :]:
        if i[0] < size[0] and i[1] < size[1]:
            circles_cordinates.append(
                (int(i[0]), int(i[1]), i[2] + 5, int(image[i[0], i[1]])))

    return circles_cordinates


# create the transformation matrix based on two sets of points
def create_mapper(source, destination):
    source = np.float32(source)
    destination = np.float32(destination)
    M = cv2.getAffineTransform(source, destination)

    def mapper(point):
        transformed_pt = np.dot(M, np.array([point[0], point[1], 1]))
        return (int(transformed_pt[0]), int(transformed_pt[1]))

    return mapper


# find mapped star in stars
def find_point(stars, source_point, mapped_point, e):
    x2, y2, r2, b2 = mapped_point

    for star in stars:
        x1, y1, r1, b1 = star
        # point = np.array([x, y])
        # dist = np.linalg.norm(point-mapped_point)
        dist_from_source = np.sqrt(
            (source_point[0] - x2) * 2 + (source_point[1] - y2) * 2)
        dist_s = np.sqrt((x1 - x2) * 2 + (y1 - y2) * 2)
        if dist_s < e and abs(r1 - r2) < 6:
            return star
    return None


# count the number of good points that are mapped correctly by 'T' from star1 to stars2 with error margin 'e'
def count_inliers(stars1, stars2, T, e=16):
    cnt = 0
    matchings = {}

    for star in stars1:
        x, y, r, b = star
        mapped_point = T((x, y))
        matched_point = find_point(
            stars2, star, (mapped_point[0], mapped_point[1], r, b), e)

        matchings[matched_point] = matchings.get(matched_point, 0) + 1

        if (matched_point is not None and matchings[matched_point] <= 1):
            cnt += 1
    return cnt


def matching_ratio(set_1, set_2, inliers_count):
    length = min(len(set_1), len(set_2))
    return inliers_count / length


def map_stars(stars1, stars2, iteration=10000):
    '''
        1- pick two identical stars in each list
        2- make transformation matrix from stars1 -> stars2
        3- return the transformation function
    '''
    line1, points_on_line_1 = ransac_line_fit(stars1)
    line2, points_on_line_2 = ransac_line_fit(stars2)

    # print('-----', len(points_on_line_1), len(points_on_line_2))
    best_t = None
    inliers_count = -1
    tried_seq = []
    pick_cnt = 3
    source_1 = None
    source_2 = None

    if (len(points_on_line_1) > 16):
        points_on_line_1 = random.sample(points_on_line_1, 16)

    if (len(points_on_line_2) > 16):
        points_on_line_2 = random.sample(points_on_line_2, 16)

    # s1 = find_good_triangle(points_on_line_1)
    for i in range(iteration):
        s1 = random.sample(points_on_line_1, pick_cnt)
        s2 = random.sample(points_on_line_2, pick_cnt)

        tup = (s1, s2)
        if (tup not in tried_seq):
            tried_seq.append(tup)
        else:
            # print('tried this', len(tried_seq), s2)
            continue

        # make transformations function
        a = np.array([(p[0], p[1]) for p in s1])
        b = np.array([(p[0], p[1]) for p in s2])
        t = create_mapper(a, b)

        # check how many inliers points
        count = count_inliers(points_on_line_1, points_on_line_2, t)

        if (count > inliers_count):
            inliers_count = count
            best_t = t
            source_1 = s1
            source_2 = s2

    mapped_stars = []
    for i, star in enumerate(points_on_line_1):
        x, y = best_t((star[0], star[1]))
        mapped_stars.append([(star[0], star[1]), (x, y)])

    return (mapped_stars, source_1, source_2, line1, points_on_line_1, line2, points_on_line_2,
            matching_ratio(points_on_line_1, points_on_line_2, inliers_count))


def get_image_difference(img1_str, image_path2, image_size=(600, 600)):
    """
    Find the geometric transformation that maps stars from the first image to the second.

    Parameters:
        image_path1 (str): The path to the first image.
        image_path2 (str): The path to the second image.
        output_path (str): The path where the mapped stars will be saved. Default is 'mapped_stars.txt'.
        image_size (tuple): A tuple representing the size to which the images should be resized. Default is (600, 600).

    Returns:
        float: The matching ratio, i.e. the number of inliers that match correctly according to the transformation.
    """

    # Register HEIF opener for supporting HEIF images
    register_heif_opener()

    # Load the images and resize them to the specified size
    img1_bytes = base64.b64decode(img1_str)
    img1_nparr = np.fromstring(img1_bytes, np.uint8)
    img1 = cv2.imdecode(img1_nparr, cv2.IMREAD_COLOR)
    img2 = np.array(Image.open(image_path2).resize(image_size))

    # Convert the images to grayscale, which is necessary for star detection
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Detect stars in the images
    stars1 = get_stars(img1_gray, image_size)
    stars2 = get_stars(img2_gray, image_size)

    # Map stars from the first image to the second image, and retrieve additional information
    mapped_stars, source_points, dest_points, line1, points_on_line_1, line2, points_on_line_2, inliers_count = map_stars(
        stars1, stars2)

    # # Save the mapped stars in a text file
    # save_mapped_stars(output_path, mapped_stars, image_size, ratio=inliers_count)
    #
    # # Display the images, stars, and the mapping
    # show_data(source_points, dest_points,
    #           points_on_line_1, line1, points_on_line_2, line2, mapped_stars, img1, img2)

    # Return the matching ratio
    return inliers_count
