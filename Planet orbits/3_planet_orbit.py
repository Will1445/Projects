import pygame
import numpy as np
import math

width=1300
height=800
dt=1
G = 6.67e-11
m1 = 1.989e29
m2 = 1.989e29
m3 = 50.9722e31

pygame.init()
screen = pygame.display.set_mode((width, height))

# Each pixel = 1 billion meters
B = 1e9

planet_1_pos_x = 600
planet_1_pos_y = 400
planet_1_rad_vel_x = 0
planet_1_rad_vel_y = 0
planet_1_tan_vel_x = 0
planet_1_tan_vel_y = 0.2

planet_2_pos_x = 700
planet_2_pos_y = 400
planet_2_rad_vel_x = 0
planet_2_rad_vel_y = 0
planet_2_tan_vel_x = -0.3
planet_2_tan_vel_y = -0.4

planet_3_pos_x = 650
planet_3_pos_y = 500
planet_3_rad_vel_x = 0
planet_3_rad_vel_y = 0
planet_3_tan_vel_x = 0.4
planet_3_tan_vel_y = -0.2

planet_1_dotted_positions = []
planet_2_dotted_positions = []
planet_3_dotted_positions = []

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

font = pygame.font.Font(None, 36)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
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
   
        
        
    
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()