bool state = false;

void setup() {
  // put your setup code here, to run once:
  pinMode(13, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  delay(500);
  
  if (state){
    state = false;
  } else {
    state = true;
  }

digitalWrite(13, state);
}
