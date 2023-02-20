#include "messenger.h"

void waitForConnection(){
  while(1){
    Serial.println("ready");
    if (Serial.available() > 0){
      String msg = Serial.readStringUntil('\n');
      if (msg == "OK") break;
    }
    delay(500);
  }
}

void sendMsg(Message* msg) {
  byte* ptr = (byte*)msg;
  for (int i = 0; i < sizeof(msg); i++) {
    Serial.write(*ptr);
    ptr++;
  }
}