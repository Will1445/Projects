import numpy as np
import random
from matplotlib import pyplot as plt
from tqdm import tqdm

Len_x = 10
Len_y = 10
N = Len_x*Len_y
thresh = 0.09
random.seed(5)
total_values = 0

# Temperature input values
min_temp = -185
max_temp = -175
temp_step = 0.1
temp_crit = -180.15


# Monte Carlo optimisation function for aligning Cooper pairs 
def Cooper_optimise():
    for j in range(N):
        rand_index = random.randint(0, N-1)
        phase_old = theta_array[rand_index] 

        d_theta = (random.uniform(0, rand_lim)-0.5)
        phase_new = phase_old + d_theta


        Energy_diff = 0
        for j in range(4):
            xy_site = xy_array[rand_index][j]  
            cos_old = np.cos(phase_old - theta_array[xy_site])
            cos_new = np.cos(phase_new - theta_array[xy_site])
            Energy_diff = Energy_diff - (cos_new - cos_old)

       # If the change in energy (phase angle) reduces the total energy then the move it accepted
        if Energy_diff <= 0 or (random.random() < np.exp(-Energy_diff/thresh)):
            theta_array[rand_index] = phase_new
            
            # Finding the difference between the new phase value and its neighbours 
            difference = 0
            for j in range(4):
                xy_site = xy_array[rand_index][j] 
                change = np.cos(phase_new) - np.cos(theta_array[xy_site])
                difference = difference + change 

            # Changing the current array of differences to include the new difference
            difference_array[rand_index] = abs(difference)
            difference_average = sum(difference_array)/N
            
            # Appending an array of the total difference across all pairs and neighbours
            values.append(difference_average)
            
temp_range = abs(int((max_temp-min_temp)/temp_step))

temp_axis = np.arange(min_temp, max_temp+temp_step, temp_step)
temp_axis2 = np.arange(min_temp, max_temp+temp_step, temp_step)
count_axis = []
count_axis2 = []
count_axis3 = []

for k in tqdm(range(temp_range + 1), desc="Progress", unit="iteration", ncols=150, colour='#1ec0e1'):
    
    ####################################################################################
    
    # This section, marked by long lines of # is pulled from a Github simulation and is used to describe neighbouring array values
    # Link: https://github.com/KonradStanski/superConductor
    
    x_array = np.zeros(N)
    y_array = np.zeros(N)
    for i in range(N):
        x = i % Len_x
        y = (i-x)/Len_x
        x_array[i] = x
        y_array[i] = y

    theta_array = np.zeros(N)

    for i in range(N):
        r = random.random()
        theta_array[i] = 2*np.pi*r

    xy_array = np.zeros((N, 4), dtype='int')

    for i in range(N):
        # Right neighbour
        if x_array[i] != Len_x-1: 
            xy_array[i][0] = i+1
        else:  
            xy_array[i][0] = i+1-Len_x

        # Up neighbour
        if y_array[i] != Len_y-1:  
            xy_array[i][1] = i+Len_x
        else:  # correct the upper edge
            xy_array[i][1] = i+Len_x-N

        # Left neighbour
        if x_array[i] != 0: 
            xy_array[i][2] = i-1
        else: 
            xy_array[i][2] = i-1+Len_x

        # Down neighbour
        if y_array[i] != 0:  
            xy_array[i][3] = i-Len_x
        else:  
            xy_array[i][3] = i-Len_x+N 
            
    ####################################################################################
    
    # Establishing the arrays which will later be modified by the function, these must be reset for each temp iteration
    values = []
    difference_array = np.zeros(N)
    
    temp = min_temp+k*temp_step
    
    # Determining the range for the random float of phase angles the pairs can move to 
    # This is determinied by an equation of similar form to the penetration depth of a magnetic field for a given superconductor 
    if temp <= temp_crit:
        rand_lim = 0.5*(-0.1*temp+temp_crit/10)**(1/7) + 0.5
        
    else:
        rand_lim = -0.5*(0.1*temp-temp_crit/10)**(1/7) + 0.5
    
    # Number of times the optimisation function will run, lower to improve runtimes greatly
    for i in range(5): 
        Cooper_optimise()
    total_values = total_values + len(values)
    ######################## Uncomment this to view the plots of each temperature     
    # plt.plot(values)
    # plt.title(temp)
    # plt.show()
    ########################  
    
    count_axis.append(len(values)/10000) # Dsiplays the data by their total amount per temperature (same as n0. of successful switches)
    
#     count_axis2.append(np.sum(np.array(values)<0.5)/len(values)) # Displays the data by the propotion of values below a threshold
   
#     found = False # Displays the data by the number of values below a threshold, removes data not below the threshold
#     for i in range(len(values)-1000):
#         if values[i+1000]<=0.6:
#             count_axis3.append(i+1000)
#             found = True
#             break
#     if found == False:
#         count_axis3.append(0)
      
# index_invalid = []
# for i in range(len(temp_axis2)):
#     if count_axis3[i] == 0:
#         print("FOUND")
#         index_invalid.append(i)
        
# count_axis3 = np.delete(count_axis3,index_invalid)
# temp_axis2 = np.delete(temp_axis2,index_invalid)
    

plt.plot(temp_axis,count_axis, label="Alignment Curve")  
# plt.plot(temp_axis,count_axis2, label="Alighment Curve")  
# plt.plot(temp_axis2,count_axis3, label="Alighment Curve")  

plt.axvline(x=temp_crit, color='red', linestyle='--', label="Critical Temperature")
plt.xlabel("Temp (°C)")
plt.ylabel("Relative alignment")
plt.title("Relative alignment with temperature")
plt.legend()
plt.show()
print(total_values)




