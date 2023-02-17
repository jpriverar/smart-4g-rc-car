int SENSOR_PIN = 0; // center pin of the potentiometer
int RPWM_Output = 5; // Arduino PWM output pin 5; connect to IBT-2 pin 1 (RPWM)
int LPWM_Output = 6; // Arduino PWM output pin 6; connect to IBT-2 pin 2 (LPWM)

void setup() {
 Serial.begin(9600);
 pinMode(RPWM_Output, OUTPUT);
 pinMode(LPWM_Output, OUTPUT);

 /*  TO CHANGE PWM PINS FREQUENCY
 *   There are three such Timer/Counter registers: TCCR0B, TCCR1B, and TCCR2B.Since there are three different prescalers, the six PWM pins are broken up into three pairs, 
 *   each pair having its own prescaler. For instance, Arduino pins 6 and 5 are both controlled by TCCR0B, so you can set Arduino pins 6 and 5 to output a PWM signal at 
 *   one frequency. Arduino pins 9 and 10 are controlled by TCCR1B, so they can be set at a different frequency from pins 6 and 5. Arduino pins 11 and 3 are controlled by 
 *   TCCR2B, so they may be set at a third frequency. But you can't set different frequencies for pins that are controlled by the sameprescaler (e.g. pins 6 and 5 must be 
 *   at the same frequency).
 *   https://arduino.stackexchange.com/questions/14333/arduino-timers-how-they-work
 *   */
 // Timer for pins 5&6
 TCCR0B = TCCR0B & 0b11111000 | 0x02; // Prescaler -> 8, 7.8 kHz
 
}

void loop() {
 /*if(Serial.available()){
    String msg = Serial.readStringUntil('\n');
    parse_message(msg);
  }*/
 int sensorValue = analogRead(SENSOR_PIN);
 // sensor value is in the range 0 to 1023
 // the lower half of it we use for reverse rotation; the upper half for forward rotation
 if (sensorValue < 512)
 {
 // reverse rotation
 int reversePWM = -(sensorValue - 511) / 2;
 analogWrite(LPWM_Output, 0);
 analogWrite(RPWM_Output, reversePWM);
 }
 else
 {
 // forward rotation
 int forwardPWM = (sensorValue - 512) / 2;
 analogWrite(LPWM_Output, forwardPWM);
 analogWrite(RPWM_Output, 0);
 }
}

void parse_message(String msg){
  String command = msg.substring(0,2);
  int input_value;
  
  if (command ==  "MF"){ // To move the motor forward
    input_value = msg.substring(2).toInt();
    analogWrite(LPWM_Output, input_value);
    analogWrite(RPWM_Output, 0);
  }
  else if (command == "MB"){ // To move the motor backwards
    input_value = msg.substring(2).toInt();
    analogWrite(LPWM_Output, 0);
    analogWrite(RPWM_Output, input_value);
  }
  else {
    Serial.println("Unknown command, try again...");
  }
}
