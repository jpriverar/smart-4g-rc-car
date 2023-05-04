#include "camera.h"

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

void setPanMax(uint16_t value){
    if ((value <= 180) && (value >= PAN_MIN)){
    PAN_MAX = value;
    sendLog(F("Cam pan max endstop changed"));
  } else {
    sendError(F("Invalid value for pan maximum endstop"));
  }
}

void setPanCenter(uint16_t value){
  if ((value <= PAN_MAX) && (value >= PAN_MIN)){
    PAN_CENTER = value;
    sendLog(F("Cam pan center value changed"));
  } else {
    sendError(F("Invalid value for pan center endstop"));
  }
}

void setPanMin(uint16_t value){
  if ((value <= PAN_MAX) && (value >= 0)){
    PAN_MIN = value;
    sendLog(F("Cam pan min endstop changed"));
  } else {
    sendError(F("Invalid value for pan min endstop"));
  }
}

uint8_t getPanMax(){
  return PAN_MAX;
}

uint8_t getPanCenter(){
  return PAN_CENTER;
}

uint8_t getPanMin(){
  return PAN_MIN;
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

void setTiltMax(uint16_t value){
    if ((value <= 180) && (value >= TILT_MIN)){
    TILT_MAX = value;
    sendLog(F("Cam tilt max endstop changed"));
  } else {
    sendError(F("Invalid value for tilt maximum endstop"));
  }
}

void setTiltCenter(uint16_t value){
  if ((value <= TILT_MAX) && (value >= TILT_MIN)){
    TILT_CENTER = value;
    sendLog(F("Cam tilt center value changed"));
  } else {
    sendError(F("Invalid value for tilt center endstop"));
  }
}

void setTiltMin(uint16_t value){
  if ((value <= TILT_MAX) && (value >= 0)){
    TILT_MIN = value;
    sendLog(F("Cam tilt min endstop changed"));
  } else {
    sendError(F("Invalid value for tilt min endstop"));
  }
}

uint8_t getTiltMax(){
  return TILT_MAX;
}

uint8_t getTiltCenter(){
  return TILT_CENTER;
}

uint8_t getTiltMin(){
  return TILT_MIN;
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
