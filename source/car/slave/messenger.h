#ifndef MESSENGER_H_
#define MESSENGER_H_
#include <Arduino.h>
#include <SoftwareSerial.h>
#include "imu.h"
#include "us_sensor.h"
#include "speedometer.h"

struct Message{
  uint8_t messageType;
  uint16_t payloadLength;
  void *payload;
};

void waitForConnection();
bool isValidCommand(String command);
bool isInteger(String input_value);
void sendMsg(Message *msg);
void sendText(uint8_t type, String text);
void sendError(String error);
void sendLog(String logText);
void sendDebug(String debugText);
void sendResponse(uint8_t data);
void sendUSSensorData(USSensorData data);
void sendIMUData(IMUData data);
void sendRPM(RPMData data);

#endif /*MESSENGER_H_*/
