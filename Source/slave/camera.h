#ifndef CAMERA_H_
#define CAMERA_H_
#include <Arduino.h>
#include <Servo.h>

void camera_init();
void camera_config(String param, int16_t value);
void change_pan_angle(uint8_t angle);
void increment_pan_angle(uint8_t inc_angle);
void change_tilt_angle(uint8_t angle);
void increment_tilt_angle(uint8_t inc_angle);

#endif /*CAMERA_H_*/