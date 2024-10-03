import pygame
import numpy as np
import math
import random

# Setting random seed and the time limit after which the system is considered stable
random.seed=14
time_limit = 7200

width=1300
height=800
dt=1
G = 6.67e-11
m1 = 1.989e30
m2 = 1.989e30
m3 = 5.9722e24
m4 = 1.989e30

pygame.init()
screen = pygame.display.set_mode((width, height))

# Each pixel = 1 billion meters
B = 1e9

# Setting initial values, planet 1 and 2 are the stars, planet 3 is the orbiting planet

planet_1_pos_x = 600
planet_1_pos_y = 400
planet_1_rad_vel_x = 0
planet_1_rad_vel_y = 0
planet_1_tan_vel_x = 0
planet_1_tan_vel_y = -0.9

planet_2_pos_x = 700
planet_2_pos_y = 400
planet_2_rad_vel_x = 0
planet_2_rad_vel_y = 0
planet_2_tan_vel_x = 0
planet_2_tan_vel_y = 0.9

planet_3_pos_x = 500
planet_3_pos_y = 500
planet_3_rad_vel_x = 0
planet_3_rad_vel_y = 0
planet_3_tan_vel_x = 0.9
planet_3_tan_vel_y = 0

planet_1_dotted_positions = []
planet_2_dotted_positions = []
planet_3_dotted_positions = []

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

count = 0
font = pygame.font.Font(None, 36)

