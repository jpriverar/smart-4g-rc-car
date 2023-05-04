#ifndef US_SENSOR_H_
#define US_SENSOR_H_
#include <Arduino.h>
#include "messenger.h"

void usSensorInit();
double measureDistance(uint8_t echoPin, uint8_t triggerPin, unsigned long timeout);
USSensorData measureFrontDistance();
USSensorData measureBackDistance();
void sendTrigger(uint8_t triggerPin);
void sendFrontTrigger();
void sendBackTrigger();

#endif /*US_SENSOR_H_*/
