#include "drive.h"

#define FPWM 5
#define BPWM 6

// Maximum allowed drive power
uint8_t MAX_POWER = 100;
uint8_t drivePower = 0;
uint8_t onDrive = FPWM; // Forward direction first on
uint8_t offDrive = BPWM; 

void changeDrivePower(uint8_t power){
  if (power > MAX_POWER){power = MAX_POWER;}

  // Saving the angle in the steer_angle variable
  drivePower = power;

  // Updating the angle
  analogWrite(onDrive, power);
  analogWrite(offDrive, 0);
}

void incrementDrivePower(uint8_t power){
  uint8_t inputValue = drivePower + power;
  changeDrivePower(inputValue);
}

void stopDrive(){
  changeDrivePower(0);
}

void changeDriveDirection(uint8_t dir){
  // Stopping motors before change direction
  stopDrive();
  
  // Forward - dir = 1
  if (dir){
    onDrive = FPWM;
    offDrive = BPWM;  
  } else {
  // Backwards - dir = 0
    onDrive = BPWM;
    offDrive = FPWM;
  }
}

void driveConfig(String param, int16_t value = -1){
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

void driveInit(){
  pinMode(FPWM, OUTPUT);
  pinMode(BPWM, OUTPUT);
  
  // Changing timer frequency for drive PWM, Timer for pins 5&6 to 7.8 kHz
  //TCCR0B = TCCR0B & 0b11111000 | 0x02; // Prescaler -> 8, 7.8 kHz

  changeDriveDirection(1); // Forward- default starting direction
  changeDrivePower(0);
}
