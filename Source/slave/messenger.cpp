#include "messenger.h"

String command;

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