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
uint8_t cam_pan = PAN_CENTER;
uint8_t cam_tilt = TILT_CENTER;

Servo pan_servo;
Servo tilt_servo;

void camera_init(){
  pinMode(CAM_PAN_PIN, OUTPUT);
  pinMode(CAM_TILT_PIN, OUTPUT);

  pan_servo.attach(CAM_PAN_PIN);
  tilt_servo.attach(CAM_TILT_PIN);

  change_pan_angle(cam_pan);
  change_tilt_angle(cam_tilt);
}

void change_pan_angle(uint8_t angle){
    if (angle > PAN_MAX){angle = PAN_MAX;}
    else if (angle < PAN_MIN){angle = PAN_MIN;}

    // Saving the angle in the cam_pan variable
    cam_pan = angle;

    // Updating the angle
    pan_servo.write(cam_pan);
}

void increment_pan_angle(uint8_t inc_angle){
  uint8_t input_value = cam_pan + inc_angle;
  change_pan_angle(input_value);
}

void change_tilt_angle(uint8_t angle){
    if (angle > TILT_MAX){angle = TILT_MAX;}
    else if (angle < TILT_MIN){angle = TILT_MIN;}
    
    // Saving the angle in the cam_tilt variable
    cam_tilt = angle;

    // Updating the angle
    tilt_servo.write(cam_tilt);
}

void increment_tilt_angle(uint8_t inc_angle){
  uint8_t input_value = cam_tilt + inc_angle;
  change_tilt_angle(input_value);
}

void camera_config(String param, int16_t value = -1){
  // GET parameter values
  if (value == -1){
    if (param == "pan min") Serial.println(PAN_MIN);
    else if (param == "pan max") Serial.println(PAN_MAX);
    else if (param == "pan center") Serial.println(PAN_CENTER);
    else if (param == "tilt min") Serial.println(TILT_MIN);
    else if (param == "tilt max") Serial.println(TILT_MAX);
    else if (param == "tilt center") Serial.println(TILT_CENTER);
    else Serial.println(F("Unknown camera configuration parameter..."));
    
  } else {
  // SET parameter values
    if (param == "pan min"){
      if (value >= 0){
        PAN_MIN = value; 
        Serial.println(F("Camera pan minimum endstop changed..."));
      } else {
        PAN_MIN = 0;
        Serial.println(F("Unvalid value for pan minimum endstop, setting to absolute minimum"));
      }
    }
    else if (param == "pan max"){
      if (value <= 180){
        PAN_MAX = value; 
        Serial.println(F("Camera pan maximum endstop changed..."));
      } else {
        PAN_MAX = 180;
        Serial.println(F("Unvalid value for pan maximum endstop, setting to absolute maximum"));
      }
    }
    else if (param == "pan center"){
      if (value >= PAN_MIN && value <= PAN_MAX){
        PAN_CENTER = value; 
        Serial.println(F("Camera pan center value changed..."));
      } else {
        Serial.println(F("Unvalid center value, value must be between PAN_MIN and PAN_MAX"));
      }
      
    }
    else if (param == "tilt min"){
      if (value >= 0){
        TILT_MIN = value; 
        Serial.println(F("Camera tilt minimum endstop changed..."));
      } else {
        TILT_MIN = 0;
        Serial.println(F("Unvalid value for tilt minimum endstop, setting to absolute minimum"));
      }
    }
    else if (param == "tilt max"){
      if (value <= 180){
        TILT_MAX = value; 
        Serial.println(F("Camera tilt maximum endstop changed..."));
      } else {
        TILT_MAX = 180;
        Serial.println(F("Unvalid value for tilt maximum endstop, setting to absolute maximum"));
      }
    }
    else if (param == "tilt center"){
      if (value >= TILT_MIN && value <= TILT_MAX){
        TILT_CENTER = value; 
        Serial.println(F("Camera tilt center value changed..."));
      } else {
        Serial.println(F("Unvalid center value, value must be between TILT_MIN and TILT_MAX"));
      }
    }
    else Serial.println(F("Unknown camera configuration parameter..."));
  }
}

