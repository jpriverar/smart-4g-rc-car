#include "steer.h"

#define STEER_PIN 11

uint8_t STEER_MIN = 35;
uint8_t STEER_MAX = 130;
uint8_t STEER_CENTER = 80;
uint8_t steerAngle = STEER_CENTER;

Servo steerServo;

void steerInit(){
  pinMode(STEER_PIN, OUTPUT);
  steerServo.attach(STEER_PIN);
  centerSteerAngle();
}

void setSteerMax(uint16_t value){
  if ((value <= 180) && (value >= STEER_MIN)){
    STEER_MAX = value;
    sendLog(F("Steering max endstop changed"));
  } else {
    sendError(F("Invalid value for max steering endstop"));
  }
}

void setSteerCenter(uint16_t value){
  if ((value <= STEER_MAX) && (value >= STEER_MIN)){
    STEER_CENTER = value;
    sendLog(F("Steering center value changed"));
  } else {
    sendError(F("Invalid value for steering center"));
  }
}

void setSteerMin(uint16_t value){
  if ((value <= STEER_MAX) && (value >= 0)){
    STEER_MIN = value;
    sendLog(F("Steering min endstop changed"));
  } else {
    sendError(F("Invalid value for min steering endstop"));
  }
}

uint8_t getSteerMax(){
  return STEER_MAX;
}

uint8_t getSteerCenter(){
  return STEER_CENTER;
}

uint8_t getSteerMin(){
  return STEER_MIN;
}

void setSteerAngle(int16_t value){
    // Mapping the input value to the angle range
    if (value > 1024) value = 1024;
    if (value < -1024) value = -1024;

    uint8_t angle = steerAngle;
    if (value >= 0) angle = map(value, 0, 1024, STEER_CENTER, STEER_MAX);
    else angle = map(value, -1024, 0, STEER_MIN, STEER_CENTER);

    // Saving the angle in the steer_angle variable
    steerAngle = angle;

    // Updating the angle
    steerServo.write(angle);
}

void incrementSteerAngle(int16_t incValue){
  uint8_t inputValue = steerAngle + map(incValue, -1024, 1024, -5, 5);
  setSteerAngle(inputValue);
}

void centerSteerAngle(){
  steerAngle = STEER_CENTER;
  steerServo.write(steerAngle);
}
