#ifndef CAMERA_H_
#define CAMERA_H_
#include <Arduino.h>
#include <Servo.h>
#include "messenger.h"

void cameraInit();

void setPanMax(uint16_t value);
void setPanCenter(uint16_t value);
void setPanMin(uint16_t value);
uint8_t getPanMax();
uint8_t getPanCenter();
uint8_t getPanMin();
void setPanAngle(int16_t value);
void incrementPanAngle(int16_t incValue);
void centerPanAngle();

void setTiltMax(uint16_t value);
void setTiltCenter(uint16_t value);
void setTiltMin(uint16_t value);
uint8_t getTiltMax();
uint8_t getTiltCenter();
uint8_t getTiltMin();
void setTiltAngle(int16_t value);
void incrementTiltAngle(int16_t incValue);
void centerTiltAngle();

#endif /*CAMERA_H_*/
