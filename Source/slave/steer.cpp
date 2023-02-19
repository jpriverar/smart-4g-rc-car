#include "steer.h"

#define STEER_PIN 11

uint8_t STEER_MIN = 35;
uint8_t STEER_MAX = 130;
uint8_t STEER_CENTER = 80;
uint8_t steerAngle = STEER_CENTER;

Servo steerServo;

void changeSteerAngle(uint8_t angle){
    if (angle > STEER_MAX){angle = STEER_MAX;}
    else if (angle < STEER_MIN){angle = STEER_MIN;}

    // Saving the angle in the steer_angle variable
    steerAngle = angle;

    // Updating the angle
    steerServo.write(angle);
}

void incrementSteerAngle(uint8_t incAngle){
  uint8_t inputValue = steerAngle + incAngle;
  changeSteerAngle(inputValue);
}

void centerSteerAngle(){
  changeSteerAngle(STEER_CENTER);
}

void steerConfig(String param, int16_t value = -1){
  // GET parameter value
  if (value == -1){
    if (param == "min") Serial.println(STEER_MIN);
    else if (param == "max") Serial.println(STEER_MAX);
    else if (param == "center") Serial.println(STEER_CENTER);
    else Serial.println(F("Unknown steer configuration parameter..."));
    
  } else {
  // SET parameter values
    if (param == "min"){
      if (value >= 0){
        STEER_MIN = value; 
        Serial.println(F("Steer direction minimum endstop changed..."));
      } else {
        STEER_MIN = 0;
        Serial.println(F("Unvalid value for steer minimum endstop, setting to absolute minimum"));
      }
    }
    else if (param == "max"){
      if (value >= 180){
        STEER_MAX = value; 
        Serial.println(F("Steer direction minimum endstop changed..."));
      } else {
        STEER_MAX = 180;
        Serial.println(F("Unvalid value for steer maximum endstop, setting to absolute maximum"));
      }
    }
    else if (param == "center"){
      if (value >= STEER_MIN && value <= STEER_MAX){
        STEER_CENTER = value; 
        Serial.println(F("Steer direction center value changed..."));
      } else {
        Serial.println(F("Unvalid center value, value must be between STEER_MIN and STEER_MAX"));
      }
    }
    else Serial.println(F("Unknown steer configuration parameter..."));
  }
}

void steerInit(){
  pinMode(STEER_PIN, OUTPUT);
  steerServo.attach(STEER_PIN);
  centerSteerAngle();
}