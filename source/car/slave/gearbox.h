#ifndef GEARBOX_H_
#define GEARBOX_H_
#include <Arduino.h>
#include "drive.h"
#include "speedometer.h"

// Struct to hold the min and max speeds for each gear
struct GearSpeed{
  int min_rpm;
  int max_rpm;
};

void gearboxInit();
void shiftGearUp();
void shiftGearDown();
uint8_t getGear();
int getMaxRPM();
int getMinRPM();

#endif /*GEARBOX_H_*/
