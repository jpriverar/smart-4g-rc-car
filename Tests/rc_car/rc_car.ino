#include <Servo.h>
#include "I2Cdev.h"
#include "MPU6050_6Axis_MotionApps20.h"
#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    #include "Wire.h"
#endif
//--------------- PIN DEFINITION --------------
const char FPWM = 5;
const char BPWM = 6;
const char STEER_PIN = 11;

const char CAM_PAN_PIN = 10;
const char CAM_TILT_PIN = 9;

const char FRONT_TRIG = 7;
const char FRONT_ECHO = 8;
const char BACK_TRIG = 4;
const char BACK_ECHO = 12;

const char MPU_INTERRUPT_PIN = 2;   
//---------------------------------------------

//-------------- MEHCANICAL EXPERIMENTAL CONSTANTS --------------
// Angle endstop for camera motors
uint8_t PAN_MIN = 10;
uint8_t PAN_MAX = 180;
uint8_t PAN_CENTER = 100;
uint8_t TILT_MIN = 40;
uint8_t TILT_MAX = 100;
uint8_t TILT_CENTER = 50;

// Angle endstop for dirction motor
uint8_t STEER_MIN = 35;
uint8_t STEER_MAX = 130;
uint8_t STEER_CENTER = 80;

// Maximum allowed drive power
uint8_t MAX_POWER = 100;

// Ultrasonic Sensor
const double VelSon = 34000.0;
//---------------------------------------------------------------

//--------------------------FUNCTION PROTOTYPES------------------
void camera_config(String param, int16_t value = -1);
void steer_config(String param, int16_t value = -1);
void drive_config(String param, int16_t value = -1);
//---------------------------------------------------------------

//--------------------- APPLICATION OBJECTS ---------------------
Servo pan_servo;
Servo tilt_servo;
Servo steer_servo;
MPU6050 mpu;
//---------------------------------------------------------------

//--------------------- APPLICATION VARIABLES -------------------
// Buffer for incoming messages
String msg;

// Setting the starting cam position to the center
uint8_t cam_pan = PAN_CENTER;
uint8_t cam_tilt = TILT_CENTER;

// Setting the starting drive power and direction angle
uint8_t steer_angle = STEER_CENTER;
uint8_t drive_power = 0;
uint8_t on_drive = FPWM; // Forward direction first on
uint8_t off_drive = BPWM; 

// Ultrasonic sensor readings
bool front_us_reading = false;
bool front_collision = false;
float front_stop_dist = 10; //cm
bool back_us_reading = false;
bool back_collision = false;
float back_stop_dist = 10; //cm


// MPU control/status vars
bool dmpReady = false;  // set true if DMP init was successful
uint8_t mpuIntStatus;   // holds actual interrupt status byte from MPU
uint8_t devStatus;      // return status after each device operation (0 = success, !0 = error)
uint16_t packetSize;    // expected DMP packet size (default is 42 bytes)
uint16_t fifoCount;     // count of all bytes currently in FIFO
uint8_t fifoBuffer[64]; // FIFO storage buffer
volatile bool mpuInterrupt = false;     // indicates whether MPU interrupt pin has gone high
bool read_imu = false;  // To start continuous imu readings
double imu_read_time = 100; // 100ms between readings
double imu_start_time;
double imu_curr_time;

// orientation/motion vars
Quaternion q;           // [w, x, y, z]         quaternion container
VectorInt16 aa;         // [x, y, z]            accel sensor measurements
VectorInt16 aaReal;     // [x, y, z]            gravity-free accel sensor measurements
VectorInt16 aaWorld;    // [x, y, z]            world-frame accel sensor measurements
VectorFloat gravity;    // [x, y, z]            gravity vector
float euler[3];         // [psi, theta, phi]    Euler angle container
float ypr[3];           // [yaw, pitch, roll]   yaw/pitch/roll container and gravity vector
//---------------------------------------------------------------

