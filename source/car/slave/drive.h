#ifndef DRIVE_H_
#define DRIVE_H_
#include <Arduino.h>
#include "messenger.h"

void driveInit();
void setMaxDrivePower(uint16_t value);
uint8_t getMaxDrivePower();
void changeDrivePower(uint16_t power);
void incrementDrivePower(uint16_t power);
void stopDrive();
void changeDriveDirection(uint16_t dir);

#endif /*DRIVE_H_*/
