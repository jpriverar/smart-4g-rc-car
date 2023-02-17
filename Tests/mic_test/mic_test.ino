// set prescale to 16
bitSet(ADCSRA,ADPS2) ;
bitClear(ADCSRA,ADPS1) ;
bitClear(ADCSRA,ADPS0) ;

int validate_adc_frequency(int channel){
  int start = millis();
  int val;
  long int freq = 0;
  
  while ((millis() - start) < 1000){
    val = analogRead(0);
    freq++;
  }
  return freq;
}

void setup() {
  Serial.begin(19200);

  int freq;
  freq = validate_adc_frequency(0);
  Serial.print(freq);
  Serial.println(" Hz");
}

void loop() {
  //int mic_val = analogRead(0); // Value from 0 to 1,023 - 10 bit resolution
  //float mic_val_scaled = (float)mic_val*32767/1023; // Value scaled to 32,768 - 15 bit resolution
  
  //Serial.println(mic_val_scaled);
}
