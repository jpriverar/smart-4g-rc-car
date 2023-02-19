#ifndef CAMERA_H_
#define CAMERA_H_
#include <Arduino.h>
#include <Servo.h>

void cameraInit();
void cameraConfig(String param, int16_t value);
void changePanAngle(uint8_t angle);
void incrementPanAngle(uint8_t incAngle);
void changeTiltAngle(uint8_t angle);
void incrementTiltAngle(uint8_t incAngle);

#endif /*CAMERA_H_*/