#include "speedometer.h"

#define SPEEDOMETER_INT_PIN 3

// Starting reference and sampling period
uint16_t gasPedal;
uint16_t breakPedal;
double rpm = 0;
double ref= 0;

// Values found with experimentation of pwm and rpms for the motor at half capacity
double input_norm_ref = 100;
double output_norm_ref = 5000;

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

void setGasPedal(uint16_t value){
  value = max(value, 0);
  value = min(value, 1023);
  gasPedal = value;
}

void setBreakPedal(uint16_t value){
  value = max(value, 0);
  value = min(value, 1023);
  breakPedal = value;
}

void setPIDReference(double value){
  value = max(value, 0);
  ref = value;
}

void updatePIDReference(){
  double new_ref;
  if (breakPedal > 0){
    new_ref = ref - ((double)breakPedal/1023)*3000;
  }

  else if (gasPedal > 0){
    int max_rpm = getMaxRPM();
    int min_rpm = getMinRPM();
    
    new_ref = ((double)gasPedal/1023)*(max_rpm-min_rpm) + min_rpm; 
  }
  
  else{
    // Regular decay
    new_ref = 0.8*ref;
  }

  ref = new_ref;
}

void updatePIDOutput(){
  // Normalizing the value
  y = rpm/output_norm_ref;

  // Computing the error
  r = ref/output_norm_ref;
  e = r - y;
  
  // Compute the required input to the system
  u = 2.0448*e - 0.41325408*e1 - 0.08112*e2 + u1;// Ecuacion en diferencias

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
  data.gear = getGear();
  return data;
}

double getRPM(){
  return rpm;
}
