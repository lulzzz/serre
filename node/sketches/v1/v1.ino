
/*
  Hydroponics controller - Version 2
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
char input_buffer[INPUT_LENGTH] = {'\0'};
StaticJsonBuffer<JSON_LENGTH> json_buffer;
int lights = 1;
int watering_time = 60;
int cycle_time = 240;

// Setup
void setup(void) {
  Serial.begin(BAUD);
}

void loop(void) {
  delay(INTERVAL);
  // {"cycle_time":120,"watering_time":30,"lights":0}
  if (Serial.available() > 0) {
    int i = 0;
    char c = ' ';
    while (c != '}') {
      c = Serial.read();
      input_buffer[i] = c;
      i++;
    }
    JsonObject& root = json_buffer.parseObject(input_buffer);
    cycle_time = root["cycle_time"];
    watering_time = root["watering_time"];
    lights = root["lights"];
  }
  sprintf(data_buffer, "{\"lights\":%d,\"watering_time\":%d,\"cycle_time\":%d}", lights, watering_time, cycle_time);
  int chksum = checksum(data_buffer);
  sprintf(output_buffer, "{\"data\":%s,\"chksum\":%d}", data_buffer,chksum);
  Serial.println(output_buffer);
}

int checksum(char* buf) {
  int sum = 0;
  for (int i = 0; i < DATA_LENGTH; i++) {
    sum = sum + buf[i];
  }
  return sum % 256;
}
