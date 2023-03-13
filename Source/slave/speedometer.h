#ifndef SPEEDOMETER_H_
#define SPEEDOMTER_H_
#include <Arduino.h>

extern double speedometerStartTime;
void speedometerInit();
void increaseCount();
double computeRPM(double period_ms);

#endif //SPEEDOMETER_H_