void setup() {
  /*=======================IMU INITIALIZATION=======================*/
  // join I2C bus (I2Cdev library doesn't do this automatically)
  #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
      Wire.begin();
      Wire.setClock(400000); // 400kHz I2C clock. Comment this line if having compilation difficulties
  #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
      Fastwire::setup(400, true);
  #endif
  
  Serial.begin(115200);
  while (!Serial); 

  // initialize MPU device
  Serial.println(F("Initializing I2C devices..."));
  mpu.initialize();
  pinMode(MPU_INTERRUPT_PIN, INPUT);

  // verify MPU connection
  Serial.println(F("Testing device connections..."));
  Serial.println(mpu.testConnection() ? F("MPU6050 connection successful") : F("MPU6050 connection failed"));

  // load and configure the MPU DMP
  Serial.println(F("Initializing DMP..."));
  devStatus = mpu.dmpInitialize();

  // supply your own MPU gyro offsets here, scaled for min sensitivity
  mpu.setXGyroOffset(95);
  mpu.setYGyroOffset(80);
  mpu.setZGyroOffset(31);
  mpu.setZAccelOffset(1514); // 1688 factory default for my test chip

  // make sure it worked (returns 0 if so)
  if (devStatus == 0) {
      // Calibration Time: generate offsets and calibrate our MPU6050
      mpu.CalibrateAccel(6);
      mpu.CalibrateGyro(6);
      mpu.PrintActiveOffsets();
      // turn on the DMP, now that it's ready
      Serial.println(F("Enabling DMP..."));
      mpu.setDMPEnabled(true);

      // enable Arduino interrupt detection
      Serial.print(F("Enabling interrupt detection (Arduino external interrupt "));
      Serial.print(digitalPinToInterrupt(MPU_INTERRUPT_PIN));
      Serial.println(F(")..."));
      attachInterrupt(digitalPinToInterrupt(MPU_INTERRUPT_PIN), dmpDataReady, RISING);
      mpuIntStatus = mpu.getIntStatus();

      // set our DMP Ready flag so the main loop() function knows it's okay to use it
      Serial.println(F("DMP ready! Waiting for first interrupt..."));
      dmpReady = true;

      // get expected DMP packet size for later comparison
      packetSize = mpu.dmpGetFIFOPacketSize();
  } else {
      // ERROR!
      // 1 = initial memory load failed
      // 2 = DMP configuration updates failed
      // (if it's going to break, usually the code will be 1)
      Serial.print(F("DMP Initialization failed (code "));
      Serial.print(devStatus);
      Serial.println(F(")"));
  }
  /*==================IMU INITIALIZATION==================*/
  
  // Drive pins
  pinMode(FPWM, OUTPUT);
  pinMode(BPWM, OUTPUT);
  pinMode(STEER_PIN, OUTPUT);

  // Camera pins
  pinMode(CAM_PAN_PIN, OUTPUT);
  pinMode(CAM_TILT_PIN, OUTPUT);

  // Ultrasonic sensor pins
  pinMode(FRONT_TRIG, OUTPUT);
  pinMode(FRONT_ECHO, INPUT);
  pinMode(BACK_TRIG, OUTPUT);
  pinMode(BACK_ECHO, INPUT);

 // Attaching pins to servo instances
  pan_servo.attach(CAM_PAN_PIN);
  tilt_servo.attach(CAM_TILT_PIN);
  steer_servo.attach(STEER_PIN);
  
  // Setting camera to the center
  change_pan_angle(cam_pan);
  change_tilt_angle(cam_tilt);

  // Setting drive and steer
  change_steer_angle(steer_angle);
  change_drive_direction(1);
  change_drive_power(drive_power);

  // Changing timer frequency for drive PWM, Timer for pins 5&6 to 7.8 kHz
  TCCR0B = TCCR0B & 0b11111000 | 0x02; // Prescaler -> 8, 7.8 kHz
}

