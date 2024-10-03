import pygame
import numpy as np
import math

width=1300
height=800
dt=1
G = 6.67e-11
m1 = 1.989e30
m2 = 1.989e30

pygame.init()
screen = pygame.display.set_mode((width, height))

# Each pixel = 1 billion meters
B = 1e9

planet_1_pos_x = 500
planet_1_pos_y = 400
planet_1_rad_vel_x = 0
planet_1_rad_vel_y = 0
planet_1_tan_vel_x = 0.5
planet_1_tan_vel_y = -0.2

planet_2_pos_x = 800
planet_2_pos_y = 400
planet_2_rad_vel_x = 0
planet_2_rad_vel_y = 0
planet_2_tan_vel_x = -0.5
planet_2_tan_vel_y = 0.2

planet_1_dotted_positions = []
planet_2_dotted_positions = []

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

font = pygame.font.Font(None, 36)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill(BLACK)
    
    seperation = np.sqrt((planet_1_pos_x*B - planet_2_pos_x*B)**2 + (planet_1_pos_y*B - planet_2_pos_y*B)**2)
    angle_1 = math.atan2((-planet_1_pos_y + planet_2_pos_y), (planet_1_pos_x - planet_2_pos_x))
    angle_2 = math.atan2((-planet_2_pos_y + planet_1_pos_y), (planet_2_pos_x - planet_1_pos_x))
    
    planet_1_acceleration = (G*m2)/seperation**2
    planet_2_acceleration = (G*m1)/seperation**2
    
    
    
    
    planet_1_acceleration_x = planet_1_acceleration * -np.cos(angle_1)
    planet_1_acceleration_y = planet_1_acceleration * np.sin(angle_1)
    planet_2_acceleration_x = planet_2_acceleration * -np.cos(angle_2)
    planet_2_acceleration_y = planet_2_acceleration * np.sin(angle_2)
    
    planet_1_rad_vel_x = planet_1_rad_vel_x + planet_1_acceleration_x * dt
    planet_1_rad_vel_y = planet_1_rad_vel_y + planet_1_acceleration_y * dt
    planet_2_rad_vel_x = planet_2_rad_vel_x + planet_2_acceleration_x * dt
    planet_2_rad_vel_y = planet_2_rad_vel_y + planet_2_acceleration_y * dt
    
    planet_1_pos_x = planet_1_pos_x + (planet_1_rad_vel_x + planet_1_tan_vel_x)* dt
    planet_1_pos_y = planet_1_pos_y + (planet_1_rad_vel_y + planet_1_tan_vel_y)* dt
    planet_2_pos_x = planet_2_pos_x + (planet_2_rad_vel_x + planet_2_tan_vel_x)* dt
    planet_2_pos_y = planet_2_pos_y + (planet_2_rad_vel_y + planet_2_tan_vel_y)* dt
    
    planet_1_dotted_positions.append((planet_1_pos_x, planet_1_pos_y))
    planet_2_dotted_positions.append((planet_2_pos_x, planet_2_pos_y))
    
    pygame.draw.circle(screen, BLUE, (planet_1_pos_x,planet_1_pos_y), 2.5)
    pygame.draw.circle(screen, RED, (planet_2_pos_x, planet_2_pos_y), 2.5)
    
    for i in range(0, len(planet_1_dotted_positions), 3):  
        pygame.draw.circle(screen, BLUE, planet_1_dotted_positions[i][:2], 1)
    
    for i in range(0, len(planet_2_dotted_positions), 3):  
        pygame.draw.circle(screen, RED, planet_2_dotted_positions[i][:2], 1)
   
        
        
    
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()