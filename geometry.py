# geometry.py
# ---------------
# Licensing Information:  You are free to use or extend this projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to the University of Illinois at Urbana-Champaign
#
# Created by James Gao (jamesjg2@illinois.edu) on 9/03/2021
# Inspired by work done by Jongdeog Lee (jlee700@illinois.edu)

"""
This file contains geometry functions necessary for solving problems in MP3
"""

from audioop import cross
import math
import numpy as np
from alien import Alien
from typing import List, Tuple

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def does_alien_touch_wall(alien, walls, granularity):
    """Determine whether the alien touches a wall

        Args:
            alien (Alien): Instance of Alien class that will be navigating our map
            walls (list): List of endpoints of line segments that comprise the walls in the maze in the format [(startx, starty, endx, endx), ...]
            granularity (int): The granularity of the map

        Return:
            True if touched, False if not
    """

    # if in ball form, check distance from ball centroid to wall
    if alien.is_circle():
        radius = alien.get_width()
        alien_centroid = alien.get_centroid()
        for wall in walls:
            if point_segment_distance(alien_centroid, ((wall[0], wall[1]), (wall[2], wall[3]))) - radius - (granularity / math.sqrt(2)) <= 0:
                return True
    
    # if in sausage form, check distance from line segment to wall
    else:
        d = alien.get_width()
        alien_line_segment = alien.get_head_and_tail()
        for wall in walls:
            dist_to_center = segment_distance(alien_line_segment, ((wall[0], wall[1]), (wall[2], wall[3]))) - d - (granularity / math.sqrt(2))
            if dist_to_center <= 0:
                return True

    return False

def does_alien_touch_goal(alien, goals):
    """Determine whether the alien touches a goal
        
        Args:
            alien (Alien): Instance of Alien class that will be navigating our map
            goals (list): x, y coordinate and radius of goals in the format [(x, y, r), ...]. There can be multiple goals
        
        Return:
            True if a goal is touched, False if not.
    """

    # if in ball shape, check point to point distance
    if alien.is_circle():
        alien_radius = alien.get_width()
        alien_centroid = alien.get_centroid()
        for goal in goals:
            goal_point = (goal[0], goal[1])
            goal_radius = goal[2]
            centroid_to_goal = distance((goal[0] - alien_centroid[0], goal[1] - alien_centroid[1]))
            if centroid_to_goal - alien_radius - goal_radius <= 0:
                return True
    
    # if in sausage shape, check point to segment distance
    else:
        d = alien.get_width()
        alien_line_segment = alien.get_head_and_tail()
        for goal in goals:
            goal_point = (goal[0], goal[1])
            goal_radius = goal[2]
            segment_to_goal = point_segment_distance(goal_point, alien_line_segment)
            if segment_to_goal - d - goal_radius <= 0:
                return True

    return False

def is_alien_within_window(alien, window, granularity):
    """Determine whether the alien stays within the window
        
        Args:
            alien (Alien): Alien instance
            window (tuple): (width, height) of the window
            granularity (int): The granularity of the map
    """
    gran = granularity / math.sqrt(2)
    # if circle, check whether or not centroid + radius is outside the window
    if alien.is_circle():
        alien_radius = alien.get_width()
        alien_centroid = alien.get_centroid()
        # to the left
        if alien_centroid[0] - alien_radius - gran <= 0:
            return False
        # to the right
        if alien_centroid[0] + alien_radius + gran >= window[0]:
            return False
        # above
        if alien_centroid[1] + alien_radius + gran >= window[1]:
            return False
        # below
        if alien_centroid[1] - alien_radius + gran <= 0:
            return False

    
    elif alien.get_shape() == 'Horizontal':
        d = alien.get_width()
        alien_line_segment = alien.get_head_and_tail()
        # to the left
        if alien_line_segment[1][0] - gran <= 0:
            return False
        # to the right
        if alien_line_segment[0][0] + gran >= window[0]:
            return False
        # above
        if alien.get_centroid()[1] - d - gran <= 0:
            return False
        # below
        if alien.get_centroid()[1] + d + gran >= window[1]:
            return False
        
    
    elif alien.get_shape() == 'Vertical':
        d = alien.get_width()
        alien_line_segment = alien.get_head_and_tail()
        # to the left
        if alien.get_centroid()[0] - d - gran <= 0:
            return False
        # to the right
        if alien.get_centroid()[0] + d + gran >= window[0]:
            return False
        # above
        if alien_line_segment[0][1] - d - gran <= 0:
            return False
        # below
        if alien_line_segment[1][1] + d + gran >= window[1]:
            return False

    return True

def distance(point):
    """Helper function encapsulating the distance formula"""
    return math.sqrt(point[0]**2 + point[1]**2)

