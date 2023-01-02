import json
from json.decoder import JSONDecodeError
from pyproj import Transformer
import sys 
from math import sqrt
from statistics import mean, median
import click


def Pythagoras(x1, y1, x2, y2):
  return float(sqrt((x2 - x1)**2 + (y2 - y1)**2))

# Prompt the user for the paths to the input files
usedefault = input("Do you want to use default geojson files, Write YES (ALL CAPITAL) if you do, else choose your own GeoJson files ")
if usedefault == "YES":
    addresses_path = 'adresy.geojson'
    containers_path = 'kontejnery.geojson'
else:
    print("Enter your paths of your selected files")
    addresses_path = click.prompt('Enter the path to the file with address points', type=click.Path(exists=True, dir_okay=False))
    containers_path = click.prompt('Enter the path to the file with container points', type=click.Path(exists=True, dir_okay=False))



# pyproj transformatos
wgs2jtsk = Transformer.from_crs(4326,5514, always_xy = True)
jtsk2wgs = Transformer.from_crs(5514,4326, always_xy = True)

# variables
values = [] 
distance = None
distance_check = None
closest_bin = None
distance_variable = None


# opens the files and tries for errors 
try:
    with open (addresses_path, 'r', encoding="utf-8") as adresy: 
        data_addresess = json.load(adresy)
except FileNotFoundError:
    sys.exit("Input file does not exist, check if your file is named properly")
except IOError:
    sys.exit("Contents of adresy is unrecognizeable, configurate the file so the program can read it.")
except PermissionError:
    sys.exit("Program does not have a permission to access the input file")
except JSONDecodeError:
    sys.exit("Input file is not valid")


try:
    with open (containers_path, 'r' , encoding="utf-8") as kontejnery: 
        data_kontejnery = json.load(kontejnery)
except FileNotFoundError:
    sys.exit("Input file does not exist, check if your file is name properly")
except IOError:
    sys.exit("Contents of data_adresy is unrecognizeable, configurate the file so the program can read it.")
except PermissionError:
    sys.exit("Program does not have a permission to access the input file")
except JSONDecodeError:
    sys.exit("Input file is not valid")

# descriptive stats before the main code begins 
print("Number of loaded containers is: {}".format(len(data_kontejnery["features"])))
print("Number of loaded adresses is: {}".format(len(data_addresess["features"])) )
print("Loading...")


try:
    #transforms coordinates from wgs to s_jtsk
    for address in data_addresess["features"]:
        s_jtskX = address["geometry"]["coordinates"][0]
        s_jtskY = address["geometry"]["coordinates"][1]
        jtsk = wgs2jtsk.transform(s_jtskX,s_jtskY)
        current_adress = ("{} {}" .format(address["properties"]["addr:street"],address["properties"]["addr:housenumber"]) )
        
        # establishes the current container
        for container in data_kontejnery["features"]:
            current_container = container["properties"]["ID"]
            #finds the coordinates of the containers and calculates the distance using pythagoras theorem
            if container["properties"]["PRISTUP"] == "volně":
                co_x = container["geometry"]["coordinates"][0]
                co_y = container["geometry"]["coordinates"][1]
                distance = Pythagoras(jtsk[0] ,jtsk[1] ,co_x , co_y)
                # helps find the furthest container by comparing it to the past values in distance variable 
                if distance_variable == None or distance_variable > distance:
                    distance_variable = distance
                    closest_bin = current_adress
            # containers situated in houses
            elif container["properties"]["PRISTUP"] == "obyvatelům domu":
                if current_adress == container['properties']['STATIONNAME']:
                    distance_variable = 0 
                else: 
                    pass
        # if the containers are further than 10000 meters then the program stops 
        if distance_variable > 10000:
            raise Exception("Containers are way too far away")
        # at the end of each cycle the program creaes new feature for closest container
        address["properties"]["closest_bin"] = round(distance_variable) 
        address["properties"]["container"] = closest_bin
        distance_variable = None
        values.append(address)
        
except KeyError:
    sys.exit("Files is missing required attributes")
# makes another file with distances and adresses joined and its dumped there by using the values list 
with open("adresy_kontejnery.geojson","w", encoding="utf-8") as out:
    json.dump(values, out, ensure_ascii = False, indent = 2)

distances = [adress["properties"]["closest_bin"] for adress in data_addresess["features"]]

# finds the adress with the furthest distance 
find_index = (distances.index(max(distances)))

# results
max_distance = max(distances)
address = data_addresess["features"][find_index]["properties"]["addr:street"]
hn = data_addresess["features"][find_index]["properties"]["addr:housenumber"]
print("Loaded")
print("Average: {}".format(round(mean(distances),1)))        
print("Median: {}".format(round(median(distances),1)))
print("Furthest distance from a container is {} m, at {} {}".format(max_distance,address,hn))




