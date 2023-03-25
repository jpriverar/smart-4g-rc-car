#ifndef STEER_H_
#define STEER_H_
#include <Arduino.h>
#include <Servo.h>

void steerInit();
uint8_t getSteer();
void steerConfig(String param, int16_t value);
void setSteerAngle(int16_t value);
void incrementSteerAngle(int16_t incValue);
void centerSteerAngle();

#endif /*STEER_H_*/
