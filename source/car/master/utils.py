def get_file_commands(file_path):
    commands = []
    commands_file = open(file_path, 'r')
    
    for line in commands_file:
        command = line.strip()
        if not command.startswith("#") and command != "":
            commands.append(command)
            
    commands_file.close()
    return commands

def save_configuration(config, config_file_path):    
    config_file = open(config_file_path, "w")
    
    for param, value in config.items():
        config_file.write(f"{param}:{value}\n")
    config_file.close()

def transform_gps_coordinates(coordinates):
    lat, latDir, lon, lonDir, _, _, _, _, _ = coordinates.split(',')
    
    latDeg = lat[:2]
    latMin = lat[2:]
    lonDeg = lon[:3]
    lonMin = lon[3:]
    
    finalLat = float(latDeg) + (float(latMin)/60)
    finalLon = float(lonDeg) + (float(lonMin)/60)
    if latDir == 'S': finalLat = -finalLat
    if lonDir == 'W': finalLon = -finalLon
    
    return finalLat, finalLon