def point_segment_distance(point, segment):
    """Compute the distance from the point to the line segment.
    Hint: Lecture note "geometry cheat sheet"

        Args:
            point: A tuple (x, y) of the coordinates of the point.
            segment: A tuple ((x1, y1), (x2, y2)) of coordinates indicating the endpoints of the segment.

        Return:
            Euclidean distance from the point to the line segment.  
    """
    # a = first endpoint
    # b = second endpoint
    # c = point

    ab = (segment[1][0] - segment[0][0], segment[1][1] - segment[0][1])
    ac = (point[0] - segment[0][0], point[1] - segment[0][1])
    dot_ab_ac = ab[0] * ac[0] + ab[1] * ac[1]
    len_ab = distance(ab)
    cos_ab_ac = dot_ab_ac / len_ab

    ba = (segment[0][0] - segment[1][0], segment[0][1] - segment[1][1])
    bc = (point[0] - segment[1][0], point[1] - segment[1][1])
    dot_ba_bc = ba[0] * bc[0] + ba[1] * bc[1]
    len_ba = distance(ba)
    cos_ba_bc = dot_ba_bc / len_ba

    if cos_ab_ac > 0 and cos_ba_bc > 0:
        cross_prod = ab[0] * ac[1] - ab[1] * ac[0]
        return abs(cross_prod / len_ab)

    else:
        return min(distance(ac), distance(bc))


### referencing https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
###
def onSegment(p, q, r):
    if ( (q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and 
           (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
        return True
    return False

### referencing https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
###
# to find the orientation of an ordered triplet (p,q,r)
def orientation(p, q, r):
    # function returns the following values:
    # 0 : Collinear points
    # 1 : Clockwise points
    # 2 : Counterclockwise
    val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y))
    if (val > 0):
        # Clockwise orientation
        return 1
    elif (val < 0):
        # Counterclockwise orientation
        return 2
    else:
        # Collinear orientation
        return 0

### referencing https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
###
def do_segments_intersect(segment1, segment2):
    """Determine whether segment1 intersects segment2.  
    We recommend implementing the above first, and drawing down and considering some examples.
    Lecture note "geometry cheat sheet" may also be handy.

        Args:
            segment1: A tuple of coordinates indicating the endpoints of segment1.
            segment2: A tuple of coordinates indicating the endpoints of segment2.
 
        Return:
            True if line segments intersect, False if not.
    """
    
    p1 = Point(segment1[0][0], segment1[0][1])
    q1 = Point(segment1[1][0], segment1[1][1])
    p2 = Point(segment2[0][0], segment2[0][1])
    q2 = Point(segment2[1][0], segment2[1][1])

    # Find the 4 orientations required for 
    # the general and special cases
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)
  
    # General case
    if ((o1 != o2) and (o3 != o4)):
        return True
  
    # Special Cases
    # p1 , q1 and p2 are collinear and p2 lies on segment p1q1
    if ((o1 == 0) and onSegment(p1, p2, q1)):
        return True
    # p1 , q1 and q2 are collinear and q2 lies on segment p1q1
    if ((o2 == 0) and onSegment(p1, q2, q1)):
        return True
    # p2 , q2 and p1 are collinear and p1 lies on segment p2q2
    if ((o3 == 0) and onSegment(p2, p1, q2)):
        return True
    # p2 , q2 and q1 are collinear and q1 lies on segment p2q2
    if ((o4 == 0) and onSegment(p2, q1, q2)):
        return True
  
    return False


def segment_distance(segment1, segment2):
    """Compute the distance from segment1 to segment2.  You will need `do_segments_intersect`.
    Hint: Distance of two line segments is the distance between the closest pair of points on both.

        Args:
            segment1: A tuple of coordinates indicating the endpoints of segment1.
            segment2: A tuple of coordinates indicating the endpoints of segment2.

        Return:
            Euclidean distance between the two line segments.
    """
    # If segments intersect, minimum distance is 0
    if do_segments_intersect(segment1, segment2):
        return 0
    
    # Assuming that one of the segment's endpoints will be the closest
    dist_1 = point_segment_distance(segment1[0], segment2)
    dist_2 = point_segment_distance(segment1[1], segment2)
    dist_3 = point_segment_distance(segment2[0], segment1)
    dist_4 = point_segment_distance(segment2[1], segment1)

    return min(dist_1, dist_2, dist_3, dist_4)


