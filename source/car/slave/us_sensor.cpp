#include "us_sensor.h"

#define FRONT_TRIG 7
#define FRONT_ECHO 8
#define BACK_TRIG 4
#define BACK_ECHO 12

const double VelSon = 34300.0;   // cm/s
unsigned long defaultTimeout = 10000; //0.008 sec, approx 1 meter go and 1 meter back

void usSensorInit(){
  pinMode(FRONT_TRIG, OUTPUT);
  pinMode(FRONT_ECHO, INPUT);
  pinMode(BACK_TRIG, OUTPUT);
  pinMode(BACK_ECHO, INPUT);
}

double measureDistance(uint8_t echoPin, uint8_t triggerPin, unsigned long timeout=defaultTimeout){
  // Sending a trigger pulse
  sendTrigger(triggerPin);
  
  // Measuring pulse lenght in us
  unsigned long pulseTime = pulseIn(echoPin, HIGH, timeout);
  
  // Calculating distance from sound speed and pulse time
  double distance = pulseTime * 0.000001 * VelSon / 2.0;
  return distance;
}

USSensorData measureFrontDistance(){
  USSensorData data;
  data.side = 1;
  data.distance = measureDistance(FRONT_ECHO, FRONT_TRIG);
  return data;
}

USSensorData measureBackDistance(){
  USSensorData data;
  data.side = 0;
  data.distance = measureDistance(BACK_ECHO, BACK_TRIG);
  return data;
}

void sendTrigger(uint8_t triggerPin){
  // Set trigger pin in low state and wait for 2 us
  digitalWrite(triggerPin, LOW);
  delayMicroseconds(2);
  
  // Set trigger pin in low state and wait for 10 us
  digitalWrite(triggerPin, HIGH);
  delayMicroseconds(10);
  
  // Comenzamos poniendo el pin Trigger en estado bajo Reset trigger pin
  digitalWrite(triggerPin, LOW);
}

void sendFrontTrigger(){
  sendTrigger(FRONT_TRIG);
}

void sendBackTrigger(){
  sendTrigger(BACK_TRIG);
}
