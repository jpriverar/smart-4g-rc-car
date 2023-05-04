#include "messenger.h"
#include "speedometer.h"
#include "us_sensor.h"
#include "camera.h"
#include "steer.h"
#include "imu.h"
#include "gearbox.h"
#include "drive.h"

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
bool readIMU = false;  // To start continuous imu readings
double IMU_lastMeasure;
double IMU_lastUpdate;
double IMU_readTime = 100; // 100ms between readings
double IMU_updateTime = 500;

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
  if ((readIMU) && (currTime - IMU_lastMeasure >= IMU_readTime)){
    IMUData data = compute6dof();

    // Send the IMU values
    if ((IMU_updateTime >= 0) && (currTime - IMU_lastUpdate >= IMU_updateTime)){
      sendIMUData(data);
      IMU_lastUpdate = millis();
    }

    IMU_lastMeasure = millis();
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
  char component = msg[0];
  char action = msg[1];
  
  if (msg.length() > 2){
    String value = msg.substring(2);
    if (!isInteger(value)) {sendError("Bad value"); return;}
    input_value = value.toInt();
  }

  switch(component){
    case 'S':
      performSteeringAction(action, input_value); break;
    case 'P':
      performCamPanAction(action, input_value); break;
    case 'T':
      performCamTiltAction(action, input_value); break;
    case 'D':
      performDriveAction(action, input_value); break;
    case 'F':
      performFrontUSSAction(action, input_value); break;
    case 'B':
      performBackUSSAction(action, input_value); break;
    case 'I':
      performIMUAction(action, input_value); break;
    case 'L':
      if (action == '1') digitalWrite(LIGHT_PIN, HIGH);
      else if (action == '0') digitalWrite(LIGHT_PIN, LOW);
      break;
    case 'H':
      if (action == '1') digitalWrite(BUZZER_PIN, HIGH);
      else if (action == '0') digitalWrite(BUZZER_PIN, LOW);
      break;
    default:
      sendError("Unknown component " + component);
  }
}

void performSteeringAction(char action, uint16_t value){
  switch(action){
    case 'S':
      setSteerAngle(value); break;
    case 'I':
      incrementSteerAngle(value); break;
    case 'D':
      incrementSteerAngle(-value); break;
    case 'C':
      centerSteerAngle(); break;
    case 'M':
      setSteerMax(value); break;
    case 'c':
      setSteerCenter(value); break;
    case 'm':
      setSteerMin(value); break;
    case 'x':
      sendResponse(getSteerMax()); break;
    case 'r':
      sendResponse(getSteerCenter()); break;
    case 'n':
      sendResponse(getSteerMin()); break;
  }
}

void performCamPanAction(char action, uint16_t value){
  switch(action){
    case 'S':
      setPanAngle(value); break;
    case 'I':
      incrementPanAngle(value); break;
    case 'D':
      incrementPanAngle(-value); break;
    case 'C':
      centerPanAngle(); break;
    case 'M':
      setPanMax(value); break;
    case 'c':
      setPanCenter(value); break;
    case 'm':
      setPanMin(value); break;
    case 'x':
      sendResponse(getPanMax()); break;
    case 'r':
      sendResponse(getPanCenter()); break;
    case 'n':
      sendResponse(getPanMin()); break;
  }
}

void performCamTiltAction(char action, uint16_t value){
  switch(action){
    case 'S':
      setTiltAngle(value); break;
    case 'I':
      incrementTiltAngle(value); break;
    case 'D':
      incrementTiltAngle(-value); break;
    case 'C':
      centerTiltAngle(); break;
    case 'M':
      setTiltMax(value); break;
    case 'c':
      setTiltCenter(value); break;
    case 'm':
      setTiltMin(value); break;
    case 'x':
      sendResponse(getTiltMax()); break;
    case 'r':
      sendResponse(getTiltCenter()); break;
    case 'n':
      sendResponse(getTiltMin()); break;
  }
}

void performDriveAction(char action, uint16_t value){
  switch(action){
    case 'P':
      followReference = false; changeDrivePower(value); break;
    case 'I':
      incrementDrivePower(value); break;
    case 'D':
      incrementDrivePower(-value); break;
    case 'S':
      followReference = false; stopDrive(); break;
    case 'C':
      changeDriveDirection(value); break;
    case 's':
      setMaxDrivePower(value); break;
    case 'g':
      sendResponse(getMaxDrivePower()); break;
  }
}

