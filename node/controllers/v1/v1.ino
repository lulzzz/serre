/*
  Hydroponics controller - Version 1
*/

// Libraries
#include <ArduinoJson.h>

// Contants
const int BAUD = 9600;
const int INTERVAL = 1000;
const int OUTPUT_LENGTH = 256;
const int DATA_LENGTH = 128;
const int JSON_LENGTH = 256;
const int INPUT_LENGTH = 256;

// Variables
char output_buffer[OUTPUT_LENGTH];
char data_buffer[DATA_LENGTH];
char targets_buffer[DATA_LENGTH];
char input_buffer[INPUT_LENGTH] = {'\0'};
StaticJsonBuffer<JSON_LENGTH> json_input;
StaticJsonBuffer<JSON_LENGTH> json_sensors;
StaticJsonBuffer<JSON_LENGTH> json_targets;
JsonObject& input = json_input.createObject();
JsonObject& sensors = json_sensors.createObject();
JsonObject& targets = json_targets.createObject();
int cycle_time = 0;
int lights = 0;
int watering_time = 0;

// Setup
void setup(void) {
  Serial.begin(BAUD);
}

void loop(void) {
  delay(INTERVAL);
  
  // Update Targets
  if (Serial.available() > 0) {
    int i = 0;
    char c = ' ';
    while (c != '}') {
      c = Serial.read();
      input_buffer[i] = c;
      i++;
    }
    JsonObject& input = json_input.parseObject(input_buffer);
    cycle_time = input["cycle_time"];
    watering_time = input["watering_time"];
    lights = input["lights"];
    while (Serial.available() > 0) {
      Serial.read();
    }
  }
  
  // Update Targets
  targets["cycle_time"] = cycle_time;
  targets["watering_time"] = watering_time;
  targets["lights"] = lights;
  targets.printTo(targets_buffer, sizeof(targets_buffer));
  
  // Update Sensors
  sensors["brightness"] = analogRead(0);
  sensors.printTo(data_buffer, sizeof(data_buffer));
  
  // Push values to node
  int chksum = checksum(data_buffer);
  sprintf(output_buffer, "{\"data\":%s,\"targets\":%s,\"chksum\":%d}", data_buffer, targets_buffer, chksum);
  Serial.println(output_buffer);
}

int checksum(char* buf) {
  int sum = 0;
  for (int i = 0; i < DATA_LENGTH; i++) {
    sum = sum + buf[i];
  }
  return sum % 256;
}
