#include "speedometer.h"

#define SPEEDOMETER_INT_PIN 3

// Starting reference and sampling period
double rpm = 0;
double speed = 0;
double ref= 0;

// Values found with experimentation of pwm and rpms for the motor at half capacity
double input_norm_ref = 100;
double output_norm_ref = 7000;

// Variables for PID controller
double r = 0;
double y = 0;
double u = 0;
double u1 = 0;
double e = 0;
double e1 = 0;
double e2 = 0;

volatile long A_count = 0;
 
void speedometerInit() {  
  // Attaching interrupt
  pinMode(SPEEDOMETER_INT_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(SPEEDOMETER_INT_PIN), increaseCount, RISING);
}

void setPIDReference(double value){
  value = max(value, 0);
  ref = value;
}

void updatePIDOutput(){
  // Normalizing the value
  y = rpm/output_norm_ref;

  // Computing the error
  r = ref/output_norm_ref;
  e = r - y;
  
  // Compute the required input to the system
  u = 1.1835*e + 0.056441*e1 - 0.000497*e2 + u1;// Ecuacion en diferencias

  // Change value from normalized to PWM
  double input_val = u*input_norm_ref; // from 0 to 255
  input_val = (input_val < 0) ? 0 : input_val;
  input_val = (input_val > 255) ? 255 : input_val;

  changeDrivePower((uint8_t)input_val);

  // Shifting the variables in time
  u1 = u;
  e2 = e1;
  e1 = e;
}

void increaseCount() {
  A_count++;
}

void resetCount(){
  A_count = 0;
}

RPMData computeRPM(double period_ms) {
  RPMData data;
  rpm = (A_count * (60000/period_ms))/100;  // sensor pulse / 100 = 1 motor revolution  
  data.rpm = rpm;
  return data;
}

SpeedData computeSpeed(){
  SpeedData data;
  speed = (rpm*2*3.14159265*0.043*3.6)/(60*3.65*2);
  data.speed = speed;
  return data;
}

double getRPM(){
  return rpm;
}