void loop() {
  // If there are any incoming messages
  if(Serial.available()){
    msg = Serial.readStringUntil('\n');
    parse_message(msg);
  }

  if (front_us_reading){
    double dist = measure_distance("front");
    
    Serial.print("front distance: ");
    Serial.println(dist);

    if (front_collision){
      if (dist < front_stop_dist) stop_drive();
    }
  }

  if (back_us_reading){
    double dist = measure_distance("back");
    
    Serial.print("back distance: ");
    Serial.println(dist);

    if (back_collision){
      if (dist < back_stop_dist) stop_drive();
    }
  }

  if (read_imu){
    if (imu_curr_time - imu_start_time >= imu_read_time){
      compute_6dof();
      imu_start_time = millis();
    }
    imu_curr_time = millis();
  }
  
}

void help(){
  Serial.println(F("|---------------------COMMAND SYNTAX----------------------"));
  Serial.println(F("  {COMMAND}{NUMERICAL VALUE TO PASS THE COMMAND}          "));
  Serial.println(F("  SC130 - Will set the steer direction value to 130°   "));
  Serial.println();
  Serial.println(F("|------------------DIRECTION COMMANDS--------------------|"));
  Serial.println(F("  SC - Change steer direcion in a range between 0-255     "));
  Serial.println(F("  SI - Increase the steer direction                       "));
  Serial.println(F("  SD - Decrease the steer direction                       "));
  Serial.println(F("  SM - Set steer direction max endstop                    "));
  Serial.println(F("  Sm - Set steer direction min endstop                    "));
  Serial.println(F("  Sc - Set steer direction center                         "));
  Serial.println();
  Serial.println(F("|-------------------CAMERA COMMANDS----------------------|"));
  Serial.println(F("  PC - Change camera pan angle in a range between 0-255   "));
  Serial.println(F("  PI - Increase camera pan angle                          "));
  Serial.println(F("  PD - Decrease camera pan angle                          "));
  Serial.println(F("  PM - Set camera pan angle max endstop                   "));
  Serial.println(F("  Pm - Set camera pan angle min endstop                   "));
  Serial.println(F("  Pc - Set camera pan angle center                        "));
  Serial.println(F("  TC - Change camera tilt angle in a range between 0-255  "));
  Serial.println(F("  TI - Increase camera tilt angle                         "));
  Serial.println(F("  TD - Decrease camera tilt angle                         "));
  Serial.println(F("  TM - Set camera tilt angle max endstop                  "));
  Serial.println(F("  Tm - Set camera tilt angle min endstop                  "));
  Serial.println(F("  Tc - Set camera tilt angle center                       "));
  Serial.println();
  Serial.println(F("|--------------------DRIVE COMMANDS----------------------|"));
  Serial.println(F("  DP - Drive the motor forward in a range between 0-255   "));
  Serial.println(F("  DI - Increase the drive power                           "));
  Serial.println(F("  DD - Decrease the drive power                           "));
  Serial.println(F("  DC - Change the drive direction 1-forward, 0-backward   "));
  Serial.println(F("  DS - Stop the drive                                     "));
  Serial.println(F("  DM - Set drive maximum allowed power                    "));
  Serial.println();
  Serial.println(F("|----------------ULTRASONIC SENSOR COMMANDS--------------|"));
  Serial.println(F("  FO - Front ultrasonic sensor one shot reading           "));
  Serial.println(F("  FC - Front ultrasonic sensor continuous reading         "));
  Serial.println(F("  FS - Stop front ultrasonic sensor reading               "));
  Serial.println(F("  BO - Back ultrasonic sensor one shot reading            "));
  Serial.println(F("  BC - Back ultrasonic sensor continuous reading          "));
  Serial.println(F("  BS - Stop back ultrasonic sensor reading                "));
  Serial.println();
  Serial.println(F("|----------------------IMU COMMANDS----------------------|"));
  Serial.println(F("  Ic - Calibrate offset values for the imu, takes 5-10m   "));
  Serial.println(F("  IC - Read IMU computed values continuously              "));
  Serial.println(F("  IS - Stop continuous IMU readings                       "));
  Serial.println(F("  IT - Change time between continuous IMU readings        "));
  Serial.println();
  Serial.println(F("|-------------COLLISION DETECTION COMMANDS---------------|"));
  Serial.println(F("  FE - Front side collision detection enabled             "));
  Serial.println(F("  FD - Front side collision detection disabled            "));
  Serial.println(F("  F! - Set front emergecy stop threshold distance         "));
  Serial.println(F("  BE - Back side collision detection enabled              "));
  Serial.println(F("  BD - Back side collision detection disabled             "));
  Serial.println(F("  B! - Set back emergecy stop threshold distance          "));
}

