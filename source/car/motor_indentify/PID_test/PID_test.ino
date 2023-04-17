// Starting values for intermediate variables
int A_count = 0;
double start_time = 0;
double curr_time = 0;
double input_val = 0;
double rpm = 0;
double norm_output = 0;
double norm_input = 0;

// ----------------------------MODIFY THESE VALUES ONLY!!!------------------------//
// Pin definition
#define FPWM 5
#define BPWM 6
const int CHANN_A = 3;

// Values found with experimentation of pwm and rpms for the motor at half capacity
double input_norm_ref = 100;
double output_norm_ref = 10000;

// Starting reference and sampling period
double ref = 0;
double T_sample = 1000/3.5014;  // 3.5014 Hz

// Noise percentage relative to the reference
double noise_percentage = 0.00; 
//-------------------------------------------------------------------------------//

// Variables for PID controller
double r = 0;
double y = 0;
double u = 0;
double u1 = 0;
double e = 0;
double e1 = 0;
double e2 = 0;

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
}

void loop() {
  // If a new reference has been entered by the user
  if(Serial.available()){
    ref = Serial.readStringUntil('\n').toDouble(); // In rpms
    // Normalize the reference
    r = ref/output_norm_ref;
  }

  // Printing the reference
  Serial.print("REF:");
  Serial.print(ref);
  Serial.print(", ");

  // Computing the rpm
  rpm = compute_rpm(T_sample);
  Serial.print("RPM:");
  Serial.println(rpm);

  // Normalizing the value
  y = rpm/output_norm_ref;

  // Computing the error
  e = r - y;
  
  // Compute the required input to the system
  u = 1.1835*e - 0.056441*e1 + 0.000497*e2 + u1;// Ecuacion en diferencias

  // Change value from normalized to PWM
  input_val = u*input_norm_ref; // from 0 to 255
  input_val = (input_val < 0) ? 0 : input_val;
  input_val = (input_val > 255) ? 255 : input_val;

  // Sending the required input to the system
  analogWrite(FPWM, input_val);

  // Shifting the variables in time
  u1 = u;
  e2 = e1;
  e1 = e;

  // Resetting count values
  A_count = 0;
  
  // Waiting for the next sample
  delay(T_sample);
}

void increase_A_count() {
  A_count++;
}

double compute_rpm(double period_ms) {
  double rpm = (A_count * (60000/period_ms))/100;  // 100 sensor pulse - 1 motor revolution
  return rpm;
}
