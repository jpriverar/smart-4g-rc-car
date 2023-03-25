int angle = 150;
int pot;
char dir = 1;

void setup() {
  Serial.begin(9600);
  pinMode(46, OUTPUT);
  analogWrite(46,angle);
}

void loop() {
  if (dir && (angle < 200)){
    angle++;
    analogWrite(46, angle);
  }
  else if (!dir && (angle > 150)){
    angle--;
    analogWrite(46, angle);
  }
  else {dir ^= 1;}
  /*
  pot = analogRead(0);
  angle = ((float)pot/1023*255);
  Serial.print(pot);
  Serial.print(' ');
  Serial.println(angle);
  analogWrite(46, angle);
  */
}
