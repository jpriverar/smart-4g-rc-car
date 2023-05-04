#ifndef STEER_H_
#define STEER_H_
#include <Arduino.h>
#include <Servo.h>
#include "messenger.h"

void steerInit();

void setSteerMax(uint16_t value);
void setSteerCenter(uint16_t value);
void setSteerMin(uint16_t value);
uint8_t getSteerMax();
uint8_t getSteerCenter();
uint8_t getSteerMin();
void setSteerAngle(int16_t value);
void incrementSteerAngle(int16_t incValue);
void centerSteerAngle();

#endif /*STEER_H_*/
