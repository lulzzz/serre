/*
  Hydroponics controller - Version 1
*/

// Contants
const int BAUD = 9600;
const int INTERVAL = 1000;
const int N_PIN = A0;
const int Ca_PIN = A1;
const int K_PIN = A2;
const int P_PIN = A3;
const int OUTPUT_LENGTH = 256;
const int DATA_LENGTH = 128;

// Variables
char output_buffer[OUTPUT_LENGTH];
char data_buffer[DATA_LENGTH];

void setup(void) {
  Serial.begin(BAUD);
}

void loop(void) {
  delay(INTERVAL);
  int N = get_N();
  int Ca = get_Ca();
  int P = get_P();
  int K = get_K();
  sprintf(data_buffer, "{\"P\":%d,\"K\":%d,\"Ca\":%d,\"N\":%d}", P, K, Ca, N);
  int chksum = checksum(data_buffer);
  sprintf(output_buffer, "{\"data\":%s,\"chksum\":%d}", data_buffer,chksum);
  Serial.println(output_buffer);
}

int get_N(void) {
  return analogRead(N_PIN);
}

int get_Ca(void) {
  return analogRead(Ca_PIN);
}

int get_K(void) {
  return analogRead(K_PIN);
}

int get_P(void) {
  return analogRead(P_PIN);
}

int checksum(char* buf) {
  int sum = 0;
  for (int i = 0; i < DATA_LENGTH; i++) {
    sum = sum + buf[i];
  }
  return sum % 256;
}
