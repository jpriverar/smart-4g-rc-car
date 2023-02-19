#include "drive.h"

#define FPWM 5
#define BPWM 6

// Maximum allowed drive power
uint8_t MAX_POWER = 100;
uint8_t drive_power = 0;
uint8_t on_drive = FPWM; // Forward direction first on
uint8_t off_drive = BPWM; 

void change_drive_power(uint8_t power){
  if (power > MAX_POWER){power = MAX_POWER;}

  // Saving the angle in the steer_angle variable
  drive_power = power;

  // Updating the angle
  analogWrite(on_drive, power);
  analogWrite(off_drive, 0);
}

void increment_drive_power(uint8_t power){
  uint8_t input_value = drive_power + power;
  change_drive_power(input_value);
}

void stop_drive(){
  change_drive_power(0);
}

void change_drive_direction(uint8_t dir){
  // Stopping motors before change direction
  stop_drive();
  
  // Forward - dir = 1
  if (dir){
    on_drive = FPWM;
    off_drive = BPWM;  
  } else {
  // Backwards - dir = 0
    on_drive = BPWM;
    off_drive = FPWM;
  }
}

void drive_config(String param, int16_t value = -1){
  // GET parameter value
  if (value == -1){
    if (param == "max") Serial.println(MAX_POWER);
    else Serial.println(F("Unknown steer configuration parameter..."));
    
  } else {
  // SET parameter values
    if (param == "max"){
      if (value <= 255){
        MAX_POWER = value; 
        Serial.println(F("Maximum allowed power changed..."));
      } else {
        MAX_POWER = 255;
        Serial.println(F("Unvalid value for maximum power, setting to absolute maximum"));
      }
    } else Serial.println(F("Unknown steer configuration parameter..."));
  }
}

void drive_init(){
  pinMode(FPWM, OUTPUT);
  pinMode(BPWM, OUTPUT);

  change_drive_direction(1); // Forward- default starting direction
  change_drive_power(drive_power);

  // Changing timer frequency for drive PWM, Timer for pins 5&6 to 7.8 kHz
  TCCR0B = TCCR0B & 0b11111000 | 0x02; // Prescaler -> 8, 7.8 kHz
}