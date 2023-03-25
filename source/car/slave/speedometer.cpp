#include "speedometer.h"
#include "messenger.h"

#define SPEEDOMETER_INT_PIN 3

int A_count = 0;
 
void speedometerInit() {  
  // Attaching interrupt
  pinMode(SPEEDOMETER_INT_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(SPEEDOMETER_INT_PIN), increaseCount, RISING);
}

void increaseCount() {
  A_count++;
}

double computeRPM(double period_ms) {
  // Computing rpm based off current count and elapsed time
  double rpm = (A_count * (60000/period_ms))/100;  // sensor pulse / 100 = 1 motor revolution
  
  // Resetting count and starting time
  A_count = 0;
  return rpm;
}
