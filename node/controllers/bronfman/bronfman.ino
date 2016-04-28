/*
  Hydroponics Controller - Bronfman
*/

/* --- Libraries --- */
#include <ArduinoJson.h>

/* --- Constants --- */
// JSON / Serial
const int INPUT_LENGTH = 512;
const int OUTPUT_LENGTH = 512;
const int DATA_LENGTH = 256;
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
// Light Relays
const int PIN_D_RELAY_PHOTO_1 = 12;
const int PIN_D_RELAY_PHOTO_2 = 13;
// Analog Pins
const int PIN_A_SENSOR_SMC_1 = 0;
const int PIN_A_SENSOR_SMC_2 = 1;
const int PIN_A_SENSOR_SMC_3 = 2;
const int PIN_A_SENSOR_SMC_4 = 3;
const int PIN_A_SENSOR_PHOTO_1 = 4;
const int PIN_A_SENSOR_PHOTO_2 = 5;

/* --- Variables --- */
// JSON
char tx_buffer[OUTPUT_LENGTH];
char data_buffer[DATA_LENGTH];
char targets_buffer[DATA_LENGTH];
char rx_buffer[INPUT_LENGTH];
StaticJsonBuffer<INPUT_LENGTH> json_rx;
StaticJsonBuffer<OUTPUT_LENGTH> json_tx;

// Relay States
bool relay_smc_1 = false;
bool relay_smc_2 = false;
bool relay_smc_3 = false;
bool relay_smc_4 = false;
bool relay_photo_1 = false;
bool relay_photo_2 = false;

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
int target_photo_1 = 0;
int target_photo_2 = 0;

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
  pinMode(PIN_D_RELAY_PHOTO_1, OUTPUT);
  digitalWrite(PIN_D_RELAY_PHOTO_1, HIGH);
  pinMode(PIN_D_RELAY_PHOTO_2, OUTPUT);
  digitalWrite(PIN_D_RELAY_PHOTO_2, HIGH);

  // Initialize Serial
  Serial.begin(BAUD_RATE);
}

void loop() {
  delay(INTERVAL);

  // Receive
  if (Serial.available() > 0) {
    int i = 0;
    char c = ' ';
    while (c != '}') {
      c = Serial.read();
      if (c == '\r') {
        break;
      }
      else {
        rx_buffer[i] = c;
        i++;
      }
    }
    while (Serial.available() > 0) {
      Serial.read();  // Flush remaining characters
    }
    JsonObject& dict_rx = json_rx.parseObject(rx_buffer);
    if (dict_rx.success()) {
      target_smc_1 = dict_rx["smc1"];
      target_smc_2 = dict_rx["smc2"];
      target_smc_3 = dict_rx["smc3"];
      target_smc_4 = dict_rx["smc4"];
      target_photo_1 = dict_rx["photo1"];
      target_photo_2 = dict_rx["photo2"];
      dict_rx.printTo(targets_buffer, sizeof(targets_buffer));
    }
  }
  else {
    JsonObject& dict_rx = json_rx.createObject();
    dict_rx["smc1"] = target_smc_1;
    dict_rx["smc2"] = target_smc_2;
    dict_rx["smc3"] = target_smc_3;
    dict_rx["smc4"] = target_smc_4;
    dict_rx["photo1"] = target_photo_1;
    dict_rx["photo2"] = target_photo_2;
    dict_rx.printTo(targets_buffer, sizeof(targets_buffer));
  }

  // Read Sensors
  current_smc_1 = litValeurHumidite(PIN_D_SENSOR_SMC_1, PIN_A_SENSOR_SMC_1);
  current_smc_2 = litValeurHumidite(PIN_D_SENSOR_SMC_2, PIN_A_SENSOR_SMC_2);
  current_smc_3 = litValeurHumidite(PIN_D_SENSOR_SMC_3, PIN_A_SENSOR_SMC_3);
  current_smc_4 = litValeurHumidite(PIN_D_SENSOR_SMC_4, PIN_A_SENSOR_SMC_4);
  current_photo_1 = litValeurCapteurLumiere(PIN_D_SENSOR_PHOTO_1, PIN_A_SENSOR_PHOTO_1);
  current_photo_2 = litValeurCapteurLumiere(PIN_D_SENSOR_PHOTO_2, PIN_A_SENSOR_PHOTO_2);

  // Decide States
  relay_smc_1 = controlMoisture(target_smc_1, current_smc_1);
  relay_smc_2 = controlMoisture(target_smc_2, current_smc_2);
  relay_smc_3 = controlMoisture(target_smc_3, current_smc_3);
  relay_smc_4 = controlMoisture(target_smc_4, current_smc_4);
  relay_photo_1 = controlLighting(target_photo_1, current_photo_1);
  relay_photo_2 = controlLighting(target_photo_2, current_photo_2);

  // Set Relays
  setRelay(PIN_D_RELAY_SMC_1, relay_smc_1); // Solenoid A
  setRelay(PIN_D_RELAY_SMC_2, relay_smc_2); // Solenoid B
  setRelay(PIN_D_RELAY_SMC_3, relay_smc_3); // Solenoid C
  setRelay(PIN_D_RELAY_SMC_4, relay_smc_4); // Solenoid D
  setRelay(PIN_D_RELAY_PHOTO_1, relay_photo_1); // Light A
  setRelay(PIN_D_RELAY_PHOTO_2, relay_photo_1); // Light B

  // Transmit
  JsonObject& dict_tx = json_tx.createObject();
  dict_tx["smc1"] = current_smc_1;
  dict_tx["smc2"] = current_smc_2;
  dict_tx["smc3"] = current_smc_3;
  dict_tx["smc4"] = current_smc_4;
  dict_tx["photo1"] = current_photo_1;
  dict_tx["photo2"] = current_photo_2;
  dict_tx.printTo(data_buffer, sizeof(data_buffer));
  sprintf(tx_buffer, "{\"data\":%s,\"targets\":%s,\"chksum\":%d}", data_buffer, targets_buffer, checksum(data_buffer));
  Serial.println(tx_buffer);
}

