#include "us_sensor.h"
#include "speedometer.h"
#include "camera.h"
#include "drive.h"
#include "steer.h"
#include "imu.h"
#include "messenger.h"
#include "gearbox.h"

#define LIGHT_PIN A0
#define BUZZER_PIN A1

// Buffer for incoming messages
String msg;

// Ultrasonic sensor readings
double frontUS_lastMeasure;
double frontUS_lastUpdate;
double frontUS_readTime = 50; //50 ms between readings
double frontUS_updateTime = 250;
bool frontUsReading = false;
bool frontCollision = false;
float frontStopDist = 10; //cm

double backUS_lastMeasure;
double backUS_lastUpdate;
double backUS_readTime = 50; // 50 ms between readings
double backUS_updateTime = 250;
bool backUsReading = false;
bool backCollision = false;
float backStopDist = 10; //cm

// IMU Variables
bool readImu = false;  // To start continuous imu readings
double imu_lastMeasure;
double imu_lastUpdate;
double imu_readTime = 100; // 100ms between readings
double imu_updateTime = 500;

// Speed control variables
bool followReference = false;
double PID_lastSample;
double PID_samplePeriod = 1000/3.5014; //3.5014 Hz

// To measure the current time
double currTime;

void setup() {
  // Waiting to stablish connection with master
  Serial.begin(115200);
  waitForConnection();

  // Initializing all car components
  gearboxInit();
  speedometerInit();
  driveInit();
  steerInit();
  cameraInit();
  usSensorInit();
  imuInit();

  pinMode(LIGHT_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  // Sending signal that all components all initialized
  Serial.println("ready");  
}

void loop() {
  // READ ANY NEW INCOMING COMMANDS
  if(Serial.available() >= 3){  //All commands are at least 2 bytes + '\n'
    msg = Serial.readStringUntil('\n');
    parse_message(msg);
  }

  // UPDATING CURRENT TIME
  currTime = millis();

  // FRONT ULTRASONIC SENSOR MEASUREMENT
  if ((frontUsReading) && (currTime - frontUS_lastMeasure >= frontUS_readTime)){
    USSensorData data = measureFrontDistance();

    // Send the Front USS values
    if ((frontUS_updateTime >= 0) && (currTime - frontUS_lastUpdate >= frontUS_updateTime)){
      sendUSSensorData(data);
      frontUS_lastUpdate = millis();
    }
    
    // Collision detection
    if (frontCollision){
      if ((data.distance < frontStopDist) && (data.distance > 0)) stopDrive();
    }
    
    frontUS_lastMeasure = millis();
  }

  // BACK ULTRASONIC SENSOR MEASUREMENT
  if ((backUsReading) && (currTime - backUS_lastMeasure >= backUS_readTime)){
    USSensorData data = measureBackDistance();

    // Send the Front USS values
    if ((backUS_updateTime >= 0) && (currTime - backUS_lastUpdate >=backUS_updateTime)){
      sendUSSensorData(data);
      backUS_lastUpdate = millis();
    }

    // Collision detection
    if (backCollision){
      if ((data.distance < backStopDist) && (data.distance > 0)) stopDrive();
    }
    
    backUS_lastMeasure = millis();
  }

  // IMU MEASUREMENT
  if ((readImu) && (currTime - imu_lastMeasure >= imu_readTime)){
    IMUData data = compute6dof();

    // Send the IMU values
    if ((imu_updateTime >= 0) && (currTime - imu_lastUpdate >= imu_updateTime)){
      sendIMUData(data);
      imu_lastUpdate = millis();
    }

    imu_lastMeasure = millis();
  }

  // RPM MEASUREMENT
  if (currTime - PID_lastSample >= PID_samplePeriod){
    RPMData data = computeRPM(currTime - PID_lastSample);
    sendRPM(data);

    // Updating PID output
    if (followReference) updatePIDOutput();    
    
    PID_lastSample = millis();
    resetCount();
  }
}

void parse_message(String msg){
  int16_t input_value = -1;
  String command = msg.substring(0,2);
  if (!isValidCommand(command)) {sendError("Bad commmand"); return;}
  
  if (msg.length() > 2){
    String value = msg.substring(2);
    if (!isInteger(value)) {sendError("Bad value"); return;}
    input_value = value.toInt();
  }
    
  if (command == "SG"){sendResponse(getSteer());}
  else if (command == "SS"){setSteerAngle(input_value);}
  else if (command == "SI"){incrementSteerAngle(input_value);}
  else if (command == "SD"){incrementSteerAngle(-input_value);}
  else if (command == "SC"){centerSteerAngle();}
  else if (command == "SM"){steerConfig("max", input_value);}
  else if (command == "Sm"){steerConfig("min", input_value);}
  else if (command == "Sc"){steerConfig("center", input_value);}

  else if (command == "PG"){sendResponse(getPan());}
  else if (command == "PS"){setPanAngle(input_value);}
  else if (command == "PI"){incrementPanAngle(input_value);}
  else if (command == "PD"){incrementPanAngle(-input_value);}
  else if (command == "PC"){centerPanAngle();}
  else if (command == "PM"){cameraConfig("pan max", input_value);}
  else if (command == "Pm"){cameraConfig("pan min", input_value);}
  else if (command == "Pc"){cameraConfig("pan center", input_value);}
  
  else if (command == "TG"){sendResponse(getTilt());}
  else if (command == "TS"){setTiltAngle(input_value);}
  else if (command == "TI"){incrementTiltAngle(input_value);}
  else if (command == "TD"){incrementTiltAngle(-input_value);}
  else if (command == "TC"){centerTiltAngle();}
  else if (command == "TM"){cameraConfig("tilt max", input_value);}
  else if (command == "Tm"){cameraConfig("tilt min", input_value);}
  else if (command == "Tc"){cameraConfig("tilt center", input_value);}

  else if (command == "DP"){followReference = false; changeDrivePower(input_value);}
  else if (command == "DI"){incrementDrivePower(input_value);}
  else if (command == "DD"){incrementDrivePower(-input_value);}
  else if (command == "DS"){followReference = false; stopDrive();}
  else if (command == "DC"){changeDriveDirection(input_value);}
  else if (command == "DM"){driveConfig("max", input_value);}
  
  else if (command == "FO"){USSensorData data = measureFrontDistance(); sendUSSensorData(data);}
  else if (command == "FC"){frontUsReading=true;}
  else if (command == "FS"){frontUsReading=false;}
  else if (command == "FT"){frontUS_readTime = input_value; frontUS_lastMeasure = millis();}
  else if (command == "FU"){frontUS_updateTime = input_value; frontUS_lastUpdate = millis();}
  else if (command == "BO"){USSensorData data = measureBackDistance(); sendUSSensorData(data);}
  else if (command == "BC"){backUsReading=true;}
  else if (command == "BS"){backUsReading=false;}
  else if (command == "BT"){backUS_readTime = input_value; backUS_lastMeasure = millis();}
  else if (command == "BU"){backUS_updateTime = input_value; backUS_lastUpdate = millis();}

  else if (command == "Ic"){sendLog("Calibration function not implemented yet...");}
  else if (command == "IO"){IMUData data = compute6dof(); sendIMUData(data);}
  else if (command == "IC"){readImu = true;}
  else if (command == "IS"){readImu = false;}
  else if (command == "IT"){imu_readTime = input_value; imu_lastMeasure = millis();}
  else if (command == "IU"){imu_updateTime = input_value; imu_lastUpdate = millis();}

  else if (command == "FE"){frontCollision=true;}
  else if (command == "FD"){frontCollision=false;}
  else if (command == "F!"){frontStopDist = input_value;}
  else if (command == "BE"){backCollision=true;}
  else if (command == "BD"){backCollision=false;}
  else if (command == "B!"){backStopDist = input_value;}

  else if (command == "RR"){followReference = true; setPIDReference((double)input_value);}
  else if (command == "RU"){shiftGearUp();}
  else if (command == "RD"){shiftGearDown();}

  else if (command == "LH"){digitalWrite(LIGHT_PIN, HIGH);}
  else if (command == "LL"){digitalWrite(LIGHT_PIN, LOW);}
  else if (command == "HH"){digitalWrite(BUZZER_PIN, HIGH);}
  else if (command == "HL"){digitalWrite(BUZZER_PIN, LOW);}
      
  else {sendLog("Unknown command " + command);}
}
