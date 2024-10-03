import pygame
import numpy as np
import math

height=800
width=800
dt=2.5
G = 5
M = 100

pygame.init()
screen = pygame.display.set_mode((height, width))

planet_pos_x = 200
planet_pos_y = 600
planet_rad_vel_x = 0
planet_rad_vel_y = 0
planet_tan_vel_x = 0.1
planet_tan_vel_y = 0.8

planet_dotted_positions = []
orbit_point = (width//2,height//2)

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
    
    seperation = np.sqrt((planet_pos_x - orbit_point[0])**2 + (planet_pos_y - orbit_point[1])**2)
    angle = math.atan2((-planet_pos_y + orbit_point[1]), (planet_pos_x - orbit_point[0]))
    
    planet_acceleration = (G*M)/seperation**2
    planet_acceleration_x = planet_acceleration * -np.cos(angle)
    planet_acceleration_y = planet_acceleration * np.sin(angle)
    
    planet_rad_vel_x = planet_rad_vel_x + planet_acceleration_x * dt
    planet_rad_vel_y = planet_rad_vel_y + planet_acceleration_y * dt
    
    planet_pos_x = planet_pos_x + (planet_rad_vel_x + planet_tan_vel_x)* dt
    planet_pos_y = planet_pos_y + (planet_rad_vel_y + planet_tan_vel_y)* dt
    
    planet_dotted_positions.append((planet_pos_x, planet_pos_y))
    
    pygame.draw.circle(screen, BLUE, (planet_pos_x,planet_pos_y), 5)
    pygame.draw.circle(screen, RED, orbit_point, 5)
    
    for i in range(0, len(planet_dotted_positions), 3):  
        pygame.draw.circle(screen, BLUE, planet_dotted_positions[i][:2], 2)
   
        
        
    
    
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()