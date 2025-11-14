import numpy as np
import pygame

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
    
    # Convert coords into complex
    complex_data = x_data + 1j * y_data
    
    # FFT
    fourier = np.fft.fft(complex_data) / N 
    
    coefficients = []
    for i in range(-n_harmonics // 2, n_harmonics // 2 + 1):
        if i < 0: 
            coef = fourier[N + i]
        elif i == 0:
            coef = fourier[0]
        else:
            coef = fourier[i]
            
        coefficients.append({ 'freq': i, 'amplitude': np.abs(coef), 'phase': np.angle(coef)})
        
    coefficients.sort(key=lambda x: x['amplitude'], reverse=True)
    return coefficients

# Main body
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN and state == 0: 
            state = 1
            continue
        
        if event.type == pygame.MOUSEBUTTONDOWN and state == 1:
            n = len(x_data)        
            coefficients = calculate_fourier_coefficients(np.array(x_data) - width // 2, np.array(y_data) - height // 2, n)
            state = 2    
        
    if state == 1:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        pygame.draw.circle(screen, WHITE, (mouse_x, mouse_y), 1)
        x_data.append(mouse_x)
        y_data.append(mouse_y)
        
        
    if state == 2:      
     
        screen.fill(BLACK)    
       
        m = -1 
        for coef in coefficients: 
            m += 1
            
            radius = coef['amplitude']
            phase = coef['phase']
            frequency = coef['freq']
            
            angle = frequency * t + phase 
            
            # First circle case
            if m == 0:
                globals()[f'position_{m}'] = (radius*np.cos(angle) + width // 2, 
                                              radius*np.sin(angle) + height // 2)
                
                pygame.draw.circle(screen, BLUE, (width // 2, height // 2) , radius, 1)
            
            # Other circles     
            else:
                globals()[f'position_{m}'] = (radius*np.cos(angle) + globals()[f'position_{m-1}'][0], 
                                              radius*np.sin(angle) + globals()[f'position_{m-1}'][1])
                
                pygame.draw.circle(screen, BLUE, globals()[f'position_{m-1}'], radius, 1)
            
                
                
        for i in range(len(coefficients)):
            
            # First circle case
            if i == 0:
                pygame.draw.circle(screen, RED, globals()[f'position_{i}'], 3)
                pygame.draw.line(screen, WHITE, (width // 2, height // 2), globals()[f'position_{i}'], 1)
            
            # Other circles
            else:
                pygame.draw.circle(screen, RED, globals()[f'position_{i}'], 3)
                pygame.draw.line(screen, WHITE, globals()[f'position_{i-1}'], globals()[f'position_{i}'], 1)
           
            
                    
        for i in range(len(x_data)):
            pygame.draw.circle(screen, WHITE, (x_data[i], y_data[i]), 1)
            
        for i in range(len(trace)-1):
            pygame.draw.line(screen, WHITE, trace[i], trace[i+1], 1)
        
        trace.append(globals()[f'position_{n}']) 
    
        t += 2 * np.pi / len(x_data)  
    
    pygame.display.flip()
    pygame.time.Clock().tick(frame_rate)

pygame.quit()