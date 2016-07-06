from math import sqrt
from flag_positions import flag_positions
from mymath import dist, angle_to



def closer_point(target_point, list_of_points):
    list_of_points.sort(key=lambda x: dist(x, target_point))
    return list_of_points[0]


def mean_points(list_of_points):
    ret = [0,0]
    for point in list_of_points:
        ret[0] += point[0]
        ret[1] += point[1]
    ret[0] /= len(list_of_points)
    ret[1] /= len(list_of_points)
    return ret


def intersect_circles(P0, P1, r0, r1):
    """
    Determines whether two circles collide and, if applicable,
    the points at which their borders intersect.
    Based on an algorithm described by Paul Bourke:
    http://local.wasp.uwa.edu.au/~pbourke/geometry/2circle/
    Arguments:
      P0 (2-tuple): the centre point of the first circle
      P1 (2-tuple): the centre point of the second circle
      r0 (numeric): radius of the first circle
      r1 (numeric): radius of the second circle
    Returns:
      False if the circles do not collide
      True if one circle wholly contains another such that the borders
          do not overlap, or overlap exactly (e.g. two identical circles)
      An array of two complex numbers containing the intersection points
          if the circle's borders intersect.
    """
    if len(P0) != 2 or len(P1) != 2:
        raise TypeError("P0 and P1 must be 2-tuples")
    d = dist(P0, P1)

    if d > (r0 + r1):
        return False
    elif d < abs(r0 - r1):
        return True
    elif d == 0:
        return True

    a = (r0**2 - r1**2 + d**2) / (2 * d)
    b = d - a
    temp = max(0, r0**2 - a**2)
    h = sqrt(temp)
    P2 = [0, 0]
    P2[0] = P0[0] + a * (P1[0] - P0[0]) / d
    P2[1] = P0[1] + a * (P1[1] - P0[1]) / d

    i1x = P2[0] + h * (P1[1] - P0[1]) / d
    i1y = P2[1] - h * (P1[0] - P0[0]) / d
    i2x = P2[0] - h * (P1[1] - P0[1]) / d
    i2y = P2[1] + h * (P1[0] - P0[0]) / d

    i1 = (i1x, i1y)
    i2 = (i2x, i2y)

    return [i1, i2]


def intersect_circles_with_error(P0, P1, r0, r1):
    """
    Call this function when you're sure that both circles intersect, but due to
    error variation, the intersection can be null
    """
    if len(P0) != 2 or len(P1) != 2:
        raise TypeError("P0 and P1 must be 2-tuples")
    d = dist(P0, P1)

    # Make r0 <= r1
    if r0 > r1:
        r0, r1 = r1, r0
        P0, P1 = P1, P0

    # Fix error
    if d > r0 + r1:
        r0 += d - (r0+r1)
        r0 += 0.001     # Fix to accuracy problems
    elif d < r1 - r0:
        r0 += r1 - r0 - d
        r0 += 0.001     # Fix to accuracy problems
    elif d == 0:
        raise Exception("This should never happen")
    return intersect_circles(P0, P1, r0, r1)



# This is to be used out there
def triangulate_position(flags, prev_position=None):
    if prev_position is None:
        print "I don't have previous position to work with"
        raise Exception("This should never happen")
    if len(flags) < 2:
        print "WARNING: I cannot see enough flags to determine position"
        return prev_position

    l = flags.items()
    l.sort(key=lambda x: x[1].distance)

    list_of_points = []
    for i in range(len(l)):
        for j in range(i+1, len(l)):
            i1, i2 = intersect_circles_with_error(flag_positions[l[i][0]],
                                                  flag_positions[l[j][0]],
                                                  l[i][1].distance, l[j][1].distance)
            list_of_points.append(closer_point(prev_position, [i1, i2]))
    return mean_points(list_of_points)


# This is to be used out there
def calculate_orientation(flags, position):
    if len(flags) == 0:
        print "WARNING: I cannot see enough flags to determine orientation"
        return None
    l = flags.items()
    l.sort(key=lambda x: x[1].distance)
    idx = 0
    ref = position
    while dist(position, ref) < 5 and idx < len(l):
        ref = flag_positions[l[idx][0]]
        idx += 1
    return -angle_to(position, ref) - l[0][1].direction


if __name__ == "__main__":
    ip = intersect_circles
    ipe = intersect_circles_with_error

    print "Intersection:", ip((0,0), (1, 0), 2, 2)
    print "Wholly inside:", ip((0,0), (1, 0), 5, 2)
    print "Single-point edge collision:", ip((0,0), (4, 0), 2, 2)
    print "No collision:", ip((0,0), (5, 0), 2, 2)
    print "Intersection with error:", ipe((2,0), (1,0), 2, 0.9)
