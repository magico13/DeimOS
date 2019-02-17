//int incomingByte = 0;
uint8_t PWR_MODE = 0; //0-Off, 1-Startup, 2-Managed, 3-Unmanaged, 4-Shutdown

uint32_t ms_pressed = 0;
uint32_t timeout_timer = 0;

uint8_t missed_checkins = 0;

#define PIN_USER 3
#define PIN_5V 2
#define PIN_LED 13

//PWR modes
#define MODE_OFF 0
#define MODE_START 1
#define MODE_MANAGED 2
#define MODE_UNMANAGED 3
#define MODE_SHUTDOWN 4

// the setup function runs once when you press reset or power the board
void setup() 
{
  // initialize pins
  pinMode(PIN_USER, INPUT_PULLUP);
  pinMode(PIN_5V, OUTPUT);
  pinMode(PIN_LED, OUTPUT);
  Serial.begin(115200);
}

// the loop function runs over and over again forever
void loop() 
{
  uint32_t now = millis();
  uint32_t button_time = 0;
  if (digitalRead(PIN_USER) && ms_pressed > 0) //not pressed
  {
    button_time = now - ms_pressed;
    ms_pressed = 0;
  }
  digitalWrite(PIN_LED, (PWR_MODE != MODE_OFF));

  if (PWR_MODE == MODE_OFF) //5v is off, not sending data to pi
  {
    digitalWrite(PIN_5V, LOW);
    //if the button is pressed for more than half a second, switch to Startup
    if (!digitalRead(PIN_USER) && ms_pressed == 0) //reads HIGH when not pressed (pullup)
    {
      ms_pressed = now;
    }
    if (button_time > 500) //half a second
    {
      PWR_MODE = MODE_START; //swap to start mode
      timeout_timer = now;
      digitalWrite(PIN_5V, HIGH);
    }
  }
  if (PWR_MODE == MODE_START) //give power and wait a minute for a signal from pi, otherwise fall back to off mode
  {
    if (Serial.available() > 0)
    {
      PWR_MODE = MODE_MANAGED; //swap to managed mode, looking for constant serial communication
    }
    else if (now - timeout_timer > 60000)
    {
      PWR_MODE = MODE_OFF; //60 seconds have passed with no serial input, shut down
    }
  }
  if (PWR_MODE == MODE_MANAGED)
  {
    int32_t available = Serial.available();
    if (available > 0) 
    {
      missed_checkins = 0;
      int32_t incomingByte;
      // read the incoming byte:
      for (uint8_t i=0; i<available; i++) 
      {
        incomingByte = Serial.read();
      }

      //send the current sensor info and the length of time that the button was pressed
    }
    else
    {
      missed_checkins++;
      if (missed_checkins > 50) //5 seconds of no serial means the pi may have crashed
      { //turn off the power (and TODO: start up again automatically)
        PWR_MODE = MODE_OFF;
        missed_checkins = 0;
      }
    }
  }

  if (PWR_MODE == MODE_SHUTDOWN)
  {
    //wait 30 seconds and then power off
    if (button_time > 30000)
    {
      PWR_MODE = MODE_OFF;
    }
  }

  if (PWR_MODE != MODE_OFF)
  {
    //if button pressed for more than 5 seconds, force off
    if (!digitalRead(PIN_USER) && ms_pressed == 0) //reads HIGH when not pressed (pullup)
    {
      ms_pressed = now;
    }
    if ((now - ms_pressed) > 5000)
    {
      ms_pressed = 0;
      PWR_MODE = MODE_OFF; //swap to start mode
    }
  }
  // send data only when you receive data:
  // int available = Serial.available();
  // if (available > 0) {
  //   // read the incoming byte:
  //   for (int i=0; i<available; i++) {
  //     incomingByte = Serial.read();
  //     if (incomingByte == '0') {
  //       state_5v = LOW;
  //     } else if (incomingByte =='1') {
  //       state_5v = HIGH;
  //     }
  //   }
  //   digitalWrite(pin5vEnable, state_5v);   // turn the LED on (HIGH is the voltage level)
  //   Serial.println(state_5v);
  // }
  delay(100);
}
