#include "messenger.h"
#include "speedometer.h"
#include "us_sensor.h"
#include "camera.h"
#include "steer.h"
#include "imu.h"
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
double currTime;

void setup() {
  // Waiting to stablish connection with master
  Serial.begin(115200);
  waitForConnection();

  // Initializing all car components
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
      if ((data.distance < frontStopDist) && (data.distance > 2)) {
        stopDrive();
        lockForwardDrive();
      } else {
        unlockForwardDrive();
      }
      
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
      if ((data.distance < backStopDist) && (data.distance > 2)) {
        stopDrive();
        lockBackwardsDrive();
      } else {
        unlockBackwardsDrive();
      }
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
    RPMData rpmData = computeRPM(currTime - PID_lastSample);
    sendRPM(rpmData);

    SpeedData speedData = computeSpeed();
    sendSpeed(speedData);

    // Updating PID output
    bool driveLocked = checkDriveLocked();
    if ((followReference) && !(driveLocked))
      updatePIDOutput();    
    
    PID_lastSample = millis();
    resetCount();
  }
}

void parse_message(String msg){
  uint16_t input_value;
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
  followReference = false;
  switch(action){
    case 'R':
      followReference = true; setPIDReference(value); break;
    case 'P':
      changeDrivePower(value); break;
    case 'I':
      incrementDrivePower(value); break;
    case 'D':
      incrementDrivePower(-value); break;
    case 'S':
      stopDrive(); break;
    case 'C':
      changeDriveDirection(value); break;
    case 's':
      setMaxDrivePower(value); break;
    case 'g':
      sendResponse(getMaxDrivePower()); break;
  }
}

void performFrontUSSAction(char action, uint16_t value){
  if (action == 'O'){USSensorData data = measureFrontDistance(); sendUSSensorData(data);}
  else if (action == 'C'){frontUsReading = true;}
  else if (action == 'S'){frontUsReading = false;}
  else if (action == 'T'){frontUS_readTime = value; frontUS_lastMeasure = millis();}
  else if (action == 'U'){frontUS_updateTime = value; frontUS_lastMeasure = millis();}
  else if (action == 'E'){frontCollision = true;}
  else if (action == 'D'){frontCollision = false;}
  else if (action == 'd'){frontStopDist = value;}
}

void performBackUSSAction(char action, uint16_t value){
  if (action == 'O'){USSensorData data = measureBackDistance(); sendUSSensorData(data);}
  else if (action == 'C'){backUsReading = true;}
  else if (action == 'S'){backUsReading = false;}
  else if (action == 'T'){backUS_readTime = value; backUS_lastMeasure = millis();}
  else if (action == 'U'){backUS_updateTime = value; backUS_lastMeasure = millis();}
  else if (action == 'E'){backCollision = true;}
  else if (action == 'D'){backCollision = false;}
  else if (action == 'd'){backStopDist = value;}
}

void performIMUAction(char action, uint16_t value){
  if (action == 'O'){IMUData data = compute6dof(); sendIMUData(data);}
  else if (action == 'C'){readIMU = true;}
  else if (action == 'S'){readIMU = false;}
  else if (action == 'T'){IMU_readTime = value; IMU_lastMeasure = millis();}
  else if (action == 'U'){IMU_updateTime = value; IMU_lastUpdate = millis();}
}
