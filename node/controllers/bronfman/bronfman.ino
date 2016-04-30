/*
  Hydroponics Controller - Bronfman
 */

/* --- Libraries --- */
#include <ArduinoJson.h>

/* --- Prototypes --- */
int FloatAIntEtArondie(float valeur);
int readAverage(const int, const int, const int);
float toVoltage(const int, const int, const int);
int readAverageLumiere (const int, const int);
int getVolumetricMoistureContent (const int, const int);
void setRelay(int, boolean);
boolean controlMoisture(int, int);
int checksum(char*);

/* --- Constants --- */
// JSON / Serial
const int INPUT_LENGTH = 256;
const int OUTPUT_LENGTH = 256;
const int DATA_LENGTH = 128;
const int BAUD_RATE = 9600;
const int INTERVAL = 20;

// Soil Moisture Sensors (VH400)
const int PIN_D_SENSOR_SMC_1 = 2;
const int PIN_D_SENSOR_SMC_2 = 3;
const int PIN_D_SENSOR_SMC_3 = 4;
const int PIN_D_SENSOR_SMC_4 = 5;

// Photosensors (950 Ohm)
const int PIN_D_SENSOR_PHOTO_1 = 6;
const int PIN_D_SENSOR_PHOTO_2 = 7;

// Soil Moisture Content Relays
const int PIN_D_RELAY_SMC_1 = 8;
const int PIN_D_RELAY_SMC_2 = 9;
const int PIN_D_RELAY_SMC_3 = 10;
const int PIN_D_RELAY_SMC_4 = 11;

// Intercanopy LED Relay
const int PIN_D_RELAY_LED = 12; // set to D13 if independent

// Analog Pins
const int PIN_A_SENSOR_SMC_1 = 0;
const int PIN_A_SENSOR_SMC_2 = 1;
const int PIN_A_SENSOR_SMC_3 = 2;
const int PIN_A_SENSOR_SMC_4 = 3;
const int PIN_A_SENSOR_PHOTO_1 = 4;
const int PIN_A_SENSOR_PHOTO_2 = 5;

/* --- Variables --- */
// JSON
char data_buffer[DATA_LENGTH];
char targets_buffer[DATA_LENGTH];
char ser_buffer[OUTPUT_LENGTH];

// Relay States
boolean relay_smc_1 = false; // Drip irrigation solenoid Bed #1, south
boolean relay_smc_2 = false; // Drip irrigation solenoid Bed #2, north
boolean relay_smc_3 = false; // Drip irrigation solenoid Bed #1, south
boolean relay_smc_4 = false; // Drip irrigation solenoid Bed #2, north
boolean relay_led = false; // Intercanopy LEDS Bed #1 & #2

// Variables contenant les valeurs des capteurs
int current_smc_1 = 0;
int current_smc_2 = 0;
int current_smc_3 = 0;
int current_smc_4 = 0;
int current_photo_1 = 0;
int current_photo_2 = 0;
int target_smc_1 = 0;
int target_smc_2 = 0;
int target_smc_3 = 0;
int target_smc_4 = 0;

