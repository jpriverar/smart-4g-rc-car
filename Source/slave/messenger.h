#ifndef MESSENGER_H_
#define MESSENGER_H_
#include <Arduino.h>
#include <SoftwareSerial.h>
#include "imu.h"
#include "us_sensor.h"

struct Message{
  uint8_t messageType;
  uint16_t payloadLength;
  union{
    IMUData imuData;
    USSensorData usSensorData;
  } payload;
};

void waitForConnection();
void sendMsg(Message *msg);

#endif /*MESSENGER_H_*/
