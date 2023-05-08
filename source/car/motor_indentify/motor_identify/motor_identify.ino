#include <Servo.h>

#define STEER_PIN 11

// Starting values for intermediate variables
int A_count = 0;
double start_time = 0;
double curr_time = 0;
double input_val = 0;
double rpm = 0;
double norm_output = 0;
double norm_input = 0;

// To generate PRBS
double time_to_wait = 50;
double wait_start = 0;
bool on = false;

String input_measurements = "";
String time_measurements = "";
String output_measurements = "";

// ----------------------------MODIFY THESE VALUES ONLY!!!------------------------//
// Pin definition
#define FPWM 6
#define BPWM 5
const int CHANN_A = 3;

// Values found with experimentation of pwm and rpms for the motor at half capacity
double input_norm_ref = 100;
double output_norm_ref = 5000;

// Starting reference and sampling period
double sample_time = 20000; // Measure for 20 seconds
double T_sample = 1000/50;  // 100 Hz

// Noise percentage relative to the reference
double noise_percentage = 0.00; 
//-------------------------------------------------------------------------------//

Servo steerServo;

void setup() {
  // Initialize Serial
  Serial.begin(115200);
  
  // Pins for motor control and encoder readings
  pinMode(FPWM, OUTPUT);
  pinMode(BPWM, OUTPUT);
  pinMode(CHANN_A, INPUT);

  // Attaching interrups 
  attachInterrupt(digitalPinToInterrupt(CHANN_A), increase_A_count, RISING);

  // Starting motor rotation
  analogWrite(FPWM, 0);
  analogWrite(BPWM, 0);

  pinMode(STEER_PIN, OUTPUT);
  steerServo.attach(STEER_PIN);
  steerServo.write(80);
  

  wait_start = millis();
  start_time = millis();
}

void loop() {
  // Updating the current time value
  curr_time = millis();

  /* If sample time is finished */
  if (curr_time - start_time > sample_time){
    Serial.print("Done");
    analogWrite(FPWM, 0);
    while(1){}
  }

  /* If sample time is finished */
  if (curr_time - wait_start > time_to_wait){
    // If motor is on, turn it off
    if (on) input_val = 0;
    else input_val = input_norm_ref;
    
    analogWrite(FPWM, input_val);
    on ^= 1;
    
    // Setting time for the new period and then update start time
    time_to_wait = (on)? random(1000, 5000) : random(500, 2500);
    wait_start = millis();
  }
  
  // Doing the rpm calculation
  rpm = compute_rpm(T_sample);

  // Normalizing the input and output values
  norm_output = rpm / output_norm_ref;
  norm_input = input_val / input_norm_ref;
  
  // Printing values
  Serial.print("t:");
  Serial.print((curr_time - start_time)/1000.0);
  Serial.print(',');
  Serial.print("IN:");
  Serial.print(norm_input);
  Serial.print(',');
  Serial.print("OUT:");
  Serial.println(norm_output);

  // Resetting count values to zero and shifting variables
  A_count = 0;

  // Waiting one second before calculating rpm measurement
  delay(T_sample);
}

void increase_A_count() {
  A_count++;
}

double compute_rpm(double period_ms) {
  double rpm = (A_count * (60000/period_ms))/100;  // sensor pulse / 11 = 1 motor revolution
                                                                // 46.8 motor revolution = 1 output shaft revolution
  return rpm;
}