distance_test = True
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
    # Will stop the sim and print the stable values once it has broken out of the loop for count exceeding time limit     
    if count>time_limit:
        running = False 
        print("Stable system found:" )
        print("x pos:",planet_3_pos_x)
        print("y pos:",planet_3_pos_y)
        print("x vel:",planet_3_tan_vel_x)
        print("y vel:",planet_3_tan_vel_y)
        break
        
    
    # Resetting screen to black and resetting count
    screen.fill(BLACK)
    count = 0
    distance_test = True
    
    
    # Resetting values 
    planet_1_pos_x = 600
    planet_1_pos_y = 400
    planet_1_rad_vel_x = 0
    planet_1_rad_vel_y = 0
    planet_1_tan_vel_x = 0
    planet_1_tan_vel_y = -0.9

    planet_2_pos_x = 700
    planet_2_pos_y = 400
    planet_2_rad_vel_x = 0
    planet_2_rad_vel_y = 0
    planet_2_tan_vel_x = 0
    planet_2_tan_vel_y = 0.9
    
    planet_3_rad_vel_x = 0
    planet_3_rad_vel_y = 0
    
    planet_1_dotted_positions = []
    planet_2_dotted_positions = []
    planet_3_dotted_positions = []
    
    # Randomising new values
    planet_3_pos_x = random.randint(0,1300) # Random x initial position
    planet_3_pos_y = random.randint(0,800) # Random y initial position 
    planet_3_tan_vel_x = random.randint(-100,100) /100 # Random x tangential speed between -1 and 1
    planet_3_tan_vel_y = random.randint(-100,100) /100 # Random y tangential speed between -1 and 1
    
    # Printing new randomised values
    print(planet_3_pos_x)
    print(planet_3_pos_y)
    print(planet_3_tan_vel_x)
    print(planet_3_tan_vel_y)
    
       
    # Only continues the simulation if the planet remains on the screen or if the time limit is exceeded
    while distance_test: 
        if planet_3_pos_x > 1300 or planet_3_pos_x < 0 or planet_3_pos_y > 800 or planet_3_pos_y < 0 or count>time_limit:
            distance_test = False
    
        screen.fill(BLACK)
        
        # Seperation between # and # as a scalar
        
        seperation_1and2 = np.sqrt((planet_1_pos_x*B - planet_2_pos_x*B)**2 + (planet_1_pos_y*B - planet_2_pos_y*B)**2)
        seperation_1and3 = np.sqrt((planet_1_pos_x*B - planet_3_pos_x*B)**2 + (planet_1_pos_y*B - planet_3_pos_y*B)**2)
        seperation_2and3 = np.sqrt((planet_2_pos_x*B - planet_3_pos_x*B)**2 + (planet_2_pos_y*B - planet_3_pos_y*B)**2)
        
        # Angle from # to # 
        
        angle_1and2 = math.atan2((-planet_1_pos_y + planet_2_pos_y), (planet_1_pos_x - planet_2_pos_x))
        angle_1and3 = math.atan2((-planet_1_pos_y + planet_3_pos_y), (planet_1_pos_x - planet_3_pos_x))
        angle_2and1 = math.atan2((-planet_2_pos_y + planet_1_pos_y), (planet_2_pos_x - planet_1_pos_x))
        angle_2and3 = math.atan2((-planet_2_pos_y + planet_3_pos_y), (planet_2_pos_x - planet_3_pos_x))
        angle_3and1 = math.atan2((-planet_3_pos_y + planet_1_pos_y), (planet_3_pos_x - planet_1_pos_x))
        angle_3and2 = math.atan2((-planet_3_pos_y + planet_2_pos_y), (planet_3_pos_x - planet_2_pos_x))
        
        # Acceleration of # caused by #
        
        planet_1_acceleration_2 = (G*m2)/seperation_1and2**2
        planet_1_acceleration_3 = (G*m3)/seperation_1and3**2
        
        planet_2_acceleration_1 = (G*m1)/seperation_1and2**2
        planet_2_acceleration_3 = (G*m3)/seperation_2and3**2
        
        planet_3_acceleration_1 = (G*m1)/seperation_1and3**2
        planet_3_acceleration_2 = (G*m2)/seperation_2and3**2
        
        
        
        planet_1_acceleration_x = planet_1_acceleration_2 * -np.cos(angle_1and2) + planet_1_acceleration_3 * -np.cos(angle_1and3)
        planet_1_acceleration_y = planet_1_acceleration_2 * np.sin(angle_1and2) + planet_1_acceleration_3 * np.sin(angle_1and3)
        
        planet_2_acceleration_x = planet_2_acceleration_1 * -np.cos(angle_2and1) + planet_2_acceleration_3 * -np.cos(angle_2and3)
        planet_2_acceleration_y = planet_2_acceleration_1 * np.sin(angle_2and1) + planet_2_acceleration_3 * np.sin(angle_2and3)
        
        planet_3_acceleration_x = planet_3_acceleration_1 * -np.cos(angle_3and1) + planet_3_acceleration_2 * -np.cos(angle_3and2)
        planet_3_acceleration_y = planet_3_acceleration_1 * np.sin(angle_3and1) + planet_3_acceleration_2 * np.sin(angle_3and2)
        
        
       
        planet_1_rad_vel_x = planet_1_rad_vel_x + planet_1_acceleration_x * dt
        planet_1_rad_vel_y = planet_1_rad_vel_y + planet_1_acceleration_y * dt
        planet_2_rad_vel_x = planet_2_rad_vel_x + planet_2_acceleration_x * dt
        planet_2_rad_vel_y = planet_2_rad_vel_y + planet_2_acceleration_y * dt
        planet_3_rad_vel_x = planet_3_rad_vel_x + planet_3_acceleration_x * dt
        planet_3_rad_vel_y = planet_3_rad_vel_y + planet_3_acceleration_y * dt
        
        planet_1_pos_x = planet_1_pos_x + (planet_1_rad_vel_x + planet_1_tan_vel_x)* dt
        planet_1_pos_y = planet_1_pos_y + (planet_1_rad_vel_y + planet_1_tan_vel_y)* dt
        planet_2_pos_x = planet_2_pos_x + (planet_2_rad_vel_x + planet_2_tan_vel_x)* dt
        planet_2_pos_y = planet_2_pos_y + (planet_2_rad_vel_y + planet_2_tan_vel_y)* dt
        planet_3_pos_x = planet_3_pos_x + (planet_3_rad_vel_x + planet_3_tan_vel_x)* dt
        planet_3_pos_y = planet_3_pos_y + (planet_3_rad_vel_y + planet_3_tan_vel_y)* dt
        
        # Creating dotted line positions
        
        planet_1_dotted_positions.append((planet_1_pos_x, planet_1_pos_y))
        planet_2_dotted_positions.append((planet_2_pos_x, planet_2_pos_y))
        planet_3_dotted_positions.append((planet_3_pos_x, planet_3_pos_y))
        
        # Drawing objects at new positions
        
        pygame.draw.circle(screen, YELLOW, (planet_1_pos_x,planet_1_pos_y), 2.5)
        pygame.draw.circle(screen, YELLOW, (planet_2_pos_x, planet_2_pos_y), 2.5)
        pygame.draw.circle(screen, BLUE, (planet_3_pos_x,planet_3_pos_y), 2.5)
        
        # Drawing the dotted lines
        
        for i in range(0, len(planet_1_dotted_positions), 3):  
            pygame.draw.circle(screen, YELLOW, planet_1_dotted_positions[i][:2], 1)
        
        for i in range(0, len(planet_2_dotted_positions), 3):  
            pygame.draw.circle(screen, YELLOW, planet_2_dotted_positions[i][:2], 1)
            
        for i in range(0, len(planet_3_dotted_positions), 3):  
            pygame.draw.circle(screen, BLUE, planet_3_dotted_positions[i][:2], 1)
        
        # Incriment count 
        count = count+1

        pygame.display.flip()
        pygame.time.Clock().tick(60)

pygame.quit()