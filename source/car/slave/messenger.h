#ifndef MESSENGER_H_
#define MESSENGER_H_
#include <Arduino.h>
#include <SoftwareSerial.h>

struct Message{
  uint8_t messageType;
  uint16_t payloadLength;
  void *payload;
};

struct RPMData{
  uint8_t gear;
  double rpm;
};

struct USSensorData{
  uint8_t side; //1 for front and 0 for back sensors
  double distance;
};

struct IMUData{
  float yaw;
  float pitch;
  float roll;
  float ax;
  float ay;
  float az;
};

void waitForConnection();
bool isValidCommand(String command);
bool isInteger(String input_value);
void sendMsg(Message *msg);
void sendText(uint8_t type, String text);
void sendError(String errorText);
void sendLog(String logText);
void sendDebug(String debugText);
void sendResponse(uint8_t data);
void sendUSSensorData(USSensorData data);
void sendIMUData(IMUData data);
void sendRPM(RPMData data);

#endif /*MESSENGER_H_*/
