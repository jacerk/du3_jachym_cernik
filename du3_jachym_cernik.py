import json
from json.decoder import JSONDecodeError
from pyproj import Transformer
import sys 
from math import sqrt
from statistics import mean, median
import argparse


# args input
parser = argparse.ArgumentParser()

parser.add_argument('-a', type = str)
parser.add_argument('-k', type = str )

args = parser.parse_args()

# function  checks files for errors and then opens them and globals its data so it can be assigned and then passed on 
def check_geojson(filename):
    '''
    This function check files for error and passes data to the variables to be further processed

    Parameters:
    filename -> targeted file 

    Output: 
    - checked file
    - data global

    '''
    global data
    try:
        with open(filename, 'r', encoding="utf-8") as f:
            data = json.load(f)

    except FileNotFoundError:
        sys.exit("Input file does not exist, check if your file is name properly")
    except IOError:
        sys.exit("Contents of input files are unrecognizeable, configurate the file so the program can read it.")
    except PermissionError:
        sys.exit("Program does not have a permission to access the input file")
    except JSONDecodeError:
        sys.exit("Input file is not valid")
    


def pythagoras(x1, y1, x2, y2):
    '''
    This function calculates a distance between two points using pythagoras theorem 

    Parameters: 
    x1 (int) coordinate x of point A
    y1 (int) coordinate y of point A
    x2 (int) coordinate x of point B
    y2 (int) coordinate y of point B

    returns:
    float: distance between two points 

    '''
    return float(sqrt((x2 - x1)**2 + (y2 - y1)**2))



# pyproj transformations
wgs2jtsk = Transformer.from_crs(4326,5514, always_xy = True)
jtsk2wgs = Transformer.from_crs(5514,4326, always_xy = True)

# variables
values = [] 
distance = None
distance_check = None
closest_container = None
distance_variable = None
adresses = None
containers = None

# Opens files, if user started the program with input, input files will be used 

if args.a:
    check_geojson(args.a)
    adresses = data
else:
    check_geojson("adresy.geojson")
    adresses = data
if args.k:
    check_geojson(args.a)
    containers = data
else:
    check_geojson("kontejnery.geojson")
    containers = data


# descriptive stats before the main code begins 
print("Number of loaded containers is: {}".format(len(adresses["features"])))
print("Number of loaded adresses is: {}".format(len(containers["features"])))
print("Loading...")

try:
    #transforms coordinates from wgs to s_jtsk
    for address in adresses["features"]:
        s_jtskX = address["geometry"]["coordinates"][0]
        s_jtskY = address["geometry"]["coordinates"][1]
        jtsk = wgs2jtsk.transform(s_jtskX,s_jtskY)
        current_adress = ("{} {}" .format(address["properties"]["addr:street"],address["properties"]["addr:housenumber"]) )
        
        # establishes the current container
        for container in containers["features"]:
            current_container = container["properties"]["ID"]
            #finds the coordinates of the containers and calculates the distance using pythagoras theorem
            if container["properties"]["PRISTUP"] == "volně":
                co_x = container["geometry"]["coordinates"][0]
                co_y = container["geometry"]["coordinates"][1]
                distance = pythagoras(jtsk[0] ,jtsk[1] ,co_x , co_y)
                # helps find the furthest container by comparing it to the past values in distance variable 
                if distance_variable == None or distance_variable > distance:
                    distance_variable = distance
                    closest_container = current_adress
            # containers situated in houses
            elif container["properties"]["PRISTUP"] == "obyvatelům domu":
                if current_adress == container['properties']['STATIONNAME']:
                    distance_variable = 0 
                else: 
                    pass
        # if the containers are further than 10000 meters then the program exits
        if distance_variable > 10000:
            raise Exception("Containers are way too far away")
            exit()
        # at the end of each cycle the program creaes new feature for closest container
        address["properties"]["closest_container"] = round(distance_variable) 
        address["properties"]["container"] = closest_container
        distance_variable = None
        values.append(address)
       #checks for missing files 
except KeyError:
    sys.exit("Files is missing required attributes")
# makes another file with distances and adresses joined and its dumped there by using the values list 
with open("adresy_kontejnery.geojson","w", encoding="utf-8") as out:
    json.dump(values, out, ensure_ascii = False, indent = 2)

distances = [adress["properties"]["closest_container"] for adress in adresses["features"]]

# finds the adress with the furthest distance 
found_index = (distances.index(max(distances)))

# results
max_distance = max(distances)
address = adresses["features"][found_index]["properties"]["addr:street"]
hn = adresses["features"][found_index]["properties"]["addr:housenumber"]

print("Loaded")
print("Average: {}".format(round(mean(distances),1)))        
print("Median: {}".format(round(median(distances),1)))
print("Furthest distance from a container is {} m, at {} {}".format(max_distance,address,hn))




