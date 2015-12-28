const int BAUD = 38400;

void setup() {
  Serial.begin(BAUD);
}

void loop() {
  if (Serial.available() > 0) {
    Serial.println("ping");
  }
}
