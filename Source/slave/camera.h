#ifndef CAMERA_H_
#define CAMERA_H_
#include <Arduino.h>
#include <Servo.h>

void cameraInit();
void cameraConfig(String param, int16_t value);
uint8_t getPan();
void setPanAngle(uint8_t angle);
void incrementPanAngle(uint8_t incAngle);
void centerPanAngle();
uint8_t getTilt();
void setTiltAngle(uint8_t angle);
void incrementTiltAngle(uint8_t incAngle);
void centerTiltAngle();

#endif /*CAMERA_H_*/