#include <Servo.h>

// Pin definition
const char STEER_PIN = 11;

// Angle endstop for servo motors
const uint8_t STEER_MIN = 35;
const uint8_t STEER_MAX = 130;

// Center positions for servo motors
const uint8_t STEER_CENTER = 80;

// Buffer for incoming messages
String msg;

// Setting the starting cam position to the center
uint8_t steer_angle = STEER_CENTER;

Servo steer_servo;

void setup() {
  Serial.begin(115200);

  pinMode(STEER_PIN, OUTPUT);

  steer_servo.attach(STEER_PIN);
  
  // Setting camera to the center
  change_steer_angle(steer_angle);

  // Timer for pins 5&6
  TCCR0B = TCCR0B & 0b11111000 | 0x02; // Prescaler -> 8, 7.8 kHz
}

void loop() {
  // If there are any incoming messages
  if(Serial.available()){
    msg = Serial.readStringUntil('\n');
    parse_message(msg);
  }
}

void parse_message(String msg){
  String command = msg.substring(0,2);
  int input_value;
  
  if (command == "SD"){
    input_value = msg.substring(2).toInt();
    change_steer_angle(input_value);
  }
  else {
    Serial.println("Unknown command, try again...");
  }
}

void change_steer_angle(uint8_t angle){
    if (angle > STEER_MAX){
      angle = STEER_MAX;
    }
    else if (angle < STEER_MIN){
      angle = STEER_MIN;
    }

    // Saving the angle in the steer_angle variable
    steer_angle = angle;

    // Updating the angle
    steer_servo.write(angle);
}

void increment_steer_angle(uint8_t inc_angle){
  uint8_t input_value = steer_angle + inc_angle;
  change_steer_angle(input_value);
}
