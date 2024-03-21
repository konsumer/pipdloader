#include <wiringPi.h>

// for oled:
// https://github.com/iliapenev/ssd1306_i2c/tree/master

// these are pins on audio-hat
#define PIN_BUTTON 23
#define PIN_LED 25

int main(int argc, char* argv[]) {
  wiringPiSetupGpio();
  pinMode(PIN_BUTTON, INPUT);
  pinMode(PIN_LED, OUTPUT);

  // pullUpDnControl(PIN_BUTTON, PUD_DOWN);

  for (;;) {
    digitalWrite(PIN_LED, HIGH);
    delay(500);
    digitalWrite(PIN_LED, LOW);
    delay(500);
  }

  return 0;
}