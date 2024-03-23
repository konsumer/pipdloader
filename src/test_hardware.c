#include <wiringPi.h>
#include "ssd1306_i2c.h"

// these are pins on audio-hat
#define PIN_BUTTON 23
#define PIN_LED 25

int main(int argc, char* argv[]) {
  wiringPiSetupGpio();

  pinMode(PIN_BUTTON, INPUT);
  pinMode(PIN_LED, OUTPUT);

  ssd1306_begin(SSD1306_SWITCHCAPVCC, SSD1306_I2C_ADDRESS);

  ssd1306_display();  // Adafruit logo is visible
  ssd1306_clearDisplay();
  delay(5000);

  char* text = "This is demo for SSD1306 i2c driver for Raspberry Pi";
  ssd1306_drawString(text);
  ssd1306_display();
  delay(5000);

  ssd1306_dim(1);
  ssd1306_startscrollright(00, 0xFF);
  delay(5000);

  ssd1306_clearDisplay();
  ssd1306_fillRect(10, 10, 50, 20, WHITE);
  ssd1306_fillRect(80, 10, 130, 50, WHITE);
  ssd1306_display();

  // pullUpDnControl(PIN_BUTTON, PUD_DOWN);

  for (;;) {
    digitalWrite(PIN_LED, HIGH);
    delay(500);
    digitalWrite(PIN_LED, LOW);
    delay(500);
  }

  return 0;
}