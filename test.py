import time
# import os


# print(10/5)

# # check anz_samples_left vielfaches von 5000

# print(20 % 5)

# print(10 % 6)
string_output = '#'
string_blank = ' '
duration = 10
start_time = time.time()
previous_time = 0
for i in range(0, duration+1, 1):
    while time.time()-previous_time < 1.0:
        time.sleep(0.001)
    previous_time = time.time()
    print("{:.0f} Sekunden vergangen;    |{}{}|" .format(
        time.time()-start_time, string_output*i, string_blank*(duration-i)), end='\r')


# print(os.path.getsize(file_name)/1024+'KB / '+size+' KB downloaded!', end='\r')
