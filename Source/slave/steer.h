#ifndef STEER_H_
#define STEER_H_
#include <Arduino.h>
#include <Servo.h>

void steer_init();
void steer_config(String param, int16_t value);
void change_steer_angle(uint8_t angle);
void increment_steer_angle(uint8_t inc_angle);

#endif /*STEER_H_*/