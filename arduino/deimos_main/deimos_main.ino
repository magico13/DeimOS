#include <EEPROM.h>

uint8_t PWR_MODE = 0; //0-Off, 1-Startup, 2-Managed, 3-Unmanaged, 4-Shutdown

uint32_t ms_pressed = 0;
uint32_t timeout_timer = 0;

uint8_t missed_checkins = 0;

#define PIN_USER 3
#define PIN_5V 2
#define PIN_LED 13
#define PIN_SPEEDO 5 //required for using frequency monitor

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
  PWR_MODE = get_state_from_eeprom();
  digitalWrite(PIN_5V, (PWR_MODE != MODE_OFF));
  digitalWrite(PIN_LED, (PWR_MODE != MODE_OFF));
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
    //Serial.print("Button ms: ");
    //Serial.println(button_time);
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
      PWR_MODE = MODE_START; //swap to start mode //temporarily swapping to Unmanaged mode
      timeout_timer = now;
      digitalWrite(PIN_5V, HIGH);
      Serial.println("Mode switch: OFF -> START");
    }
  }
  if (PWR_MODE == MODE_START) //give power and wait a minute for a signal from pi, otherwise fall back to off mode
  {
    if (Serial.available() > 0)
    {
      PWR_MODE = MODE_MANAGED; //swap to managed mode, looking for constant serial communication
      Serial.println("Mode switch: START -> MANAGED");
    }
    else if (now - timeout_timer > 60000)
    {
      PWR_MODE = MODE_OFF; //60 seconds have passed with no serial input, shut down
      Serial.println("Mode switch: START -> OFF");
    }
  }
  if (PWR_MODE == MODE_MANAGED || PWR_MODE == MODE_UNMANAGED)
  {
    int32_t available = Serial.available();
    if (available > 0) 
    {
      missed_checkins = 0;
      handle_serial_input(available);

      //send the current sensor info and the length of time that the button was pressed
      Serial.print(PWR_MODE);
      Serial.print(",");
      Serial.print(button_time);
      Serial.println();
    }
    else if (PWR_MODE == MODE_MANAGED)
    {
      missed_checkins++;
      if (missed_checkins > 50) //5 seconds of no serial means the pi may have crashed
      { //turn off the power (and TODO: start up again automatically)
        PWR_MODE = MODE_OFF;
        missed_checkins = 0;
        Serial.println("Mode switch: MANAGED -> OFF");
      }
    }
  }

  if (PWR_MODE == MODE_SHUTDOWN)
  {
    //wait 30 seconds and then power off
    if (now - timeout_timer > 30000)
    {
      PWR_MODE = MODE_OFF;
      Serial.println("Mode switch: SHUTDOWN -> OFF");
    }
  }

  if (PWR_MODE != MODE_OFF)
  {
    //if button pressed for more than 5 seconds, force off
    if (!digitalRead(PIN_USER) && ms_pressed == 0) //reads HIGH when not pressed (pullup)
    {
      ms_pressed = now;
    }
    if (button_time > 5000)
    {
      ms_pressed = 0;
      PWR_MODE = MODE_OFF;
      Serial.println("Mode switch: BUTTON -> OFF"); //the user can hold the button to force the system off
    }
  }
  update_state_in_eeprom(PWR_MODE);
  delay(100);
}

void update_state_in_eeprom(uint8_t state)
{
  EEPROM.update(0, state);
}

uint8_t get_state_from_eeprom()
{
  return EEPROM.read(0);
}

void handle_serial_input(uint32_t available)
{
  uint8_t incomingByte;
  // read the incoming byte:
  for (uint8_t i=0; i<available; i++)
  {
    incomingByte = Serial.read();
    // 1 - regular update
    // 2 - swap to unmanaged mode
    // 3 - swap to managed mode
    // 4 - swap to shutdown mode
    switch (incomingByte)
    {
      case 2: PWR_MODE = MODE_UNMANAGED; Serial.println("Mode switch: UNMANAGED"); break;
      case 3: PWR_MODE = MODE_MANAGED; Serial.println("Mode switch: MANAGED"); break;
      case 4: PWR_MODE = MODE_SHUTDOWN; timeout_timer = millis(); Serial.println("Mode switch: SHUTDOWN"); break;
      default: break;
    }
  }
}
