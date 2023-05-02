#ifndef SPEEDOMETER_H_
#define SPEEDOMETER_H_
#include <Arduino.h>
#include "drive.h"
#include "gearbox.h"

struct RPMData{
  uint8_t gear;
  double rpm;
};

void speedometerInit();
void setPIDReference(double value);
void updatePIDOutput();
void increaseCount();
void resetCount();
RPMData computeRPM(double period);
double getRPM();

#endif /*SPEEDOMETER_H_*/
