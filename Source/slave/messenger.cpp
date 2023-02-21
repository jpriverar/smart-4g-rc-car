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