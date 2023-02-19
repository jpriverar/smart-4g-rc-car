#ifndef IMU_H_
#define IMU_H_
#include <Arduino.h>
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    #include "Wire.h"
#endif

void imu_init();
void dmpDataReady();
void compute_6dof();

#endif /*IMU_H_*/