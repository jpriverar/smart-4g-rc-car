#include <SoftwareSerial.h>

const char mic_pin = 2;
const char rx1_pin = 0;
const char ry1_pin = 1;

int rx1_val = 0;
int ry1_val = 0;

String command;

void read_joysticks(){
  // Reading adc
  rx1_val = analogRead(rx1_pin);
  ry1_val = analogRead(ry1_pin);

  // Sending the joystick values
  Serial.print(rx1_val);
  Serial.print(' ');
  Serial.println(ry1_val);
}

void read_mic(){
  int mic_raw = analogRead(mic_pin);
  float mic_volts = (float)mic_raw/1024*5;
  Serial.println(mic_raw);
}

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

void setup() {
  Serial.begin(9600);

  // Making sure there's a successfull connection
  wait_for_connection();
}
void loop() {
  // if raspberrypi sends new command
  if (Serial.available() > 0) {
    command = Serial.readStringUntil('\n');
    Serial.print("New command received: ");
    Serial.println(command);
  }

  if (command == "joystick"){
    read_joysticks();
  } 

  else if (command == "mic"){
    read_mic();
  }
}
