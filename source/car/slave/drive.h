#ifndef DRIVE_H_
#define DRIVE_H_
#include <Arduino.h>

void driveInit();
void driveConfig(String param, int16_t value);
void changeDrivePower(uint8_t power);
void incrementDrivePower(uint8_t power);
void stopDrive();
void changeDriveDirection(uint8_t dir);

#endif /*DRIVE_H_*/
