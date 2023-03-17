#ifndef SPEEDOMETER_H_
#define SPEEDOMTER_H_
#include <Arduino.h>

void speedometerInit();
void increaseCount();
double computeRPM(double currTime);

#endif //SPEEDOMETER_H_
