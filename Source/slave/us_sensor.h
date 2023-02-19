#ifndef US_SENSOR_H_
#define US_SENSOR_H_
#include <Arduino.h>

void us_sensor_init();
double measure_distance(String sensor);
void send_trigger(String sensor);

#endif /*US_SENSOR_H_*/