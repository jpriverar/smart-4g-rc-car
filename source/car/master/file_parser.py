class FileParser:
    @staticmethod
    def write_cmd_file(cmd_file_path, commands):
        cmd_file = open(cmd_file_path, "w")
        
        for command in commands:
            cmd_file.write(command + "\n")
        cmd_file.close()
        print(f"{cmd_file_path} overwritten.")
    
    @staticmethod
    def write_conf_file(config_file_path, config):    
        config_file = open(config_file_path, "w")
        
        for param, value in config.items():
            config_file.write(f"{param}:{value}\n")
        config_file.close()
        print(f"{config_file_path} overwritten.")
        
    @staticmethod
    def parse_conf_file(config_file_path):
        config = {}
        
        config_file = open(config_file_path, 'r')
        for line in config_file:
            config_line = line.strip()
            if not config_line.startswith("#") and config_line != "":
                param, value = config_line.split(":")
                param, value = param.strip(), value.strip()
                config[param] = int(value)
        config_file.close()
        return config
    
    @staticmethod
    def parse_cmd_file(cmd_file_path):
        commands = []
        commands_file = open(cmd_file_path, 'r')
        
        for line in commands_file:
            command = line.strip()
            if not command.startswith("#") and command != "":
                commands.append(command)
                
        commands_file.close()
        return commands
        
        
    