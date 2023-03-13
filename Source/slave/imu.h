#ifndef IMU_H_
#define IMU_H_
#include <Arduino.h>
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    #include "Wire.h"
#endif

struct IMUData{
  float yaw;
  float pitch;
  float roll;
  float ax;
  float ay;
  float az;
};

void imuInit();
void dmpDataReady();
IMUData compute6dof();

#endif /*IMU_H_*/
