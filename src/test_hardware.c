// these are pins on audio-hat
#define PIN_BUTTON 23
#define PIN_LED 25

#define SSD1306_LCDHEIGHT 64

#include <wiringPi.h>
#include "ssd1306_i2c.h"

#define SSD1306_PAGE_START_ADDRESS 0

#if SSD1306_LCDHEIGHT == 64
#define SSD1306_PAGE_END_ADDRESS 7
#endif
#if SSD1306_LCDHEIGHT == 32
#define SSD1306_PAGE_END_ADDRESS 3
#endif
#if SSD1306_LCDHEIGHT == 16
#define SSD1306_PAGE_END_ADDRESS 1
#endif

void ssd1306_display_image(int* buffer) {
  ssd1306_command(SSD1306_COLUMNADDR);
  ssd1306_command(0);                     // Column start address (0 = reset)
  ssd1306_command(SSD1306_LCDWIDTH - 1);  // Column end address (127
  // = reset)

  ssd1306_command(SSD1306_PAGEADDR);
  ssd1306_command(SSD1306_PAGE_START_ADDRESS);
  ssd1306_command(SSD1306_PAGE_END_ADDRESS);

  // I2C
  int i;
  for (i = 0; i < (SSD1306_LCDWIDTH * SSD1306_LCDHEIGHT / 8); i++) {
    wiringPiI2CWriteReg8(i2cd, 0x40, buffer[i]);
    // This sends byte by byte.
    // Better to send all buffer without 0x40 first
    // Should be optimized
  }
}

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