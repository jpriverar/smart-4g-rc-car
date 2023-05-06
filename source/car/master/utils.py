def get_config_file_commands(file_path):
    commands = []
    config_file = open(file_path, 'r')
    
    for line in config_file:
        command = line.strip()
        if not command.startswith("#") and command != "":
            commands.append(command)
    return commands

def get_current_configuration(messenger):
    configuration_values = {}
    
    command_param_pairs = [("Sx", "STEER_MAX"),
                           ("Sr", "STEER_CENTER"),
                           ("Sn", "STEER_MIN"),
                           ("Px", "PAN_MAX"),
                           ("Pr", "PAN_CENTER"),
                           ("Pn", "PAN_MIN"),
                           ("Tx", "TILT_MAX"),
                           ("Tr", "TILT_CENTER"),
                           ("Tn", "TILT_MIN"),
                           ("Dg", "DRIVE_MAX_POWER")]
    
    for command, param in command_param_pairs:
        messenger.send_command(command)
        configuration_values[param] = messenger.get_response()
    return configuration_values
    

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