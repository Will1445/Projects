import pygame
import numpy as np
import random

random.seed=14
frame_rate = 60
width = 1300
height = 800
dt = 1
BLACK = (0,0,0)
GREEN = (0,255,0)
GREY = (50,50,50)
BLUE = (0,0,255)
YELLOW = (255,255,0)

frame_count = 0
plane_1_desired_heading = 0
plane_1_heading_change = 0
initial_heading_set = False
plane_1_heading_changing = False
plane_1_predict_path = []

pygame.init()
screen = pygame.display.set_mode((width, height))

pygame.font.init()
font = pygame.font.Font(None, 18)


plane_1_distance = random.randint(370,400)
plane_1_theta = random.uniform(0, 2 * np.pi)

plane_1_x = width/2 + plane_1_distance * np.cos(plane_1_theta)
plane_1_y = height/2 + plane_1_distance * np.sin(plane_1_theta)

def get_heading(theta):
    x_velocity = -2 * np.cos(theta)
    y_velocity = -2 * np.sin(theta)
    
    heading_rad = np.arctan2(y_velocity, x_velocity)
    heading_degrees = np.degrees(heading_rad)
    
    if heading_degrees < 0:
        heading_degrees += 360
        
    heading_degrees_adjust = round(heading_degrees) + 90
    
    if  heading_degrees_adjust > 360:
        heading_degrees_adjust -= 360
    
    return heading_degrees_adjust



running = True
while running:
    screen.fill(BLACK)
    plane_1_predict_path = [(plane_1_x,plane_1_y)]
    
    # Runway 
    pygame.draw.rect(screen, GREEN, (width/2 - 5/2,height/2 - 25/2,5,25), 1)
    
    # Area coverage  
    pygame.draw.circle(screen, GREY, (width/2,height/2), 350, 1)
    
    plane_1_x_velocity = -2 * np.cos(plane_1_theta)
    plane_1_y_velocity = -2 * np.sin(plane_1_theta)
    
    
    if frame_count % 60 == 1: # Creates low framerate 
        plane_1_x = plane_1_x + plane_1_x_velocity 
        plane_1_y = plane_1_y + plane_1_y_velocity 
        

    pygame.draw.circle(screen, GREEN, (plane_1_x,plane_1_y), 2) # Plane
    pygame.draw.circle(screen, GREEN, (plane_1_x,plane_1_y), 10, 1) # Outline
    pygame.draw.line(screen, BLUE, (plane_1_x,plane_1_y), (plane_1_x - 20*np.cos(plane_1_theta), plane_1_y - 20*np.sin(plane_1_theta)), 2)
        
    
    # Displaying plane info
    
    
    plane_1_heading_degrees_adjust = get_heading(plane_1_theta)
        
    
    if not initial_heading_set:
       plane_1_desired_heading = plane_1_heading_degrees_adjust
       initial_heading_set = True
   
       
    plane_1_heading_text = font.render(f"Heading {plane_1_heading_degrees_adjust}", True, GREEN)
    screen.blit(plane_1_heading_text, (plane_1_x+10, plane_1_y-20))
                
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and plane_1_heading_changing == False:
                plane_1_heading_change -= 1
                
            elif event.key == pygame.K_RIGHT and plane_1_heading_changing == False:  
                plane_1_heading_change += 1
            
                
            elif event.key == pygame.K_RETURN:
                plane_1_heading_changing = True
                plane_1_desired_heading += plane_1_heading_change
                plane_1_heading_change = 0
                
                if plane_1_desired_heading > 360:
                    plane_1_desired_heading -= 360
                    
                if plane_1_desired_heading < 0:
                    plane_1_desired_heading += 360
            
    if plane_1_heading_changing == False:
        plane_1_desired_heading_text = font.render(f"Target Heading {plane_1_heading_degrees_adjust + plane_1_heading_change}", True, GREEN)
        
        if plane_1_heading_change > 0:
        
            n=0
            while get_heading(plane_1_theta + 0.03*n) < plane_1_heading_degrees_adjust + plane_1_heading_change:
                plane_1_predict_path.append((plane_1_predict_path[-1][0] + -2*np.cos(plane_1_theta + 0.03*n),plane_1_predict_path[-1][1] + -2*np.sin(plane_1_theta + 0.03*n)))
               
                n += 1
                
                   
            for i in range(100):
                plane_1_predict_path.append((plane_1_predict_path[-1][0] + -2*(i/20)*np.cos(plane_1_theta + 0.03*n),plane_1_predict_path[-1][1] + -2*(i/20)*np.sin(plane_1_theta + 0.03*n)))   
            
            
        elif plane_1_heading_change < 0:
            
            m=0
            while get_heading(plane_1_theta + 0.03*m) > plane_1_heading_degrees_adjust + plane_1_heading_change:
                plane_1_predict_path.append((plane_1_predict_path[-1][0] + -2*np.cos(plane_1_theta - 0.03*m),plane_1_predict_path[-1][1] + -2*np.sin(plane_1_theta - 0.03*m)))
               
                m += 1
           
            for i in range(100):
                plane_1_predict_path.append((plane_1_predict_path[-1][0] + -2*(i/20)*np.cos(plane_1_theta - 0.03*m),plane_1_predict_path[-1][1] + -2*(i/20)*np.sin(plane_1_theta - 0.03*m)))   
                
         
        if len(plane_1_predict_path) > 0:
            for i in range(0,len(plane_1_predict_path),3):
                pygame.draw.circle(screen, YELLOW, (plane_1_predict_path[i][0],plane_1_predict_path[i][1]), 2)
    
    
    else:
        plane_1_desired_heading_text = font.render(f"Target Heading {plane_1_desired_heading}", True, GREEN)
        
     

        
    
    
    screen.blit(plane_1_desired_heading_text, (20,20))
            
    if plane_1_desired_heading > plane_1_heading_degrees_adjust: # Right turn
        plane_1_theta += 0.0005
    
    elif plane_1_desired_heading < plane_1_heading_degrees_adjust: # Left turn
        plane_1_theta -= 0.0005
    
    elif plane_1_desired_heading == plane_1_heading_degrees_adjust:
        plane_1_heading_changing = False

            
    
    
    frame_count = frame_count+1    
    pygame.display.flip()
    pygame.time.Clock().tick(frame_rate)

pygame.quit()
