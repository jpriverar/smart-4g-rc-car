#include "speedometer.h"

#define SPEEDOMETER_INT_PIN 3

double speedometerStartTime = 0;
int count = 0;
 
void speedometerInit() {  
  // Attaching interrupt
  pinMode(SPEEDOMETER_INT_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(SPEEDOMETER_INT_PIN), increaseCount, RISING);
}

void increaseCount() {
  count++;
}

double computeRPM(double currTime) {
  // Computing rpm based off current count and elapsed time
  double rpm = (count * (60000/(currTime - speedometerStartTime)))/(100);  // sensor pulse / 100 = 1 motor revolution

  // Resetting count and starting time
  count = 0;
  speedometerStartTime = millis();

  return rpm;
}
