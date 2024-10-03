import pygame
import numpy as np
import math
import random

random.seed=14

width = 1300
height = 800
dt = 1
G = 1
m = 30

n=9

pygame.init()
screen = pygame.display.set_mode((width, height))
random_colours = []

# Sun
planet_1_pos_x = 650
planet_1_pos_y = 400
planet_1_rad_vel_x = 0
planet_1_rad_vel_y = 0
planet_1_tan_vel_x = 0
planet_1_tan_vel_y = 0

# Mercury 
planet_2_pos_x = 650 + 47.556
planet_2_pos_y = 400
planet_2_rad_vel_x = 0
planet_2_rad_vel_y = 0
planet_2_tan_vel_x = 0
planet_2_tan_vel_y = 0

# Venus
planet_3_pos_x = 650 + 107.6
planet_3_pos_y = 400
planet_3_rad_vel_x = 0
planet_3_rad_vel_y = 0
planet_3_tan_vel_x = 0
planet_3_tan_vel_y = 0

# Earth
planet_4_pos_x = 0
planet_4_pos_y = 400
planet_4_rad_vel_x = 0
planet_4_rad_vel_y = 0
planet_4_tan_vel_x = 0
planet_4_tan_vel_y = 0

# Mars
planet_5_pos_x = 650 + 209.76
planet_5_pos_y = 400
planet_5_rad_vel_x = 0
planet_5_rad_vel_y = 0
planet_5_tan_vel_x = 0
planet_5_tan_vel_y = 0

planet_6_pos_x = 650 + 751.26
planet_6_pos_y = 400
planet_6_rad_vel_x = 0
planet_6_rad_vel_y = 0
planet_6_tan_vel_x = 0
planet_6_tan_vel_y = 0

planet_7_pos_x = 0
planet_7_pos_y = 400
planet_7_rad_vel_x = 0
planet_7_rad_vel_y = 0
planet_7_tan_vel_x = 0
planet_7_tan_vel_y = 0

planet_8_pos_x = 0
planet_8_pos_y = 400
planet_8_rad_vel_x = 0
planet_8_rad_vel_y = 0
planet_8_tan_vel_x = 0
planet_8_tan_vel_y = 0

planet_9_pos_x = 0
planet_9_pos_y = 400
planet_9_rad_vel_x = 0
planet_9_rad_vel_y = 0
planet_9_tan_vel_x = 0
planet_9_tan_vel_y = 0


# Creating dotted positions empty arrays 
for i in range(1,n+1):
    globals()[f'planet_{i}_dotted_positions'] = []


BLACK = (0, 0, 0)

font = pygame.font.Font(None, 36)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill(BLACK)
    
    # Seperation between # and # as a scalar
    for i in range(1,n+1):
        for j in range(i+1,n+1):
            globals()[f'seperation_{i}and{j}'] = np.sqrt((globals()[f'planet_{i}_pos_x'] - globals()[f'planet_{j}_pos_x'])**2 + (globals()[f'planet_{i}_pos_y'] - globals()[f'planet_{j}_pos_y'])**2)
       
    # Angle from # to #                                                                                                                               
    for i in range(1,n+1):
        for j in range(i+1,n+1):
            globals()[f'angle_{i}and{j}'] = math.atan2(-globals()[f'planet_{i}_pos_y'] + globals()[f'planet_{j}_pos_y'], globals()[f'planet_{i}_pos_x'] - globals()[f'planet_{j}_pos_x'])
            globals()[f'angle_{j}and{i}'] = globals()[f'angle_{i}and{j}'] + np.pi
    
    # Acceleration of # caused by #
    for i in range(1,n+1):
        for j in range(i+1,n+1):
            globals()[f'planet_{i}_acceleration_{j}'] = (G*m)/globals()[f'seperation_{i}and{j}']**2
            globals()[f'planet_{j}_acceleration_{i}'] = (G*m)/globals()[f'seperation_{i}and{j}']**2
            
    # Summing accelerations from all other planets for planet # in the x direction        
    for i in range(1,n+1):
        temp = 0
        for j in range(1,n+1):
            if i != j:
                temp = temp + globals()[f'planet_{i}_acceleration_{j}'] * -np.cos(globals()[f'angle_{i}and{j}'])
        globals()[f'planet_{i}_acceleration_x'] = temp
    
    # Summing accelerations from all other planets for planet # in the y direction    
    for i in range(1,n+1):
        temp = 0
        for j in range(1,n+1):
            if i != j:
                temp = temp + globals()[f'planet_{i}_acceleration_{j}'] * np.sin(globals()[f'angle_{i}and{j}'])
        globals()[f'planet_{i}_acceleration_y'] = temp
    
    # Finding each planets new radial velocity
    for i in range(1,n+1):
        globals()[f'planet_{i}_rad_vel_x'] = globals()[f'planet_{i}_rad_vel_x'] + globals()[f'planet_{i}_acceleration_x'] * dt
        globals()[f'planet_{i}_rad_vel_y'] = globals()[f'planet_{i}_rad_vel_y'] + globals()[f'planet_{i}_acceleration_y'] * dt
   
    # Finding each planets new position
    for i in range(1,n+1):
        globals()[f'planet_{i}_pos_x'] = globals()[f'planet_{i}_pos_x'] + (globals()[f'planet_{i}_rad_vel_x'] + globals()[f'planet_{i}_tan_vel_x']) * dt
        globals()[f'planet_{i}_pos_y'] = globals()[f'planet_{i}_pos_y'] + (globals()[f'planet_{i}_rad_vel_y'] + globals()[f'planet_{i}_tan_vel_y']) * dt
    
    
    # Creating dotted line positions
    
    for i in range(1,n+1):
        globals()[f'planet_{i}_dotted_positions'].append((globals()[f'planet_{i}_pos_x'], globals()[f'planet_{i}_pos_y']))
    
    
    # Drawing objects at new positions
    
    for i in range(1,n+1):
        pygame.draw.circle(screen, (255,0,0), (globals()[f'planet_{i}_pos_x'], globals()[f'planet_{i}_pos_y']), 2.5)
    
    
    # Drawing the dotted lines
    
    for i in range(1,n+1):
        for j in range(0,len(globals()[f'planet_{i}_dotted_positions']), 3):
            pygame.draw.circle(screen, (255,0,0), globals()[f'planet_{i}_dotted_positions'][j][:2], 1)
   

    
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()