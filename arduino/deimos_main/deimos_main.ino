

int incomingByte = 0;
bool state = LOW;

int pin5vEnable = 2;

// the setup function runs once when you press reset or power the board
void setup() {
  // initialize pins
  pinMode(pin5vEnable, OUTPUT);
  Serial.begin(115200);
}

// the loop function runs over and over again forever
void loop() {
  

  // send data only when you receive data:
  int available = Serial.available();
  if (available > 0) {
    // read the incoming byte:
    for (int i=0; i<available; i++) {
      incomingByte = Serial.read();
      //Serial.print(incomingByte, DEC);
      //Serial.print(incomingByte + '0');
      //Serial.print(' ');
      if (incomingByte == '0') {
        state = LOW;
      } else if (incomingByte =='1') {
        state = HIGH;
      }
    }
    digitalWrite(pin5vEnable, state);   // turn the LED on (HIGH is the voltage level)
    Serial.println(state);
  }
  delay(100);
}