if __name__ == '__main__':

    from geometry_test_data import walls, goals, window, alien_positions, alien_ball_truths, alien_horz_truths, \
        alien_vert_truths, point_segment_distance_result, segment_distance_result, is_intersect_result

    # Here we first test your basic geometry implementation
    def test_point_segment_distance(points, segments, results):
        num_points = len(points)
        num_segments = len(segments)
        for i in range(num_points):
            p = points[i]
            for j in range(num_segments):
                seg = ((segments[j][0], segments[j][1]), (segments[j][2], segments[j][3]))
                cur_dist = point_segment_distance(p, seg)
                assert abs(cur_dist - results[i][j]) <= 10 ** -3, \
                    f'Expected distance between {points[i]} and segment {segments[j]} is {results[i][j]}, ' \
                    f'but get {cur_dist}'


    def test_do_segments_intersect(center: List[Tuple[int]], segments: List[Tuple[int]],
                                   result: List[List[List[bool]]]):
        for i in range(len(center)):
            for j, s in enumerate([(40, 0), (0, 40), (100, 0), (0, 100), (0, 120), (120, 0)]):
                for k in range(len(segments)):
                    cx, cy = center[i]
                    st = (cx + s[0], cy + s[1])
                    ed = (cx - s[0], cy - s[1])
                    a = (st, ed)
                    b = ((segments[k][0], segments[k][1]), (segments[k][2], segments[k][3]))
                    if do_segments_intersect(a, b) != result[i][j][k]:
                        if result[i][j][k]:
                            assert False, f'Intersection Expected between {a} and {b}.'
                        if not result[i][j][k]:
                            assert False, f'Intersection not expected between {a} and {b}.'


    def test_segment_distance(center: List[Tuple[int]], segments: List[Tuple[int]], result: List[List[float]]):
        for i in range(len(center)):
            for j, s in enumerate([(40, 0), (0, 40), (100, 0), (0, 100), (0, 120), (120, 0)]):
                for k in range(len(segments)):
                    cx, cy = center[i]
                    st = (cx + s[0], cy + s[1])
                    ed = (cx - s[0], cy - s[1])
                    a = (st, ed)
                    b = ((segments[k][0], segments[k][1]), (segments[k][2], segments[k][3]))
                    distance = segment_distance(a, b)
                    assert abs(result[i][j][k] - distance) <= 10 ** -3, f'The distance between segment {a} and ' \
                                                                  f'{b} is expected to be {result[i]}, but your' \
                                                                  f'result is {distance}'

    def test_helper(alien: Alien, position, truths):
        alien.set_alien_pos(position)
        config = alien.get_config()

        touch_wall_result = does_alien_touch_wall(alien, walls, 0)
        touch_goal_result = does_alien_touch_goal(alien, goals)
        in_window_result = is_alien_within_window(alien, window, 0)

        assert touch_wall_result == truths[
            0], f'does_alien_touch_wall(alien, walls) with alien config {config} returns {touch_wall_result}, ' \
                f'expected: {truths[0]}'
        assert touch_goal_result == truths[
            1], f'does_alien_touch_goal(alien, goals) with alien config {config} returns {touch_goal_result}, ' \
                f'expected: {truths[1]}'
        assert in_window_result == truths[
            2], f'is_alien_within_window(alien, window) with alien config {config} returns {in_window_result}, ' \
                f'expected: {truths[2]}'


    # Initialize Aliens and perform simple sanity check.
    alien_ball = Alien((30, 120), [40, 0, 40], [11, 25, 11], ('Horizontal', 'Ball', 'Vertical'), 'Ball', window)
    # test_helper(alien_ball, alien_ball.get_centroid(), (False, False, True))

    alien_horz = Alien((30, 120), [40, 0, 40], [11, 25, 11], ('Horizontal', 'Ball', 'Vertical'), 'Horizontal', window)
    test_helper(alien_horz, alien_horz.get_centroid(), (False, False, True))

    alien_vert = Alien((30, 120), [40, 0, 40], [11, 25, 11], ('Horizontal', 'Ball', 'Vertical'), 'Vertical', window)
    # test_helper(alien_vert, alien_vert.get_centroid(), (True, False, True))

    edge_horz_alien = Alien((50, 100), [100, 0, 100], [11, 25, 11], ('Horizontal', 'Ball', 'Vertical'), 'Horizontal',
                            window)
    edge_vert_alien = Alien((200, 70), [120, 0, 120], [11, 25, 11], ('Horizontal', 'Ball', 'Vertical'), 'Vertical',
                            window)

    centers = alien_positions
    segments = walls
    test_point_segment_distance(centers, segments, point_segment_distance_result)
    test_do_segments_intersect(centers, segments, is_intersect_result)
    test_segment_distance(centers, segments, segment_distance_result)

    for i in range(len(alien_positions)):
        test_helper(alien_ball, alien_positions[i], alien_ball_truths[i])
        test_helper(alien_horz, alien_positions[i], alien_horz_truths[i])
        test_helper(alien_vert, alien_positions[i], alien_vert_truths[i])

    # Edge case coincide line endpoints
    test_helper(edge_horz_alien, edge_horz_alien.get_centroid(), (True, False, False))
    test_helper(edge_horz_alien, (110, 55), (True, True, True))
    test_helper(edge_vert_alien, edge_vert_alien.get_centroid(), (True, False, True))

    print("Geometry tests passed\n")