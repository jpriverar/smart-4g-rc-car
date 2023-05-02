def get_config_file_commands(file_path):
    commands = []
    config_file = open(file_path, 'r')
    
    for line in config_file:
        command = line.strip()
        if not command.startswith("#") and command != "":
            commands.append(command)
    return commands

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
    
