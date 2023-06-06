#ifndef SPEEDOMETER_H_
#define SPEEDOMETER_H_
#include <Arduino.h>
#include "drive.h"
#include "messenger.h"

void speedometerInit();
void setGasPedal(uint16_t value);
void setBreakPedal(uint16_t value);
void setPIDReference(double value);
void updatePIDOutput();
void increaseCount();
void resetCount();
struct RPMData computeRPM(double period);
struct SpeedData computeSpeed();
double getRPM();

#endif /*SPEEDOMETER_H_*/