void parse_message(String msg){
  int16_t input_value = -1;
  String command = msg.substring(0,2);

  if (msg.length() > 2) input_value = msg.substring(2).toInt();
  //Serial.println(input_value);
  
  if (msg == "help"){help();}
  else if (command ==  "SC"){change_steer_angle(input_value);}
  else if (command == "SI"){increment_steer_angle(input_value);}
  else if (command == "SD"){increment_steer_angle(-input_value);}
  else if (command == "SM"){steer_config("max", input_value);}
  else if (command == "Sm"){steer_config("min", input_value);}
  else if (command == "Sc"){steer_config("center", input_value);}

  else if (command == "PC"){change_pan_angle(input_value);}
  else if (command == "PI"){increment_pan_angle(input_value);}
  else if (command == "PD"){increment_pan_angle(-input_value);}
  else if (command == "PM"){camera_config("pan max", input_value);}
  else if (command == "Pm"){camera_config("pan min", input_value);}
  else if (command == "Pc"){camera_config("pan center", input_value);}
  
  else if (command == "TC"){change_tilt_angle(input_value);}
  else if (command == "TI"){increment_tilt_angle(input_value);}
  else if (command == "TD"){increment_tilt_angle(-input_value);}
  else if (command == "TM"){camera_config("tilt max", input_value);}
  else if (command == "Tm"){camera_config("tilt min", input_value);}
  else if (command == "Tc"){camera_config("tilt center", input_value);}

  else if (command == "DP"){change_drive_power(input_value);}
  else if (command == "DI"){increment_drive_power(input_value);}
  else if (command == "DD"){increment_drive_power(-input_value);}
  else if (command == "DS"){stop_drive();}
  else if (command == "DC"){change_drive_direction(input_value);}
  else if (command == "DM"){drive_config("max", input_value);}
  
  else if (command == "FO"){Serial.println(measure_distance("front"));}
  else if (command == "FC"){front_us_reading=true;}
  else if (command == "FS"){front_us_reading=false;}
  else if (command == "BO"){Serial.println(measure_distance("back"));}
  else if (command == "BC"){back_us_reading=true;}
  else if (command == "BS"){back_us_reading=false;}

  else if (command == "Ic"){Serial.println("Calibration function not implemented yet...");}
  else if (command == "IC"){read_imu = true;}
  else if (command == "IS"){read_imu = false;}
  else if (command == "IT"){imu_read_time = input_value; imu_start_time = millis();}
  
  else {Serial.println("Unknown command, try again...");}
}

// INTERRUPT ROUTINE
void dmpDataReady() {
    mpuInterrupt = true;
}

void compute_6dof(){
  if (mpu.dmpGetCurrentFIFOPacket(fifoBuffer)) {
    mpu.dmpGetQuaternion(&q, fifoBuffer);
    mpu.dmpGetGravity(&gravity, &q);
    mpu.dmpGetYawPitchRoll(ypr, &q, &gravity);
    mpu.dmpGetAccel(&aa, fifoBuffer);
    mpu.dmpGetLinearAccel(&aaReal, &aa, &gravity);

    // Gyroscope values
    Serial.print("ypr\t");
    Serial.print(ypr[0] * 180/M_PI);
    Serial.print("\t");
    Serial.print(ypr[1] * 180/M_PI);
    Serial.print("\t");
    Serial.print(ypr[2] * 180/M_PI);
    Serial.print("\t");
  
    // Acceleration values
    Serial.print("areal\t");
    Serial.print(aaReal.x);
    Serial.print("\t");
    Serial.print(aaReal.y);
    Serial.print("\t");
    Serial.println(aaReal.z);
  }
}

