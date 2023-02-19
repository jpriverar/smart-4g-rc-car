#include "us_sensor.h"
#include "camera.h"
#include "drive.h"
#include "steer.h"
#include "imu.h"
#include "messenger.h"

// Buffer for incoming messages
String msg;

// Ultrasonic sensor readings
bool front_us_reading = false;
bool front_collision = false;
float front_stop_dist = 10; //cm
bool back_us_reading = false;
bool back_collision = false;
float back_stop_dist = 10; //cm

void setup() {
  // Waiting to stablish connection with master
  Serial.begin(9600);
  wait_for_connection();

  // Initializing all car components
  us_sensor_init();
  camera_init();
  drive_init();
  steer_init();
  //imu_init();
}

void loop() {
  // If there are any incoming messages
  if(Serial.available()){
    msg = Serial.readStringUntil('\n');
    Serial.print("New message received: ");
    Serial.println(msg);
    parse_message(msg);
  }

  if (front_us_reading){
    double dist = measure_distance("front");
    
    Serial.print("front distance: ");
    Serial.println(dist);

    if (front_collision){
      if (dist < front_stop_dist) stop_drive();
    }
  }

  if (back_us_reading){
    double dist = measure_distance("back");
    
    Serial.print("back distance: ");
    Serial.println(dist);

    if (back_collision){
      if (dist < back_stop_dist) stop_drive();
    }
  }

  /*if (read_imu){
    if (imu_curr_time - imu_start_time >= imu_read_time){
      compute_6dof();
      imu_start_time = millis();
    }
    imu_curr_time = millis();
  }*/
}

void help(){
  Serial.println(F("|---------------------COMMAND SYNTAX----------------------"));
  Serial.println(F("  {COMMAND}{NUMERICAL VALUE TO PASS THE COMMAND}          "));
  Serial.println(F("  SC130 - Will set the steer direction value to 130°   "));
  Serial.println();
  Serial.println(F("|------------------DIRECTION COMMANDS--------------------|"));
  Serial.println(F("  SC - Change steer direcion in a range between 0-255     "));
  Serial.println(F("  SI - Increase the steer direction                       "));
  Serial.println(F("  SD - Decrease the steer direction                       "));
  Serial.println(F("  SM - Set steer direction max endstop                    "));
  Serial.println(F("  Sm - Set steer direction min endstop                    "));
  Serial.println(F("  Sc - Set steer direction center                         "));
  Serial.println();
  Serial.println(F("|-------------------CAMERA COMMANDS----------------------|"));
  Serial.println(F("  PC - Change camera pan angle in a range between 0-255   "));
  Serial.println(F("  PI - Increase camera pan angle                          "));
  Serial.println(F("  PD - Decrease camera pan angle                          "));
  Serial.println(F("  PM - Set camera pan angle max endstop                   "));
  Serial.println(F("  Pm - Set camera pan angle min endstop                   "));
  Serial.println(F("  Pc - Set camera pan angle center                        "));
  Serial.println(F("  TC - Change camera tilt angle in a range between 0-255  "));
  Serial.println(F("  TI - Increase camera tilt angle                         "));
  Serial.println(F("  TD - Decrease camera tilt angle                         "));
  Serial.println(F("  TM - Set camera tilt angle max endstop                  "));
  Serial.println(F("  Tm - Set camera tilt angle min endstop                  "));
  Serial.println(F("  Tc - Set camera tilt angle center                       "));
  Serial.println();
  Serial.println(F("|--------------------DRIVE COMMANDS----------------------|"));
  Serial.println(F("  DP - Drive the motor forward in a range between 0-255   "));
  Serial.println(F("  DI - Increase the drive power                           "));
  Serial.println(F("  DD - Decrease the drive power                           "));
  Serial.println(F("  DC - Change the drive direction 1-forward, 0-backward   "));
  Serial.println(F("  DS - Stop the drive                                     "));
  Serial.println(F("  DM - Set drive maximum allowed power                    "));
  Serial.println();
  Serial.println(F("|----------------ULTRASONIC SENSOR COMMANDS--------------|"));
  Serial.println(F("  FO - Front ultrasonic sensor one shot reading           "));
  Serial.println(F("  FC - Front ultrasonic sensor continuous reading         "));
  Serial.println(F("  FS - Stop front ultrasonic sensor reading               "));
  Serial.println(F("  BO - Back ultrasonic sensor one shot reading            "));
  Serial.println(F("  BC - Back ultrasonic sensor continuous reading          "));
  Serial.println(F("  BS - Stop back ultrasonic sensor reading                "));
  Serial.println();
  Serial.println(F("|----------------------IMU COMMANDS----------------------|"));
  Serial.println(F("  Ic - Calibrate offset values for the imu, takes 5-10m   "));
  Serial.println(F("  IC - Read IMU computed values continuously              "));
  Serial.println(F("  IS - Stop continuous IMU readings                       "));
  Serial.println(F("  IT - Change time between continuous IMU readings        "));
  Serial.println();
  Serial.println(F("|-------------COLLISION DETECTION COMMANDS---------------|"));
  Serial.println(F("  FE - Front side collision detection enabled             "));
  Serial.println(F("  FD - Front side collision detection disabled            "));
  Serial.println(F("  F! - Set front emergecy stop threshold distance         "));
  Serial.println(F("  BE - Back side collision detection enabled              "));
  Serial.println(F("  BD - Back side collision detection disabled             "));
  Serial.println(F("  B! - Set back emergecy stop threshold distance          "));
}

