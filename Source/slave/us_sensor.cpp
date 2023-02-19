#include "us_sensor.h"

#define FRONT_TRIG 7
#define FRONT_ECHO 8
#define BACK_TRIG 4
#define BACK_ECHO 12

const double VelSon = 34000.0;

void us_sensor_init(){
  pinMode(FRONT_TRIG, OUTPUT);
  pinMode(FRONT_ECHO, INPUT);
  pinMode(BACK_TRIG, OUTPUT);
  pinMode(BACK_ECHO, INPUT);
}

double measure_distance(String sensor){
  // Check which echo pin
  char echo;
  
  if (sensor == "front"){
    echo = FRONT_ECHO;
  } 
  else if (sensor == "back"){
    echo = BACK_ECHO;
  }
  else {
    Serial.println("Unvalid echo pin...");
    return -1;
  }

  // Sending a trigger pulse
  send_trigger(sensor);
  
  // Measuring pulse lenght in us
  unsigned long pulse_time = pulseIn(echo, HIGH);
  
  // Calculating distance from sound speed and pulse time
  double distance = pulse_time * 0.000001 * VelSon / 2.0;
  return distance;
}

void send_trigger(String sensor){
  // Check which trigger pin
  char trigger;

  if (sensor == "front"){
    trigger = FRONT_TRIG;
  } 
  else if (sensor == "back"){
    trigger = BACK_TRIG;
  }
  else {
    Serial.println("Unvalid trigger pin...");
    return;
  }
  
  // Set trigger pin in low state and wait for 2 us
  digitalWrite(trigger, LOW);
  delayMicroseconds(2);
  
  // Set trigger pin in low state and wait for 10 us
  digitalWrite(trigger, HIGH);
  delayMicroseconds(10);
  
  // Comenzamos poniendo el pin Trigger en estado bajo Reset trigger pin
  digitalWrite(trigger, LOW);
}