void setup() {

  // Initialise I/O Pins
  pinMode(PIN_D_SENSOR_SMC_1, OUTPUT);
  digitalWrite(PIN_D_SENSOR_SMC_1, LOW);
  pinMode(PIN_D_SENSOR_SMC_2, OUTPUT);
  digitalWrite(PIN_D_SENSOR_SMC_2, LOW);
  pinMode(PIN_D_SENSOR_SMC_3, OUTPUT);
  digitalWrite(PIN_D_SENSOR_SMC_3, LOW);
  pinMode(PIN_D_SENSOR_SMC_4, OUTPUT);
  digitalWrite(PIN_D_SENSOR_SMC_4, LOW);
  pinMode(PIN_D_SENSOR_PHOTO_1, OUTPUT);
  digitalWrite(PIN_D_SENSOR_PHOTO_1, LOW);
  pinMode(PIN_D_SENSOR_PHOTO_2, OUTPUT);
  digitalWrite(PIN_D_SENSOR_PHOTO_2, LOW);
  pinMode(PIN_D_RELAY_SMC_1, OUTPUT);
  digitalWrite(PIN_D_RELAY_SMC_1, HIGH);
  pinMode(PIN_D_RELAY_SMC_2, OUTPUT);
  digitalWrite(PIN_D_RELAY_SMC_2, HIGH);
  pinMode(PIN_D_RELAY_SMC_3, OUTPUT);
  digitalWrite(PIN_D_RELAY_SMC_3, HIGH);
  pinMode(PIN_D_RELAY_SMC_4, OUTPUT);
  digitalWrite(PIN_D_RELAY_SMC_4, HIGH);
  pinMode(PIN_D_RELAY_LED, OUTPUT);
  digitalWrite(PIN_D_RELAY_LED, HIGH);

  // Initialize Serial
  Serial.begin(BAUD_RATE);

  // Initialize RX Buffer
  StaticJsonBuffer<INPUT_LENGTH> json_rx;
  JsonObject& dict = json_rx.createObject();
  dict["s1"] = target_smc_1;
  dict["s2"] = target_smc_2;
  dict["s3"] = target_smc_3;
  dict["s4"] = target_smc_4;
  dict["l"] = (int)relay_led;
  dict.printTo(targets_buffer, sizeof(targets_buffer));
}

void loop() {
  delay(INTERVAL);
  StaticJsonBuffer<INPUT_LENGTH> json_rx;
  StaticJsonBuffer<OUTPUT_LENGTH> json_tx;

  // Receive
  if (Serial.available() > 0) {
    memset(&ser_buffer[0], 0, sizeof(ser_buffer));
    int i = 0;
    char c = ' ';
    while (c != '}') {
      c = Serial.read();
      if (c == '\r') {
        break;
      }
      else {
        ser_buffer[i] = c;
        i++;
      }
    }
    while (Serial.available() > 0) {
      Serial.read();  // Flush remaining characters
    }
    JsonObject& dict = json_rx.parseObject(ser_buffer);
    if (dict.success()) {
      target_smc_1 = dict["s1"];
      target_smc_2 = dict["s2"];
      target_smc_3 = dict["s3"];
      target_smc_4 = dict["s4"];
      relay_led = (boolean)dict["l"];
      dict.printTo(targets_buffer, sizeof(targets_buffer));
    }
    else {
      Serial.println("Failed!");
    }
  }

  // Read Sensors
  current_smc_1 = getVolumetricMoistureContent(PIN_D_SENSOR_SMC_1, PIN_A_SENSOR_SMC_1);
  current_smc_2 = getVolumetricMoistureContent(PIN_D_SENSOR_SMC_2, PIN_A_SENSOR_SMC_2);
  current_smc_3 = getVolumetricMoistureContent(PIN_D_SENSOR_SMC_3, PIN_A_SENSOR_SMC_3);
  current_smc_4 = toMoistureContent(PIN_D_SENSOR_SMC_4, PIN_A_SENSOR_SMC_4);
  current_photo_1 = toOhms(PIN_D_SENSOR_PHOTO_1, PIN_A_SENSOR_PHOTO_1);
  current_photo_2 = toOhms(PIN_D_SENSOR_PHOTO_2, PIN_A_SENSOR_PHOTO_2);

  // Control Irritation
  relay_smc_1 = controlMoisture(target_smc_1, current_smc_1);
  relay_smc_2 = controlMoisture(target_smc_2, current_smc_2);
  relay_smc_3 = controlMoisture(target_smc_3, current_smc_3);
  relay_smc_4 = controlMoisture(target_smc_4, current_smc_4);
  setRelay(PIN_D_RELAY_SMC_1, relay_smc_1); // Solenoid A
  setRelay(PIN_D_RELAY_SMC_2, relay_smc_2); // Solenoid B
  setRelay(PIN_D_RELAY_SMC_3, relay_smc_3); // Solenoid C
  setRelay(PIN_D_RELAY_SMC_4, relay_smc_4); // Solenoid D

  // Control Inter-canopy Lighting
  setRelay(PIN_D_RELAY_LED, relay_led);

  // Transmit
  JsonObject& dict = json_tx.createObject();
  dict["s1"] = current_smc_1;
  dict["s2"] = current_smc_2;
  dict["s3"] = current_smc_3;
  dict["s4"] = current_smc_4;
  dict["p1"] = current_photo_1;
  dict["p2"] = current_photo_2;
  dict.printTo(data_buffer, sizeof(data_buffer));
  sprintf(ser_buffer, "{\"data\":%s,\"targets\":%s,\"chksum\":%d}", data_buffer, targets_buffer, checksum(data_buffer));
  Serial.println(ser_buffer);
}