void parse_message(String msg){
  int16_t input_value = -1;
  String command = msg.substring(0,2);

  if (msg.length() > 2) input_value = msg.substring(2).toInt();
  //Serial.println(input_value);
  
  if (msg == "help"){help();}
  else if (command ==  "SC"){change_steer_angle(input_value);}
  else if (command == "SI"){increment_steer_angle(input_value);}
  else if (command == "SD"){increment_steer_angle(-input_value);}
  else if (command == "SM"){steer_config("max", input_value);}
  else if (command == "Sm"){steer_config("min", input_value);}
  else if (command == "Sc"){steer_config("center", input_value);}

  else if (command == "PC"){change_pan_angle(input_value);}
  else if (command == "PI"){increment_pan_angle(input_value);}
  else if (command == "PD"){increment_pan_angle(-input_value);}
  else if (command == "PM"){camera_config("pan max", input_value);}
  else if (command == "Pm"){camera_config("pan min", input_value);}
  else if (command == "Pc"){camera_config("pan center", input_value);}
  
  else if (command == "TC"){change_tilt_angle(input_value);}
  else if (command == "TI"){increment_tilt_angle(input_value);}
  else if (command == "TD"){increment_tilt_angle(-input_value);}
  else if (command == "TM"){camera_config("tilt max", input_value);}
  else if (command == "Tm"){camera_config("tilt min", input_value);}
  else if (command == "Tc"){camera_config("tilt center", input_value);}

  else if (command == "DP"){change_drive_power(input_value);}
  else if (command == "DI"){increment_drive_power(input_value);}
  else if (command == "DD"){increment_drive_power(-input_value);}
  else if (command == "DS"){stop_drive();}
  else if (command == "DC"){change_drive_direction(input_value);}
  else if (command == "DM"){drive_config("max", input_value);}
  
  else if (command == "FO"){Serial.println(measure_distance("front"));}
  else if (command == "FC"){front_us_reading=true;}
  else if (command == "FS"){front_us_reading=false;}
  else if (command == "BO"){Serial.println(measure_distance("back"));}
  else if (command == "BC"){back_us_reading=true;}
  else if (command == "BS"){back_us_reading=false;}

  else if (command == "Ic"){Serial.println("Calibration function not implemented yet...");}
  //else if (command == "IC"){read_imu = true;}
  //else if (command == "IS"){read_imu = false;}
  //else if (command == "IT"){imu_read_time = input_value; imu_start_time = millis();}
  
  else {Serial.println("Unknown command, try again...");}
}