void performFrontUSSAction(char action, uint16_t value){
  switch(action){
    case 'O':
      USSensorData data = measureFrontDistance(); sendUSSensorData(data); break;
    case 'C':
      frontUsReading = true; break;
    case 'S':
      frontUsReading = false; break;
    case 'T':
      frontUS_readTime = value; frontUS_lastMeasure = millis(); break;
    case 'U':
      frontUS_updateTime = value; frontUS_lastUpdate = millis(); break;
    case 'E':
      frontCollision = true; break;
    case 'D':
      frontCollision = false; break;
    case 'd':
      frontStopDist = value; break;
  }
}

void performBackUSSAction(char action, uint16_t value){
  switch(action){
    case 'O':
      USSensorData data = measureBackDistance(); sendUSSensorData(data); break;
    case 'C':
      backUsReading = true; break;
    case 'S':
      backUsReading = false; break;
    case 'T':
      backUS_readTime = value; frontUS_lastMeasure = millis(); break;
    case 'U':
      backUS_updateTime = value; frontUS_lastUpdate = millis(); break;
    case 'E':
      backCollision = true; break;
    case 'D':
      backCollision = false; break;
    case 'd':
      backStopDist = value; break;
  }
}

void performIMUAction(char action, uint16_t value){
  switch(action){
    case 'O':
      IMUData data = compute6dof(); sendIMUData(data); break;
    case 'C':
      readIMU = true; break;
    case 'S':
      readIMU = false; break;
    case 'T':
      IMU_readTime = value; IMU_lastMeasure = millis(); break;
    case 'U':
      IMU_updateTime = value; IMU_lastUpdate = millis(); break;
  }
}

  /*
  if (command == "SS"){setSteerAngle(input_value);}
  else if (command == "SI"){incrementSteerAngle(input_value);}
  else if (command == "SD"){incrementSteerAngle(-input_value);}
  else if (command == "SC"){centerSteerAngle();}
  else if (command == "SX"){setSteerMax(input_value);}
  else if (command == "SY"){setSteerCenter(input_value);}
  else if (command == "SZ"){setSteerMin(input_value);}
  else if (command == "SM"){sendResponse(getSteerMax());}
  else if (command == "Sc"){sendResponse(getSteerCenter());}
  else if (command == "Sm"){sendResponse(getSteerMin());}
  
  else if (command == "PS"){setPanAngle(input_value);}
  else if (command == "PI"){incrementPanAngle(input_value);}
  else if (command == "PD"){incrementPanAngle(-input_value);}
  else if (command == "PC"){centerPanAngle();}
  else if (command == "PX"){setPanMax(input_value);}
  else if (command == "PY"){setPanCenter(input_value);}
  else if (command == "PZ"){setPanMin(input_value);}
  else if (command == "PM"){sendResponse(getPanMax());}
  else if (command == "Pc"){sendResponse(getPanCenter());}
  else if (command == "Pm"){sendResponse(getPanMin());}
  
  else if (command == "TS"){setTiltAngle(input_value);}
  else if (command == "TI"){incrementTiltAngle(input_value);}
  else if (command == "TD"){incrementTiltAngle(-input_value);}
  else if (command == "TC"){centerTiltAngle();}
  else if (command == "TX"){setTiltMax(input_value);}
  else if (command == "TY"){setTiltCenter(input_value);}
  else if (command == "TZ"){setTiltMin(input_value);}
  else if (command == "TM"){sendResponse(getTiltMax());}
  else if (command == "Tc"){sendResponse(getTiltCenter());}
  else if (command == "Tm"){sendResponse(getTiltMin());}

  else if (command == "DP"){followReference = false; changeDrivePower(input_value);}
  else if (command == "DI"){incrementDrivePower(input_value);}
  else if (command == "DD"){incrementDrivePower(-input_value);}
  else if (command == "DS"){followReference = false; stopDrive();}
  else if (command == "DC"){changeDriveDirection(input_value);}
  else if (command == "Ds"){setMaxDrivePower(input_value);}
  else if (command == "Dg"){sendResponse(getMaxDrivePower());}
  
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
  else if (command == "Fd"){frontStopDist = input_value;}
  else if (command == "BE"){backCollision=true;}
  else if (command == "BD"){backCollision=false;}
  else if (command == "Bd"){backStopDist = input_value;}

  else if (command == "RR"){followReference = true; setPIDReference((double)input_value);}
  else if (command == "RU"){shiftGearUp();}
  else if (command == "RD"){shiftGearDown();}

  else if (command == "LH"){digitalWrite(LIGHT_PIN, HIGH);}
  else if (command == "LL"){digitalWrite(LIGHT_PIN, LOW);}
  else if (command == "HH"){digitalWrite(BUZZER_PIN, HIGH);}
  else if (command == "HL"){digitalWrite(BUZZER_PIN, LOW);}
      
  else {sendLog("Unknown command " + command);}
  */
