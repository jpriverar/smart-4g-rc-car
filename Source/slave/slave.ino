#include "us_sensor.h"
#include "camera.h"
#include "drive.h"
#include "steer.h"
#include "imu.h"
#include "messenger.h"

// Buffer for incoming messages
String msg;

// Ultrasonic sensor readings
bool frontUsReading = false;
bool frontCollision = false;
float frontStopDist = 10; //cm
bool backUsReading = false;
bool backCollision = false;
float backStopDist = 10; //cm

// IMU Variables
bool readImu = false;  // To start continuous imu readings
double imuReadTime = 100; // 100ms between readings
double imuStartTime;
double imuCurrTime;

void sendUSData(USSensorData data){
  Message msg;
  msg.messageType = 0x01;
  msg.payloadLength = sizeof(data);
  msg.payload = &data;
  sendMsg(&msg);
}

void sendImuData(IMUData data){
  Message msg;
  msg.messageType = 0x02;
  msg.payloadLength = sizeof(data);
  msg.payload = &data;
  sendMsg(&msg);
}

void setup() {
  // Waiting to stablish connection with master
  Serial.begin(115200);
  waitForConnection();

  // Initializing all car components
  driveInit();
  steerInit();
  cameraInit();
  usSensorInit();
  imuInit();

  // Sending signal that all components all initialized
  Serial.println("ready");  
}

void loop() {
  // If there are any incoming messages
  if(Serial.available() >= 3){  //All commands are at least 2 bytes + '\n'
    msg = Serial.readStringUntil('\n');
    //Serial.print("New message received: ");
    //Serial.println(msg);
    parse_message(msg);
  }

  if (frontUsReading){
    USSensorData data = measureFrontDistance();
    sendUSData(data);

    if (frontCollision){
      if (data.distance < frontStopDist) stopDrive();
    }
  }

  if (backUsReading){
    USSensorData data = measureBackDistance();
    sendUSData(data);

    if (backCollision){
      if (data.distance < backStopDist) stopDrive();
    }
  }

  if (readImu){
    if (imuCurrTime - imuStartTime >= imuReadTime){
      IMUData data = compute6dof();
      sendImuData(data);

      imuStartTime = millis();
    }
    imuCurrTime = millis();
  }
}

void help(){
  Serial.println(F("|---------------------COMMAND SYNTAX---------------------|"));
  Serial.println(F("  {COMMAND}{NUMERICAL VALUE TO PASS THE COMMAND}          "));
  Serial.println(F("  SS130 - Will set the steer direction value to 130°      "));
  Serial.println();
  Serial.println(F("|------------------DIRECTION COMMANDS--------------------|"));
  Serial.println(F("  SG - Get the current steer direction                    "));
  Serial.println(F("  SC - Change steer direcion in a range between 0-255     "));
  Serial.println(F("  SI - Increase the steer direction                       "));
  Serial.println(F("  SD - Decrease the steer direction                       "));
  Serial.println(F("  SC - Center the steer direction                         "));
  Serial.println(F("  SM - Set steer direction max endstop                    "));
  Serial.println(F("  Sm - Set steer direction min endstop                    "));
  Serial.println(F("  Sc - Set steer direction center                         "));
  Serial.println();
  Serial.println(F("|-------------------CAMERA COMMANDS----------------------|"));
  Serial.println(F("  PG - Get the current cam pan angle                      "));
  Serial.println(F("  PS - Set camera pan angle in a range between 0-255      "));
  Serial.println(F("  PI - Increase camera pan angle                          "));
  Serial.println(F("  PD - Decrease camera pan angle                          "));
  Serial.println(F("  PC - Center the camera pan angle                        "));
  Serial.println(F("  PM - Set camera pan angle max endstop                   "));
  Serial.println(F("  Pm - Set camera pan angle min endstop                   "));
  Serial.println(F("  Pc - Set camera pan angle center                        "));
  Serial.println(F("  TG - Get the current cam tilt angle                     "));
  Serial.println(F("  TS - Set camera tilt angle in a range between 0-255     "));
  Serial.println(F("  TI - Increase camera tilt angle                         "));
  Serial.println(F("  TD - Decrease camera tilt angle                         "));
  Serial.println(F("  TC - Center the camera tilt angle                       "));
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
  else if (command == "SG"){Serial.println(getSteer());}
  else if (command == "SS"){setSteerAngle(input_value);}
  else if (command == "SI"){incrementSteerAngle(input_value);}
  else if (command == "SD"){incrementSteerAngle(-input_value);}
  else if (command == "SC"){centerSteerAngle();}
  else if (command == "SM"){steerConfig("max", input_value);}
  else if (command == "Sm"){steerConfig("min", input_value);}
  else if (command == "Sc"){steerConfig("center", input_value);}

  else if (command == "PG"){Serial.println(getPan());}
  else if (command == "PS"){setPanAngle(input_value);}
  else if (command == "PI"){incrementPanAngle(input_value);}
  else if (command == "PD"){incrementPanAngle(-input_value);}
  else if (command == "PC"){centerPanAngle();}
  else if (command == "PM"){cameraConfig("pan max", input_value);}
  else if (command == "Pm"){cameraConfig("pan min", input_value);}
  else if (command == "Pc"){cameraConfig("pan center", input_value);}
  
  else if (command == "TG"){Serial.println(getTilt());}
  else if (command == "TS"){setTiltAngle(input_value);}
  else if (command == "TI"){incrementTiltAngle(input_value);}
  else if (command == "TD"){incrementTiltAngle(-input_value);}
  else if (command == "TC"){centerTiltAngle();}
  else if (command == "TM"){cameraConfig("tilt max", input_value);}
  else if (command == "Tm"){cameraConfig("tilt min", input_value);}
  else if (command == "Tc"){cameraConfig("tilt center", input_value);}

  else if (command == "DP"){changeDrivePower(input_value);}
  else if (command == "DI"){incrementDrivePower(input_value);}
  else if (command == "DD"){incrementDrivePower(-input_value);}
  else if (command == "DS"){stopDrive();}
  else if (command == "DC"){changeDriveDirection(input_value);}
  else if (command == "DM"){driveConfig("max", input_value);}
  
  else if (command == "FO"){Serial.println(measureFrontDistance().distance);}
  else if (command == "FC"){frontUsReading=true;}
  else if (command == "FS"){frontUsReading=false;}
  else if (command == "BO"){Serial.println(measureBackDistance().distance);}
  else if (command == "BC"){backUsReading=true;}
  else if (command == "BS"){backUsReading=false;}

  else if (command == "Ic"){}//Serial.println("Calibration function not implemented yet...");}
  else if (command == "IC"){readImu = true;}
  else if (command == "IS"){readImu = false;}
  else if (command == "IT"){imuReadTime = input_value; imuStartTime = millis();}

  else if (command == "FE"){frontCollision=true;}
  else if (command == "FD"){frontCollision=false;}
  else if (command == "F!"){frontStopDist = input_value;}
  else if (command == "BE"){backCollision=true;}
  else if (command == "BD"){backCollision=false;}
  else if (command == "B!"){backStopDist = input_value;}
  
  else {Serial.println("Unknown command, try again...");}
}
