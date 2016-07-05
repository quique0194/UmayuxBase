from math import sqrt, atan2, degrees

def dist(a, b):
    return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)


def angle_to(a, b):
    return degrees(atan2(b[1]-a[1], b[0]-a[0]))


def normalize_angle(angle, min_angle=-180, max_angle=180):
    while angle < min_angle:
        angle += 360
    while angle >= max_angle:
        angle -= 360
    return angle
