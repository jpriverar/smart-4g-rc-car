#include "messenger.h"

void waitForConnection(){
  while(1){
    Serial.println("available");
    if (Serial.available() > 0){
      String msg = Serial.readStringUntil('\n');
      if (msg == "OK") break;
    }
    delay(500);
  }
}

bool isValidCommand(String command){
  if (command.length() > 2) return false;

  for(size_t i=0; i < command.length(); i++){
    if (!isalpha(command[i])) return false;
  }
  return true;
}

bool isInteger(String input_value){
  size_t start = 0;
  if (input_value[0] == '-') start++;
  
  for (size_t i=start; i < input_value.length() ; i++) {
      if (isdigit(input_value[i])) continue;
      else return false; // Not a digit, not an integer
  }
  
  return true; // All characters are digits, integer
}

void sendText(uint8_t type, String data){
  uint16_t dataLength = data.length();
  
  Serial.write(type);
  
  byte lenBytes[2];
  lenBytes[0] = dataLength & 0xFF; // low byte
  lenBytes[1] = (dataLength >> 8) & 0xFF; // high byte
  Serial.write(lenBytes[0]);
  Serial.write(lenBytes[1]);
  
  Serial.println(data);
}

void sendResponse(uint8_t data){
  Message msg;
  msg.messageType = 0x03;
  msg.payloadLength = 1;
  msg.payload = &data;
  sendMsg(&msg);
}

void sendError(String error){
  uint8_t type = 0x04;
  sendText(type, error);
}

void sendLog(String logText){
  uint8_t type = 0x05;
  sendText(type, logText);
}

void sendDebug(String debugText){
  uint8_t type = 0x06;
  sendText(type, debugText);
}

void sendMsg(Message* msg) {
  // Sending the header
  byte* ptr = (byte*)msg;
  for (int i = 0; i < 3; i++) {
    Serial.write(*ptr);
    ptr++;
  }

  // Sending the actual payload
  byte* ptrPayload = (byte*)msg->payload;
  for (int i = 0; i < msg->payloadLength; i++){
    Serial.write(*ptrPayload);
    ptrPayload++;
  }
}

void sendUSSensorData(USSensorData data){
  Message msg;
  msg.messageType = 0x01;
  msg.payloadLength = sizeof(data);
  msg.payload = &data;
  sendMsg(&msg);
}

void sendIMUData(IMUData data){
  Message msg;
  msg.messageType = 0x02;
  msg.payloadLength = sizeof(data);
  msg.payload = &data;
  sendMsg(&msg);
}

void sendRPM(RPMData data){
  Message msg;
  msg.messageType = 0x00;
  msg.payloadLength = sizeof(data);
  msg.payload = &data;
  sendMsg(&msg);
}
