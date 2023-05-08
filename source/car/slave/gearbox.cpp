#include "gearbox.h"

// Defining the gear speeds for each gear
GearSpeed gearSpeeds[7];

void gearboxInit(){
  // Reverse
  gearSpeeds[0].min_rpm = 0;
  gearSpeeds[0].max_rpm = 1500;
  
  // Forward gears
  gearSpeeds[1].min_rpm = 0;
  gearSpeeds[1].max_rpm = 1000;
  
  gearSpeeds[2].min_rpm = 900;
  gearSpeeds[2].max_rpm = 2000;
  
  gearSpeeds[3].min_rpm = 1900;
  gearSpeeds[3].max_rpm = 3000;
  
  gearSpeeds[4].min_rpm = 2800;
  gearSpeeds[4].max_rpm = 4000;
  
  gearSpeeds[5].min_rpm = 3800;
  gearSpeeds[5].max_rpm = 5000;
  
  gearSpeeds[6].min_rpm = 4700;
  gearSpeeds[6].max_rpm = 6000;
}


uint8_t gear = 1;

uint8_t getGear(){
  return gear;
}

int getMaxRPM(){
  return gearSpeeds[gear].max_rpm;
}

int getMinRPM(){
  return gearSpeeds[gear].min_rpm;
}


void shiftGearUp(){
  if (gear < 6){
    double rpm = getRPM();

    // If in reverse, car must be stopped completely before changing to first gear
    if ((gear == 0) && (rpm == 0)){
      // Changing the drive direction to move forward
      changeDriveDirection(1);
      gear = 1;
    }

    // Otherwise, we just need to reach the minimum next speed
    else if (rpm >= gearSpeeds[gear+1].min_rpm){
      gear++;
    }
  }
}

void shiftGearDown(){
  if (gear > 0){
    double rpm = getRPM();
    
    // To go to reverse, car must be completely stopped and in first gear
    if (gear == 1){
      // Changing the drive direction to move backwards
      if (rpm == 0){
        changeDriveDirection(0);
        gear = 0;
      }
    }

    // Otherwise, simply lower the gear and set the reference to the minium between the current rpm and lower-gear max rpm
    else{
    if (gearSpeeds[gear-1].max_rpm < rpm) setPIDReference(gearSpeeds[gear-1].max_rpm);
    gear--;
    }
  }
}
