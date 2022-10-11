# search.py
# ---------------
# Licensing Information:  You are free to use or extend this projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to the University of Illinois at Urbana-Champaign
#
# Created by Jongdeog Lee (jlee700@illinois.edu) on 09/12/2018

"""
This file contains search functions.
"""
# Search should return the path and the number of states explored.
# The path should be a list of tuples in the form (alpha, beta, gamma) that correspond
# to the positions of the path taken by your search algorithm.
# Number of states explored should be a number.
# maze is a Maze object based on the maze from the file specified by input filename
# searchMethod is the search method specified by --method flag (bfs,astar)
# You may need to slight change your previous search functions in MP1 since this is 3-d maze

from collections import deque
import heapq

from state import MazeState

# Search should return the path and the number of states explored.
# The path should be a list of MazeState objects that correspond
# to the positions of the path taken by your search algorithm.
# Number of states explored should be a number.
# maze is a Maze object based on the maze from the file specified by input filename
# searchMethod is the search method specified by --method flag (astar)
# You may need to slight change your previous search functions in MP2 since this is 3-d maze
def search(maze, searchMethod):
    return {
        "astar": astar,
    }.get(searchMethod, [])(maze)

def astar(maze, ispart1=False):
    """
    This function returns an optimal path in a list, which contains the start and objective.

    @param maze: Maze instance from maze.py
    @param ispart1:pass this variable when you use functions such as getNeighbors and isObjective. DO NOT MODIFY THIS
    @return: a path in the form of a list of MazeState objects
    """
    # Your code here

    starting_state = maze.getStart()

    visited_states = {starting_state: (None, 0)}
    # NOTE: states are ordered because the __lt__ method of AbstractState is implemented
    frontier = []
    heapq.heappush(frontier, starting_state)
    
    # TODO(III): implement the rest of the best first search algorithm
    # HINTS:
    #   - add new states to the frontier by calling state.get_neighbors()
    #   - check whether you've finished the search by calling state.is_goal()
    #       - then call backtrack(visited_states, state)...
    # Your code here ---------------
    
    if len(frontier) == 0: # When there are no valid neighbors...
        return []

    goal_reached = False
    goal = None
    state = None
    
    while (not goal_reached or not frontier[0].is_goal()) and len(frontier) != 0:
        state = heapq.heappop(frontier)
        if state.is_goal():
            goal_reached = True
            goal = state
            heapq.heappush(frontier, state)
        
        nbrs = state.get_neighbors(ispart1)
        for nbr in nbrs:
            # Update distance to state if state can be reached more quickly
            if nbr in visited_states.keys() and nbr.dist_from_start < visited_states[nbr][1]:
                heapq.heappush(frontier, nbr)
                visited_states[nbr] = (state, nbr.dist_from_start)
            elif nbr not in visited_states.keys():
                heapq.heappush(frontier, nbr)
                visited_states[nbr] = (state, nbr.dist_from_start)
            # else: pass

    if len(frontier) > 0: # if the first item in the frontier is the goal state
        return backtrack(visited_states, goal)

    # if you do not find the goal return an empty list
    return None

# This is the same as backtrack from MP2 -> Do we need to do anything for 3D implementation?
def backtrack(visited_states, current_state):
    path = []
    # Starting at the goal_state, iterate backwards on the best path until parent = None
    state = current_state
    while visited_states[state][0]:
        path.append(state)
        # path.insert(0, state)
        state = visited_states[state][0]

    path.append(state) # insert the initial state
    path.reverse()
    return path