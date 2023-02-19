#include "messenger.h"

String command;

void wait_for_connection(){
  while(1){
    Serial.println("ready");
    if (Serial.available() > 0){
      String msg = Serial.readStringUntil('\n');
      if (msg == "OK") break;
    }
    delay(500);
  }
}