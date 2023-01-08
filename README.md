# du3_jachym_cernik

This script processes and analyzes data from GeoJSON files containing information about address points and containers.
Its final result is to calculate the distance between the points and further process it. 
The program used json, pyproj, sys, math, statistics and argparse modules. 

command to run: 

python du3_jachym_cernik.py [-a <address_points_file>] [-k <containers_file>]

if the files in repositary are installed then input files are not needed for the start 

The program starts with receiving two input Geojson files(containers, addresses) containing location data and other metadata. If the user does not start the program with input files and downloads the files in the repository then the program will run with default files from the repository. Firstly the program determines if the user has used their own data or not. After its inputs are determined the filenames are sent to a function called check_geojson(filename). This function checks files for errors and loads its data into the 'data' global variable. If an error is encountered the program raises an exception and the program ends. Global data are caught by variables(containers, addresses) underneath the if statements that were setting the inputs. 
	Now when the new variables hold the data for the Geojson files the main block of code starts. Before the program starts try is used to determine if the file is not empty. At first, the address coordinates of input files are transformed using the pyproj transformator and the coordinates are stored. Then the program iterates through each container in the input files and with that it also calculates the distances between containers and addresses using a pythagoras function. The distance is then sorted into a distance variable which is pushed to be further processed. The program evaluates if the container is not within the address, if so, then the program will count it as 0 meters away. The program sets a threshold for the maximum distance that would exit the program in case of a distance being more than 10000 meters.  
`	After the main block container info and distances are attached to new metadata regarding the id of the closest container and its distance. Data from addresses and containers together with calculated data is then dumped into new Geojson files. Then the distance data is appended to a list called values and that is later on used to find the furthest container from a single address and also to calculate descriptive stats. 

