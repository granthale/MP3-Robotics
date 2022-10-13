
# transform.py
# ---------------
# Licensing Information:  You are free to use or extend this projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to the University of Illinois at Urbana-Champaign
# 
# Created by Jongdeog Lee (jlee700@illinois.edu) on 09/12/2018

"""
This file contains the transform function that converts the robot arm map
to the maze.
"""
import copy
# from arm import Arm
from maze import Maze
from search import *
from geometry import *
from const import *
from utils import *
import os

def transformToMaze(alien, goals, walls, window, granularity):
    """This function transforms the given 2D map to the maze in MP1.
    
        Args:
            alien (Alien): alien instance
            goals (list): [(x, y, r)] of goals
            walls (list): [(startx, starty, endx, endy)] of walls
            window (tuple): (width, height) of the window

        Return:
            Maze: the maze instance generated based on input arguments.

    """
    # BE CAREFUL! -> check minimum value
    num_x_positions = int(window[0] / granularity + 1)
    num_y_positions = int(window[1] / granularity + 1)

    # # # # Generate ASCII maze # # # #

    # Level 0 = "Horizontal", 1 = "Ball", 2 = "Vertical"
    maze = np.full((num_x_positions, num_y_positions, 3), "%")
    
    # Make a deep copy of alien... (why?)

    alien_start = configToIdx(alien.get_config(), [0,0,0], granularity, alien)
    
    for x in range(num_x_positions):
        for y in range(num_y_positions):
            # Horizontal
            alien2 = copy.deepcopy(alien)
            config = idxToConfig([x, y], [0,0,0], granularity, alien2)
            alien2.set_alien_config([config[0], config[1], "Horizontal"])
            if not is_alien_within_window(alien2, window, granularity) or does_alien_touch_wall(alien2, walls, granularity):
                maze[0][x][y] = "%"
            elif does_alien_touch_goal(alien2, goals):
                maze[0][x][y] = "."
            else:
                maze[0][x][y] = " "
            
            # Ball
            alien2 = copy.deepcopy(alien)
            config = idxToConfig([x, y], [0,0,0], granularity, alien2)
            alien2.set_alien_config([config[0], config[1], "Ball"])
            if not is_alien_within_window(alien2, window, granularity) or does_alien_touch_wall(alien2, walls, granularity):
                maze[1][x][y] = "%"
            elif does_alien_touch_goal(alien2, goals):
                maze[1][x][y] = "."
            else:
                maze[1][x][y] = " "

            #Vertical
            alien2 = copy.deepcopy(alien)
            config = idxToConfig([x, y], [0,0,0], granularity, alien2)
            alien2.set_alien_config([config[0], config[1], "Vertical"])
            if not is_alien_within_window(alien2, window, granularity) or does_alien_touch_wall(alien2, walls, granularity):
                maze[2][x][y] = "%"
            elif does_alien_touch_goal(alien2, goals):
                maze[2][x][y] = "."
            else:
                maze[2][x][y] = " "
            
    # Replace start coordinate in maze with "P"
    shape = 0
    if config[2] == "Ball": shape = 1
    if config[2] == "Vertical": shape = 2
    maze[shape][alien_start[0]][alien_start[1]] = "P"

    # Instantiate Maze object
    gen_maze = Maze(maze, alien, granularity)
    gen_maze.saveToFile(f"./file/gran_{granularity}.txt")

    return gen_maze
    

if __name__ == '__main__':
    import configparser

    def generate_test_mazes(granularities,map_names):
        for granularity in granularities:
            for map_name in map_names:
                try:
                    print('converting map {} with granularity {}'.format(map_name,granularity))
                    configfile = './maps/test_config.txt'
                    config = configparser.ConfigParser()
                    config.read(configfile)
                    lims = eval(config.get(map_name, 'Window'))
                    # print(lis)
                    # Parse config file
                    window = eval(config.get(map_name, 'Window'))
                    centroid = eval(config.get(map_name, 'StartPoint'))
                    widths = eval(config.get(map_name, 'Widths'))
                    alien_shape = 'Ball'
                    lengths = eval(config.get(map_name, 'Lengths'))
                    alien_shapes = ['Horizontal','Ball','Vertical']
                    obstacles = eval(config.get(map_name, 'Obstacles'))
                    boundary = [(0,0,0,lims[1]),(0,0,lims[0],0),(lims[0],0,lims[0],lims[1]),(0,lims[1],lims[0],lims[1])]
                    obstacles.extend(boundary)
                    goals = eval(config.get(map_name, 'Goals'))
                    alien = Alien(centroid,lengths,widths,alien_shapes,alien_shape,window)
                    generated_maze = transformToMaze(alien,goals,obstacles,window,granularity)
                    generated_maze.saveToFile('./mazes/{}_granularity_{}.txt'.format(map_name,granularity))
                except Exception as e:
                    print('Exception at maze {} and granularity {}: {}'.format(map_name,granularity,e))
    def compare_test_mazes_with_gt(granularities,map_names):
        name_dict = {'%':'walls','.':'goals',' ':'free space','P':'start'}
        shape_dict = ['Horizontal','Ball','Vertical']
        for granularity in granularities:
            for map_name in map_names:
                this_maze_file = './mazes/{}_granularity_{}.txt'.format(map_name,granularity)
                gt_maze_file = './mazes/gt_{}_granularity_{}.txt'.format(map_name,granularity)
                if(not os.path.exists(gt_maze_file)):
                    print('no gt available for map {} at granularity {}'.format(map_name,granularity))
                    continue
                gt_maze = Maze([],[],{}, [],filepath = gt_maze_file)
                this_maze = Maze([],[],{},[],filepath= this_maze_file)
                gt_map = np.array(gt_maze.get_map())
                this_map = np.array(this_maze.get_map())
                difx,dify,difz = np.where(gt_map != this_map)
                if(difx.size != 0):
                    diff_dict = {}
                    for i in ['%','.',' ','P']:
                        for j in ['%','.',' ','P']:
                            diff_dict[i + '_'+ j] = []
                    print('\n\nDifferences in {} at granularity {}:'.format(map_name,granularity))    
                    for i,j,k in zip(difx,dify,difz):
                        gt_token = gt_map[i][j][k] 
                        this_token = this_map[i][j][k]
                        diff_dict[gt_token + '_' + this_token].append(noAlienidxToConfig((j,i,k),granularity,shape_dict))
                    for key in diff_dict.keys():
                        this_list = diff_dict[key]
                        gt_token = key.split('_')[0]
                        your_token = key.split('_')[1]
                        if(len(this_list) != 0):
                            print('Ground Truth {} mistakenly identified as {}: {}'.format(name_dict[gt_token],name_dict[your_token],this_list))
                    print('\n\n')
                else:
                    print('no differences identified  in {} at granularity {}:'.format(map_name,granularity))
    ### change these to speed up your testing early on! 
    granularities = [2,5,8,10]
    map_names = ['Test1','Test2','Test3','Test4','NoSolutionMap']
    generate_test_mazes(granularities,map_names)
    compare_test_mazes_with_gt(granularities,map_names)
