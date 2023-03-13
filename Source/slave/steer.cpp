#include "steer.h"
#include "messenger.h"

#define STEER_PIN 11

uint8_t STEER_MIN = 35;
uint8_t STEER_MAX = 130;
uint8_t STEER_CENTER = 80;
uint8_t steerAngle = STEER_CENTER;

Servo steerServo;

uint8_t getSteer(){
  return steerAngle;
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

void steerConfig(String param, int16_t value = -1){
  // GET parameter value
  if (value == -1){
    if (param == "min") sendResponse(STEER_MIN);
    else if (param == "max") sendResponse(STEER_MAX);
    else if (param == "center") sendResponse(STEER_CENTER);
    else sendError("Invalid steer parameter");
    return;
  } 
  // SET parameter values
  if (value < 0) {value = 0; sendError(F("Steer param invalid, below min"));}
  if (value > 180) {value = 180; sendError(F("Steer param invalid, above max"));}

  if (param == "min"){
    STEER_MIN = value; 
    sendLog(F("Steer min endstop changed"));
  }
  else if (param == "max"){
    STEER_MAX = value; 
    sendLog(F("Steer max endstop changed"));
  }
  else if (param == "center"){
    if (value >= STEER_MIN && value <= STEER_MAX){
      STEER_CENTER = value; 
      sendLog(F("Steer center val changed"));
    } else sendError(F("Steer center val out of bounds"));
  }
  else sendError(F("Invalid steer parameter"));
}

void steerInit(){
  pinMode(STEER_PIN, OUTPUT);
  steerServo.attach(STEER_PIN);
  centerSteerAngle();
}
