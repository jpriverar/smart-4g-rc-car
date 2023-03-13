#include "camera.h"
#include "messenger.h"

#define CAM_PAN_PIN 10
#define CAM_TILT_PIN 9

// Angle endstop for camera motors
uint8_t PAN_MIN = 10;
uint8_t PAN_MAX = 180;
uint8_t PAN_CENTER = 100;
uint8_t TILT_MIN = 40;
uint8_t TILT_MAX = 100;
uint8_t TILT_CENTER = 50;
uint8_t camPan = PAN_CENTER;
uint8_t camTilt = TILT_CENTER;

Servo panServo;
Servo tiltServo;

void cameraInit(){
  pinMode(CAM_PAN_PIN, OUTPUT);
  pinMode(CAM_TILT_PIN, OUTPUT);

  panServo.attach(CAM_PAN_PIN);
  tiltServo.attach(CAM_TILT_PIN);

  setPanAngle(camPan);
  setTiltAngle(camTilt);
}

uint8_t getPan(){
  return camPan;
}

void setPanAngle(int16_t value){
    // Mapping the input value to the angle range
    if (value > 1023) value = 1023;
    if (value < -1024) value = -1024;

    uint8_t angle = camPan;
    if (value >= 0) angle = map(value, 0, 1024, PAN_CENTER, PAN_MAX); 
    else angle = map(value, -1024, 0, PAN_MIN, PAN_CENTER);

    // Saving the angle in the cam_pan variable
    camPan = angle;

    // Updating the angle
    panServo.write(camPan);
}

void incrementPanAngle(int16_t incValue){
  camPan += map(incValue, -1024, 1024, -5, 5);

  if (camPan > PAN_MAX) camPan = PAN_MAX;
  else if (camPan < PAN_MIN) camPan = PAN_MIN;
  panServo.write(camPan);
}

void centerPanAngle(){
  camPan = PAN_CENTER;
  panServo.write(camPan);
}

uint8_t getTilt(){
  return camTilt;
}

void setTiltAngle(int16_t value){
    // Mapping the input value to the angle range
    if (value > 1023) value = 1023;
    if (value < -1024) value = -1024;

    uint8_t angle = camTilt;
    if (value >= 0) angle = map(value, 0, 1024, TILT_CENTER, TILT_MAX);
    else angle = map(value, -1024, -0, TILT_MIN, TILT_CENTER);
    
    // Saving the angle in the cam_tilt variable
    camTilt = angle;

    // Updating the angle
    tiltServo.write(camTilt);
}


void incrementTiltAngle(int16_t incValue){
  camTilt += map(incValue, -1024, 1024, -5, 5);

  if (camTilt > TILT_MAX) camTilt = TILT_MAX;
  else if (camTilt < TILT_MIN) camTilt = TILT_MIN;
  tiltServo.write(camTilt);
}

void centerTiltAngle(){
  camTilt = TILT_CENTER;
  tiltServo.write(camTilt);
}

void cameraConfig(String param, int16_t value = -1){
  // GET parameter values
  if (value == -1){
    if (param == "pan min") sendResponse(PAN_MIN);
    else if (param == "pan max") sendResponse(PAN_MAX);
    else if (param == "pan center") sendResponse(PAN_CENTER);
    else if (param == "tilt min") sendResponse(TILT_MIN);
    else if (param == "tilt max") sendResponse(TILT_MAX);
    else if (param == "tilt center") sendResponse(TILT_CENTER);
    else sendError(F("Invalid cam parameter"));
    return;
  } 
  
  // SET parameter values
  if (value < 0) {value = 0; sendError(F("Cam param invalid, below min"));}
  if (value > 180) {value = 180; sendError(F("Cam param invalid, above max"));}
  
  if (param == "pan min"){
    PAN_MIN = value; 
    sendLog(F("Cam pan min endstop changed"));
  }
  else if (param == "pan max"){
    PAN_MAX = value; 
    sendLog(F("Cam pan max endstop changed"));
  }
  else if (param == "pan center"){
    if (value >= PAN_MIN && value <= PAN_MAX){
      PAN_CENTER = value; 
      sendLog(F("Cam pan center val changed"));
    } else sendError(F("Pan center val out of bounds"));
  }
  else if (param == "tilt min"){
    TILT_MIN = value; 
    sendLog(F("Cam tilt min endstop changed"));
  }
  else if (param == "tilt max"){
    TILT_MAX = value; 
    sendLog(F("Cam tilt max endstop changed"));
  }
  else if (param == "tilt center"){
    if (value >= TILT_MIN && value <= TILT_MAX){
      TILT_CENTER = value; 
      sendLog(F("Cam tilt center val changed"));
    } else sendError(F("Tilt center val out of bounds"));
  }
  else sendError(F("Invalid cam parameter"));
}
