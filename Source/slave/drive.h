#ifndef DRIVE_H_
#define DRIVE_H_
#include <Arduino.h>

void drive_init();
void drive_config(String param, int16_t value);
void change_drive_power(uint8_t power);
void increment_drive_power(uint8_t power);
void stop_drive();
void change_drive_direction(uint8_t dir);

#endif /*DRIVE_H_*/