double measure_distance(String sensor){
  // Check which echo pin
  char echo;
  
  if (sensor == "front"){
    echo = FRONT_ECHO;
  } 
  else if (sensor == "back"){
    echo = BACK_ECHO;
  }
  else {
    Serial.println("Unvalid echo pin...");
    return;
  }

  // Sending a trigger pulse
  send_trigger(sensor);
  
  // Measuring pulse lenght in us
  unsigned long pulse_time = pulseIn(echo, HIGH);
  
  // Calculating distance from sound speed and pulse time
  double distance = pulse_time * 0.000001 * VelSon / 2.0;
  return distance;
}

void send_trigger(String sensor){
  // Check which trigger pin
  char trigger;

  if (sensor == "front"){
    trigger = FRONT_TRIG;
  } 
  else if (sensor == "back"){
    trigger = BACK_TRIG;
  }
  else {
    Serial.println("Unvalid trigger pin...");
    return;
  }
  
  // Set trigger pin in low state and wait for 2 us
  digitalWrite(trigger, LOW);
  delayMicroseconds(2);
  
  // Set trigger pin in low state and wait for 10 us
  digitalWrite(trigger, HIGH);
  delayMicroseconds(10);
  
  // Comenzamos poniendo el pin Trigger en estado bajo Reset trigger pin
  digitalWrite(trigger, LOW);
}

void change_pan_angle(uint8_t angle){
    if (angle > PAN_MAX){angle = PAN_MAX;}
    else if (angle < PAN_MIN){angle = PAN_MIN;}

    // Saving the angle in the cam_pan variable
    cam_pan = angle;

    // Updating the angle
    pan_servo.write(cam_pan);
}

void increment_pan_angle(uint8_t inc_angle){
  uint8_t input_value = cam_pan + inc_angle;
  change_pan_angle(input_value);
}

void change_tilt_angle(uint8_t angle){
    if (angle > TILT_MAX){angle = TILT_MAX;}
    else if (angle < TILT_MIN){angle = TILT_MIN;}
    
    // Saving the angle in the cam_tilt variable
    cam_tilt = angle;

    // Updating the angle
    tilt_servo.write(cam_tilt);
}

void increment_tilt_angle(uint8_t inc_angle){
  uint8_t input_value = cam_tilt + inc_angle;
  change_tilt_angle(input_value);
}

void change_steer_angle(uint8_t angle){
    if (angle > STEER_MAX){angle = STEER_MAX;}
    else if (angle < STEER_MIN){angle = STEER_MIN;}

    // Saving the angle in the steer_angle variable
    steer_angle = angle;

    // Updating the angle
    steer_servo.write(angle);
}

void increment_steer_angle(uint8_t inc_angle){
  uint8_t input_value = steer_angle + inc_angle;
  change_steer_angle(input_value);
}

void change_drive_power(uint8_t power){
  if (power > MAX_POWER){power = MAX_POWER;}

  // Saving the angle in the steer_angle variable
  drive_power = power;

  // Updating the angle
  analogWrite(on_drive, power);
  analogWrite(off_drive, 0);
}

void increment_drive_power(uint8_t power){
  uint8_t input_value = drive_power + power;
  change_drive_power(input_value);
}

void stop_drive(){
  change_drive_power(0);
}

void change_drive_direction(uint8_t dir){
  // Stopping motors before change direction
  stop_drive();
  
  // Forward - dir = 1
  if (dir){
    on_drive = FPWM;
    off_drive = BPWM;  
  } else {
  // Backwards - dir = 0
    on_drive = BPWM;
    off_drive = FPWM;
  }
}

