#include "steer.h"

#define STEER_PIN 11

uint8_t STEER_MIN = 35;
uint8_t STEER_MAX = 130;
uint8_t STEER_CENTER = 80;
uint8_t steer_angle = STEER_CENTER;

Servo steer_servo;

void change_steer_angle(uint8_t angle){
    if (angle > STEER_MAX){angle = STEER_MAX;}
    else if (angle < STEER_MIN){angle = STEER_MIN;}

    // Saving the angle in the steer_angle variable
    steer_angle = angle;

    // Updating the angle
    steer_servo.write(angle);
}

void increment_steer_angle(uint8_t inc_angle){
  uint8_t input_value = steer_angle + inc_angle;
  change_steer_angle(input_value);
}

void steer_config(String param, int16_t value = -1){
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

void steer_init(){
  pinMode(STEER_PIN, OUTPUT);
  steer_servo.attach(STEER_PIN);
  change_steer_angle(steer_angle);
}