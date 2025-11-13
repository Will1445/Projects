import pygame
import numpy as np

frame_rate = 60

WHITE = (255,255,255)
BLACK = (0,0,0)
BLUE = (0,0,255)
RED = (255,0,0)

width = 1300
height = 800

x_data = []
y_data = []
trace = []
t = 0
state = 0

pygame.init()
screen = pygame.display.set_mode((width, height))

def calculate_fourier_coefficients(x_data, y_data, n_harmonics):
    N = len(x_data)
    
    # Combine x and y into complex numbers
    complex_data = x_data + 1j * y_data
    
    # Calculate FFT
    fourier = np.fft.fft(complex_data) / N # Scaled by number of data points
    
    # Extract coefficients for positive and negative frequencies
    coefficients = []
    for i in range(-n_harmonics // 2, n_harmonics // 2 + 1):
        if i < 0: 
            coef = fourier[N + i] # Negative frequencies
        elif i == 0:
            coef = fourier[0]
        else:
            coef = fourier[i]  # Positive frequencies
            
        coefficients.append({ # Save outputs to array
            'freq': i,
            'amplitude': np.abs(coef),
            'phase': np.angle(coef)
        })
        
    coefficients.sort(key=lambda x: x['amplitude'], reverse=True) # Sort by amplitude to draw larger circles first (not 'needed')
    return coefficients

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: # Quits the program when pressing close
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN and state == 0: # Sets program to 'take data' state
            state = 1
            continue
        
        if event.type == pygame.MOUSEBUTTONDOWN and state == 1: # Calculates the fourier coefficients from the collected data and sets state to 'play'
            n = len(x_data)        
            coefficients = calculate_fourier_coefficients(np.array(x_data) - width // 2, np.array(y_data) - height // 2, n)
            state = 2    
        
    if state == 1: # Takes the x and y position of the mouse as x and y data for later and plots points when it takes data
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.circle(screen, WHITE, (mouse_x, mouse_y), 1)
        x_data.append(mouse_x)
        y_data.append(mouse_y)
        
        
    if state == 2: # Runs the bulk of the epicyle program        
     
        screen.fill(BLACK)    
       
        m = -1 
        for coef in coefficients: # Gets the radius phase and harmonic freq from the fourier coefficient output for each harmonic
            m += 1
            
            radius = coef['amplitude']
            phase = coef['phase']
            frequency = coef['freq']
            
            angle = frequency * t + phase 
            
            if m == 0: # For the first circle at the centre
                globals()[f'position_{m}'] = (radius*np.cos(angle) + width // 2, 
                                              radius*np.sin(angle) + height // 2) # Finds the position of circle m 
                pygame.draw.circle(screen, BLUE, (width // 2, height // 2) , radius, 1) # Draws the blue outline circles
            else: # For other circles, with their midpoint at the position of the previous circle
                globals()[f'position_{m}'] = (radius*np.cos(angle) + globals()[f'position_{m-1}'][0], 
                                              radius*np.sin(angle) + globals()[f'position_{m-1}'][1]) # Finds the position of circle m 
                pygame.draw.circle(screen, BLUE, globals()[f'position_{m-1}'], radius, 1) # Draws the blue outline circles
            
                
                
        for i in range(len(coefficients)):
            if i == 0: # For the first circle
                pygame.draw.circle(screen, RED, globals()[f'position_{i}'], 3) # Plots the circle with its moving position
                pygame.draw.line(screen, WHITE, (width // 2, height // 2), globals()[f'position_{i}'], 1) # Plots the 'arm' on each circle
            else: # For other circles
                pygame.draw.circle(screen, RED, globals()[f'position_{i}'], 3) # Plots the circle with its moving position
                pygame.draw.line(screen, WHITE, globals()[f'position_{i-1}'], globals()[f'position_{i}'], 1) # Plots the 'arm' on each circle
           
            
                    
        for i in range(len(x_data)): # Draws the data onto the screen 
            pygame.draw.circle(screen, WHITE, (x_data[i], y_data[i]), 1)
            
        for i in range(len(trace)-1): # Plots the points in the trace to plot the line for the overall image
            pygame.draw.line(screen, WHITE, trace[i], trace[i+1], 1)
        
        trace.append(globals()[f'position_{n}']) # Takes the position of the outer circle as the outline of the image
    
        t += 2 * np.pi / len(x_data) # Increments time within 2pi, scaled with the total amount of data     
    
    pygame.display.flip()
    pygame.time.Clock().tick(frame_rate)

pygame.quit()