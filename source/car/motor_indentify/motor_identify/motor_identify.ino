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
#define FPWM 5
#define BPWM 6
const int CHANN_A = 3;

// Values found with experimentation of pwm and rpms for the motor at half capacity
double input_norm_ref = 80;
double output_norm_ref = 65;

// Starting reference and sampling period
double sample_time = 10000; // Measure for 10 seconds
double T_sample = 1000/10;  // 10 Hz

// Noise percentage relative to the reference
double noise_percentage = 0.00; 
//-------------------------------------------------------------------------------//

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

  // Changing timer frequency for drive PWM, Timer for pins 5&6 to 7.8 kHz
  TCCR0B = TCCR0B & 0b11111000 | 0x02; // Prescaler -> 8, 7.8 kHz

  wait_start = millis();
  start_time = millis();
}

void loop() {
  // Updating the current time value
  curr_time = millis();

  /* If sample time is finished */
  if (curr_time - start_time > sample_time){
    // Printing before resetting time and rpm measurements
    Serial.println(time_measurements);
    Serial.println(input_measurements);
    Serial.println(output_measurements);
    
    time_measurements = "";
    input_measurements = "";
    output_measurements = "";

    // Saving the new start
    start_time = millis();
  }

  /* If sample time is finished */
  if (curr_time - wait_start > time_to_wait){
    // If motor is on, turn it off
    if (on) analogWrite(FPWM, 0);
    else analogWrite(FPWM, input_norm_ref);
    on ^= 1;

    // Setting time for the new period and then update start time
    time_to_wait = random(1000);
    wait_start = millis();
  }

  
  // Doing the rpm calculation
  rpm = compute_rpm(T_sample);

  // Normalizing the input and output values
  norm_output = rpm; /// output_norm_ref;
  norm_input = input_val / input_norm_ref;
  
  // Printing values
  Serial.print("RPM:");
  Serial.print(rpm);
  Serial.print(',');
  Serial.print("IN:");
  Serial.print(norm_input);
  Serial.print(',');
  Serial.print("OUT:");
  Serial.println(norm_output);

  // Saving time and rpm measurements
  time_measurements += String((curr_time - start_time)/1000.0, 6) + ' ';
  input_measurements += String(norm_input, 6) + ' ';
  output_measurements += String(norm_output, 6) + ' ';

  // Resetting count values to zero and shifting variables
  A_count = 0;

  // Waiting one second before calculating rpm measurement
  delay(T_sample);
}

void increase_A_count() {
  A_count++;
}

double compute_rpm(double period_ms) {
  float mean_count = (float)(A_count + B_count) / 2;
  double rpm = (mean_count * (60000/period_ms))/(11.0 * 46.8);  // sensor pulse / 11 = 1 motor revolution
                                                                // 46.8 motor revolution = 1 output shaft revolution
  return rpm;
}
