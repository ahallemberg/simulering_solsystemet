import json

class Storage: 
    """
    klasse for å lagre data til json fil for å huske simulering state, og å hente ut data igjen
    """
    def __init__(self, path) -> None: # constructor
        self.file_path =  path # file path for stored data 
       
    def get(self) -> str|None:  
        """ 
        henter cache data 
        """
        with open(self.file_path) as f: # åpner fil 
            json_str = f.read() # leser innnhold i fil
            if json_str == "": # hvis innhold er tomt, returner ingenting
                return None 
            else: 
                return json.loads(json_str) # hvis innhold, parse json string og convert til python dictionary og returner 
            
    def update(self, space_objects, time, dt_per_s, zoom, camera_offset) -> None: 
        """
        oppdater data i storage
        """
        space_objects_data_arr = [] # liste for å holde data om space objects
        for space_object in space_objects: # looper igjennom alle space objects
            space_object_data = { # all data som lagres om hver av space_objects 
            "name": space_object.name, # navn
            "x": space_object.x, # x koordinat
            "y": space_object.y, # y koordinat
            "v_x": space_object.v_x, # fartsvektor
            "v_y": space_object.v_y, # fartsvektor
            }
            space_objects_data_arr.append(space_object_data) # appender data til liste
            
        data = { # data som skal lagres
            "space_objects": space_objects_data_arr, # liste med data for hver space_object
            "time": time, # simuleringstid 
            "dt_per_s": dt_per_s, # tidsendring per s 
            "zoom": zoom, # kamera zoom
            "camera_offset": [camera_offset.x, camera_offset.y] # camera offset
        }
        
        with open(self.file_path, "w") as f: # åpner fil i write modus
           json.dump(data, f) # lagrer python dictionary som json i fil 

    def clear(self) -> None: 
        """
        metode for å slette all lagret data
        """
        with open(self.file_path, "w") as f: # åpner fil i write modus
            f.write("") # oppdaterer innhold til tomt 

