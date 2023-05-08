import uuid, random, string

param_command_dict = {"STEER_MAX":"Sx",
                      "STEER_CENTER":"Sr",
                      "STEER_MIN":"Sn",
                      "PAN_MAX":"Px",
                      "PAN_CENTER":"Pr",
                      "PAN_MIN":"Pn",
                      "TILT_MAX":"Tx",
                      "TILT_CENTER":"Tr",
                      "TILT_MIN":"Tn",
                      "DRIVE_MAX_POWER":"Dg"}

def get_command_file_commands(file_path):
    commands = []
    commands_file = open(file_path, 'r')
    
    for line in commands_file:
        command = line.strip()
        if not command.startswith("#") and command != "":
            commands.append(command)
            
    commands_file.close()
    return commands

def get_current_configuration(messenger):
    configuration_values = {}
    
    for param, command in param_command_dict.items():
        messenger.send_command(command)
        configuration_values[param] = messenger.get_response()
        
    return configuration_values

def get_config_file_commands(file_path):
    commands = []
    config_file = open(file_path, 'r')
    
    for line in config_file:
        config_line = line.strip()
        if not config_line.startswith("#") and command != "":
            param, value = config_line.split(":")
            param, value = param.strip(), value.strip()

            commands.append(param_command_dict[param] + str(value))
            
    config_file.close()
    return commands

def save_current_configuration(messenger, config_file_path):
    config = get_current_configuration(messenger)
    
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

def generate_mqtt_client_id():
    # Making a client_id 23 characters long
    mac = str(hex(uuid.getnode()))[2:]
    random_str = "".join(random.choice(string.ascii_letters) for _ in range(11))
    return mac + random_str
