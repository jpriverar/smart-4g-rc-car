#ifndef CAMERA_H_
#define CAMERA_H_
#include <Arduino.h>
#include <Servo.h>
#include "messenger.h"

void cameraInit();
void cameraConfig(String param, int16_t value);
uint8_t getPan();
void setPanAngle(int16_t value);
void incrementPanAngle(int16_t incValue);
void centerPanAngle();
uint8_t getTilt();
void setTiltAngle(int16_t value);
void incrementTiltAngle(int16_t incValue);
void centerTiltAngle();

#endif /*CAMERA_H_*/
