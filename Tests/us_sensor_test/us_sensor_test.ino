#define ultrasoundTrigger 7 
#define ultrasoundEcho 8 
#define pulseLengthDistanceRatio 0.5 * 0.343
volatile unsigned long msStart; 
volatile float ultrasoundDistance = -1; 
unsigned long usPulse; 

void setup() {
Serial.begin(9600);
pinMode(ultrasoundEcho, INPUT); 
pinMode(ultrasoundTrigger, OUTPUT); 
digitalWrite(ultrasoundTrigger, HIGH); // LOW to trigger 
attachInterrupt(digitalPinToInterrupt(ultrasoundEcho), isr, CHANGE); 
} 
void isr() {
  Serial.println("Entered interrupt");
  if (digitalRead(ultrasoundEcho) == LOW) {
    if (millis() - msStart > 40) {
      // newly triggered next event is echo HIGH for pulse start
      Serial.print("Hello"); 
      } 
    else { // must be distance 
      usPulse = micros() - usPulse;
      ultrasoundDistance = usPulse * pulseLengthDistanceRatio;
      } 
  }
  else { // echo is HIGH 
   if (millis() - msStart > 40) {
      // post trigger timeout
      Serial.print("Here"); 
    } 
    else { 
      usPulse = micros(); // pulse start 
    }
  }
} 
void loop() {
  if (millis() - msStart > 60) { // every 50ms 
    msStart = millis(); 
    sendTrigger();
    Serial.println("Sending trigger"); 
  }
  else if (ultrasoundDistance > 0) { 
    Serial.print(ultrasoundDistance); 
    Serial.println("mm"); 
    ultrasoundDistance = -1; 
  }
}

void sendTrigger() {
  digitalWrite(ultrasoundTrigger, LOW);
  delayMicroseconds(2);
  
  digitalWrite(ultrasoundTrigger, HIGH);
  delayMicroseconds(10);
  
  digitalWrite(ultrasoundTrigger, LOW);
}