void camera_config(String param, int16_t value = -1){
  // GET parameter values
  if (value == -1){
    if (param == "pan min") Serial.println(PAN_MIN);
    else if (param == "pan max") Serial.println(PAN_MAX);
    else if (param == "pan center") Serial.println(PAN_CENTER);
    else if (param == "tilt min") Serial.println(TILT_MIN);
    else if (param == "tilt max") Serial.println(TILT_MAX);
    else if (param == "tilt center") Serial.println(TILT_CENTER);
    else Serial.println(F("Unknown camera configuration parameter..."));
    
  } else {
  // SET parameter values
    if (param == "pan min"){
      if (value >= 0){
        PAN_MIN = value; 
        Serial.println(F("Camera pan minimum endstop changed..."));
      } else {
        PAN_MIN = 0;
        Serial.println(F("Unvalid value for pan minimum endstop, setting to absolute minimum"));
      }
    }
    else if (param == "pan max"){
      if (value <= 180){
        PAN_MAX = value; 
        Serial.println(F("Camera pan minimum endstop changed..."));
      } else {
        PAN_MAX = 180;
        Serial.println(F("Unvalid value for pan maximum endstop, setting to absolute maximum"));
      }
    }
    else if (param == "pan center"){
      if (value >= PAN_MIN && value <= PAN_MAX){
        PAN_CENTER = value; 
        Serial.println(F("Camera pan center value changed..."));
      } else {
        Serial.println(F("Unvalid center value, value must be between PAN_MIN and PAN_MAX"));
      }
      
    }
    else if (param == "tilt min"){
      if (value >= 0){
        TILT_MIN = value; 
        Serial.println(F("Camera tilt minimum endstop changed..."));
      } else {
        TILT_MIN = 0;
        Serial.println(F("Unvalid value for tilt minimum endstop, setting to absolute minimum"));
      }
    }
    else if (param == "tilt max"){
      if (value <= 180){
        TILT_MAX = value; 
        Serial.println(F("Camera tilt minimum endstop changed..."));
      } else {
        TILT_MAX = 180;
        Serial.println(F("Unvalid value for tilt maximum endstop, setting to absolute maximum"));
      }
    }
    else if (param == "tilt center"){
      if (value >= TILT_MIN && value <= TILT_MAX){
        TILT_CENTER = value; 
        Serial.println(F("Camera tilt center value changed..."));
      } else {
        Serial.println(F("Unvalid center value, value must be between TILT_MIN and TILT_MAX"));
      }
    }
    else Serial.println(F("Unknown camera configuration parameter..."));
  }
}

void steer_config(String param, int16_t value = -1){
  // GET parameter value
  if (value == -1){
    if (param == "min") Serial.println(STEER_MIN);
    else if (param == "max") Serial.println(STEER_MAX);
    else if (param == "center") Serial.println(STEER_CENTER);
    else Serial.println(F("Unknown steer configuration parameter..."));
    
  } else {
  // SET parameter values
    if (param == "min"){
      if (value >= 0){
        STEER_MIN = value; 
        Serial.println(F("Steer direction minimum endstop changed..."));
      } else {
        STEER_MIN = 0;
        Serial.println(F("Unvalid value for steer minimum endstop, setting to absolute minimum"));
      }
    }
    else if (param == "max"){
      if (value >= 180){
        STEER_MAX = value; 
        Serial.println(F("Steer direction minimum endstop changed..."));
      } else {
        STEER_MAX = 180;
        Serial.println(F("Unvalid value for steer maximum endstop, setting to absolute maximum"));
      }
    }
    else if (param == "center"){
      if (value >= STEER_MIN && value <= STEER_MAX){
        STEER_CENTER = value; 
        Serial.println(F("Steer direction center value changed..."));
      } else {
        Serial.println(F("Unvalid center value, value must be between STEER_MIN and STEER_MAX"));
      }
    }
    else Serial.println(F("Unknown steer configuration parameter..."));
  }
}

void drive_config(String param, int16_t value = -1){
  // GET parameter value
  if (value == -1){
    if (param == "max") Serial.println(MAX_POWER);
    else Serial.println(F("Unknown steer configuration parameter..."));
    
  } else {
  // SET parameter values
    if (param == "max"){
      if (value <= 255){
        MAX_POWER = value; 
        Serial.println(F("Maximum allowed power changed..."));
      } else {
        MAX_POWER = 255;
        Serial.println(F("Unvalid value for maximum power, setting to absolute maximum"));
      }
    } else Serial.println(F("Unknown steer configuration parameter..."));
  }
}
