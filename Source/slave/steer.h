#ifndef STEER_H_
#define STEER_H_
#include <Arduino.h>
#include <Servo.h>

void steerInit();
void steerConfig(String param, int16_t value);
void changeSteerAngle(uint8_t angle);
void incrementSteerAngle(uint8_t incAngle);
void centerSteerAngle();

#endif /*STEER_H_*/