/* --- Functions --- */
// Convertie un nombre � virgule en entier arrondi.
int FloatAIntEtArondie(float valeur) {
  int iTemp = (int)valeur;
  float fTemp = valeur - iTemp;
  if (fTemp > 0.5) {
    return (int)(valeur + 1);
  }
  return (int)valeur;
}

// Retourne la valeur du capteur de 0 � 1023
// lit le capteur un certain nombre de fois et en fait une moyennne
// Le capteur est activ� pour la lecture puis est d�sactiv�
int litValeurCapteur(const int PIN_ECRITURE, const int PIN_LECTURE, const int NOMBRE_DE_LECTURE) {
  //temps d'attente pour s'assurer que le capteur est bien activ�.
  const int ATTENTE_LECTURE_MS = 100;
  int valeur = 0;
  for (int i = 0; i != NOMBRE_DE_LECTURE; i++) {
    digitalWrite(PIN_ECRITURE, HIGH);
    delay(ATTENTE_LECTURE_MS);
    valeur += analogRead(PIN_LECTURE);
    digitalWrite(PIN_ECRITURE, LOW);
  }
  return valeur / NOMBRE_DE_LECTURE;
}

//retourne la valeur du capteur en voltage
//le arduino donne une valeur de 0 � 1023 qui repr�sente le voltage du capteur sur 5 volts. Chaque nombre repr�sente environ 0.005 volt
float litValeurCapteurVoltage(const int PIN_ECRITURE, const int PIN_LECTURE, const int NOMBRE_DE_LECTURE) {
  return litValeurCapteur(PIN_ECRITURE, PIN_LECTURE, NOMBRE_DE_LECTURE) * (5.0 / 1023.0);
}

//retourne la r�sistance en Ohm du capteur photo-r�sistif
int litValeurCapteurLumiere (const int PIN_ECRITURE, const int PIN_LECTURE) {
  //le nombre de fois que le capteur sera lu par le arduino pour en faire une moyenne
  const int NOMBREDELECTURE = 4;
  const int VIN = 5; //Voltage d'arduino
  const float RESISTANCE_FIXE = 975; //vrai==975Ohm(sur paquet 1000Ohm) pour les 2!
  //retourne un entier contenant la r�sistance de la photor�sistance en Ohm � l'aide du principe de la division du voltage
  return FloatAIntEtArondie(RESISTANCE_FIXE / ((VIN / litValeurCapteurVoltage(PIN_ECRITURE, PIN_LECTURE, NOMBREDELECTURE)) - 1));
}

// capteur vh400
// retourne la teneur en eau volum�trique(Volumetric Water Content) en %
// Equation fond�e sur les calculs de la compagnie qui produit le capteur d'humidit
// http://vegetronix.com/Products/VH400/VH400-Piecewise-Curve.phtml
int litValeurHumidite (const int PIN_ECRITURE, const int PIN_LECTURE) {
  const int NOMBREDELECTURE = 4;
  float ValeurHumidite = 0.0;
  const int NOMBREDECIMAL = 100;
  float valeurCapteurVoltage = litValeurCapteurVoltage(PIN_ECRITURE, PIN_LECTURE, NOMBREDELECTURE);
  if (valeurCapteurVoltage < 1.1) {
    ValeurHumidite = 10.0 * valeurCapteurVoltage - 1.0;
  }
  if (valeurCapteurVoltage < 1.3) {
    ValeurHumidite = 25.0 * valeurCapteurVoltage - 17.5;
  }
  if (valeurCapteurVoltage < 1.82) {
    ValeurHumidite = 48.08 * valeurCapteurVoltage - 47.5;
  }
  if (valeurCapteurVoltage < 2.2) {
    ValeurHumidite = 26.32 * valeurCapteurVoltage - 7.89;
  }
  // si la valeur est en haut de 50 la pente est approximativement lin�aire
  if (valeurCapteurVoltage >= 2.2) {
    ValeurHumidite = 26.32 * valeurCapteurVoltage - 7.89;
  }
  return ValeurHumidite * NOMBREDECIMAL;
}

// Set Relay
void setRelay(int pin, bool state) {
  delay(25);
  if (state) {
    digitalWrite(pin, LOW);
  }
  else {
    digitalWrite(pin, HIGH);
  }
}

// Function to determine if irrigation solenoid should be engaged/disengaged
bool controlMoisture(int target, int current) {
  if (target > current) {
    return true;
  }
  else {
    return false;
  }
}

// Function to determine if lighting should be engaged/disengaged
bool controlLighting(int target, int current) {
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
