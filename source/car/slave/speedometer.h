#ifndef SPEEDOMETER_H_
#define SPEEDOMETER_H_
#include <Arduino.h>
#include "drive.h"
#include "gearbox.h"
#include "messenger.h"

void speedometerInit();
void setPIDReference(double value);
void updatePIDOutput();
void increaseCount();
void resetCount();
struct RPMData computeRPM(double period);
double getRPM();

#endif /*SPEEDOMETER_H_*/