/* --- Functions --- */
// Convert Float to Int
int roundFloat(float value) {
  int iTemp = (int)value;
  float fTemp = value - iTemp;
  if (fTemp > 0.5) {
    return (int)(value + 1);
  }
  return (int)value;
}

// Read Pin Value
int readAverage(const int PIN_WRITE, const int PIN_READ, const int NUM_SAMPLES) {
  const int DELAY_MS = 100;
  int sum = 0;
  for (int i = 0; i < NUM_SAMPLES; i++) {
    digitalWrite(PIN_WRITE, HIGH);
    delay(DELAY_MS);
    sum += analogRead(PIN_READ);
    digitalWrite(PIN_WRITE, LOW);
  }
  return sum / NUM_SAMPLES;
}

// Convert to Voltage
float toVoltage(const int PIN_WRITE, const int PIN_READ, const int NUM_SAMPLES) {
  return readAverage(PIN_WRITE, PIN_READ, NUM_SAMPLES) * (5.0 / 1023.0);
}

// Return Ohms
int toOhms (const int PIN_WRITE, const int PIN_READ) {
  const int NUM_SAMPLES = 4;
  const int VIN = 5; // Arduino Voltage
  const float RESISTANCE = 975; // Ohms
  return roundFloat(RESISTANCE / ((VIN / toVoltage(PIN_WRITE, PIN_READ, NUM_SAMPLES)) - 1));
}

// capteur vh400
// retourne la teneur en eau volum�trique(Volumetric Water Content) en %
// Equation fond�e sur les calculs de la compagnie qui produit le capteur d'humidit
// http://vegetronix.com/Products/VH400/VH400-Piecewise-Curve.phtml
int toMoistureContent (const int PIN_WRITE, const int PIN_READ) {
  const int NUM_SAMPLES = 4;
  float moisture = 0.0;
  float voltage = toVoltage(PIN_WRITE, PIN_READ, NUM_SAMPLES);
  if (voltage < 1.1) {
    moisture = 10.0 * voltage - 1.0;
  }
  if (voltage < 1.3) {
    moisture = 25.0 * voltage - 17.5;
  }
  if (voltage < 1.82) {
    moisture = 48.08 * voltage - 47.5;
  }
  if (voltage < 2.2) {
    moisture = 26.32 * voltage - 7.89;
  }
  // si la valeur est en haut de 50 la pente est approximativement lin�aire
  if (voltage >= 2.2) {
    moisture = 26.32 * voltage - 7.89;
  }
  return MoistureContent;
}

// Set Relay
void setRelay(constint pin, boolean state) {
  delay(25);
  if (state) {
    digitalWrite(pin, LOW);
  }
  else {
    digitalWrite(pin, HIGH);
  }
}

// Function to determine if irrigation solenoid should be engaged/disengaged
boolean controlMoisture(int target, int current) {
  if (target > current) {
    return true;
  }
  else {
    return false;
  }
}

int checksum(char* buf) {
  int sum = 0;
  for (int i = 0; i < DATA_LENGTH; i++) {
    sum = sum + buf[i];
  }
  return sum % 256;
}

