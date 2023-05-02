#define LEDS A0
#define BUZZER A1

char ledState = 0;
char buzzerState = 0;

void setup() {
  pinMode(LEDS, OUTPUT);
  pinMode(BUZZER, OUTPUT);
}

void loop() {
  digitalWrite(LEDS, ledState);
  digitalWrite(BUZZER, buzzerState);

  ledState ^= 1;
  buzzerState ^= 1;

  delay(1500);
}
