#include "drive.h"

#define FPWM 6
#define BPWM 5

// Maximum allowed drive power
uint8_t MAX_POWER = 255;
double drivePower = 0;
uint8_t onDrive = FPWM; // Forward direction first on
uint8_t offDrive = BPWM; 

void changeDrivePower(uint16_t power){
  if (power > MAX_POWER){power = MAX_POWER;}

  // Saving the angle in the steer_angle variable
  drivePower = power;

  // Updating the angle
  analogWrite(onDrive, power);
  analogWrite(offDrive, 0);
}

void incrementDrivePower(uint16_t power){
  uint8_t inputValue = drivePower + power;
  changeDrivePower(inputValue);
}

void stopDrive(){
  changeDrivePower(0);
}

void changeDriveDirection(uint16_t dir){
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

void setMaxDrivePower(uint16_t value){
  if ((value <= 255) && (value >= 0)){
    MAX_POWER = value;
    sendLog(F("Maximum allowed power changed"));
  } else {
    sendError(F("Invalid value for maximum power"));
  }
}

uint8_t getMaxDrivePower(){
  return MAX_POWER;
}

void driveInit(){
  pinMode(FPWM, OUTPUT);
  pinMode(BPWM, OUTPUT);

  changeDriveDirection(1); // Forward- default starting direction
  changeDrivePower(0);
}
