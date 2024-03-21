#include <libgen.h>
#include <stdio.h>
#include <stdlib.h>
#include "portaudio.h"
#include "z_libpd.h"

#include <c-flags.h>
#include <stdbool.h>
#include <unistd.h>
#include "vec.h"
#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#endif

bool file_exists(char* filename) {
  return (access(filename, R_OK)) != -1;
}

// returns number of input channels for device index or 0 if none
static int pa_get_inputs(PaDeviceIndex dev) {
  const PaDeviceInfo* info = Pa_GetDeviceInfo(dev);
  return (info ? info->maxInputChannels : 0);
}

// returns number of output channels for device index or 0 if none
static int pa_get_outputs(PaDeviceIndex dev) {
  const PaDeviceInfo* info = Pa_GetDeviceInfo(dev);
  return (info ? info->maxOutputChannels : 0);
}

// portaudio sample render callback
static int pa_callback(const void* inputBuffer, void* outputBuffer, unsigned long framesPerBuffer, const PaStreamCallbackTimeInfo* timeInfo, PaStreamCallbackFlags statusFlags, void* userData) {
  // assumes blocksize is *always* a multiple of libpd_blocksize(),
  // if not, then additional buffer is required
  int ticks = framesPerBuffer / libpd_blocksize();
  libpd_process_float(ticks, inputBuffer, outputBuffer);
  return 0;
}

// cross-platform sleep
// from https://gist.github.com/rafaelglikis/ee7275bf80956a5308af5accb4871135
void sleep_ms(int ms) {
#ifdef _WIN32
  Sleep(ms);
#elif _POSIX_C_SOURCE >= 199309L
  struct timespec ts;
  ts.tv_sec = ms / 1000;
  ts.tv_nsec = (ms % 1000) * 1000000;
  nanosleep(&ts, NULL);
#else
  usleep(ms * 1000);
#endif
}

static void printHook(const char* s) {
  printf("%s", s);
}

static void messageHook(const char* src, const char* sym, int argc, t_atom* argv) {
  // printf("MESSAGE: %s %s (%d)\n", src, sym, argc);
  if (strcmp(src, "oled") == 0) {
    if (strcmp(sym, "text") == 0) {
      int color = libpd_get_float(&argv[0]);
      int x = libpd_get_float(&argv[1]);
      int y = libpd_get_float(&argv[2]);

      char text[100] = "";
      for (int i = 3; i < argc; i++) {
        strcat(text, libpd_get_symbol(&argv[i]));
        if (i < (argc - 1)) {
          strcat(text, " ");
        }
      }
      printf("TEXT %d (%dx%d): %s\n", color, x, y, text);
    }

    if (strcmp(sym, "circle") == 0) {
      int color = libpd_get_float(&argv[0]);
      int x = libpd_get_float(&argv[1]);
      int y = libpd_get_float(&argv[2]);
      int r = libpd_get_float(&argv[3]);
      printf("CIRCLE %d: (%dx%d - %d)\n", color, x, y, r);
    }

    if (strcmp(sym, "pixel") == 0) {
      int color = libpd_get_float(&argv[0]);
      int x = libpd_get_float(&argv[1]);
      int y = libpd_get_float(&argv[2]);
      printf("PIXEL %d: (%dx%d)\n", color, x, y);
    }

    if (strcmp(sym, "rectangle") == 0) {
      int color = libpd_get_float(&argv[0]);
      int x = libpd_get_float(&argv[1]);
      int y = libpd_get_float(&argv[2]);
      int w = libpd_get_float(&argv[3]);
      int h = libpd_get_float(&argv[4]);
      printf("RECTANGLE %d: (%dx%d - %dx%d)\n", color, x, y, w, h);
    }

    if (strcmp(sym, "image") == 0) {
      int x = libpd_get_float(&argv[0]);
      int y = libpd_get_float(&argv[1]);

      char filename[100] = "";
      for (int i = 3; i < argc; i++) {
        strcat(filename, libpd_get_symbol(&argv[i]));
        if (i < (argc - 1)) {
          strcat(filename, " ");
        }
      }
      printf("IMAGE (%dx%d): %s\n", x, y, filename);
    }
  }

  // these are neopixels
  if (strcmp(src, "rgb") == 0) {
    // TODO: set RGB colors
  }
}

static void noteonHook(int channel, int pitch, int velocity) {
  printf("NOTEON: %d %d %d\n", channel, pitch, velocity);
}

static void listHook(const char* src, int argc, t_atom* argv) {
  if (strcmp(src, "gpio_out") == 0) {
    int pin = libpd_get_float(&argv[0]);
    int value = libpd_get_float(&argv[1]);
    printf("GPIO OUT: %d %d\n", pin, value);
  }
}

/*

static void bangHook(const char* src) {
}

static void floatHook(const char* src, float x) {
}

static void symbolHook(const char* src, const char* sym) {
}

static void controlChangeHook(int channel, int controller, int value) {
}

static void programChangeHook(int channel, int value) {
}

static void pitchBendHook(int channel, int value) {
}

static void aftertouchHook(int channel, int value) {
}

static void polyAftertouchHook(int channel, int pitch, int value) {
}

static void midiByteHook(int port, int byte) {
}

*/

int piploader_run(char* filename, char* dirname, bool oled, int* input_gpios, int input_gpios_count, int* output_gpios, int output_gpios_count) {
  printf("File: %s\nOLED: %s\nInputs: ", filename, oled ? "yes" : "no");
  for (int i = 0; i < input_gpios_count; i++) {
    printf("%d ", input_gpios[i]);
  }
  printf("\nOutputs: ");
  for (int i = 0; i < output_gpios_count; i++) {
    printf("%d ", output_gpios[i]);
  }
  printf("\n");

  // init portaudio: default devices, 32 bit float samples
  PaError error = Pa_Initialize();
  if (error != paNoError) {
    printf("portaudio init error: %s\n", Pa_GetErrorText(error));
    return -1;
  }
  int inputdev = Pa_GetDefaultInputDevice();
  int outputdev = Pa_GetDefaultOutputDevice();
  int inputchan = pa_get_inputs(inputdev);
  int outputchan = pa_get_outputs(outputdev);
  int samplerate = 44100;
  int buffersize = 512;
  PaStream* stream = NULL;
  PaStreamParameters inputParams = {
      .device = (PaDeviceIndex)inputdev,
      .channelCount = inputchan,
      .sampleFormat = paFloat32,
      0,
      NULL};
  PaStreamParameters outputParams = {
      .device = (PaDeviceIndex)outputdev,
      .channelCount = outputchan,
      .sampleFormat = paFloat32,
      0,
      NULL};
  error = Pa_OpenStream(
      &stream,
      (inputchan > 0 ? &inputParams : NULL),
      (outputchan > 0 ? &outputParams : NULL),
      samplerate,
      buffersize,
      0,
      pa_callback,
      NULL);

  if (error != paNoError) {
    fprintf(stderr, "portaudio open error: %s\n", Pa_GetErrorText(error));
    return -1;
  }

  libpd_set_printhook(printHook);
  libpd_set_messagehook(messageHook);
  libpd_set_noteonhook(noteonHook);
  libpd_set_listhook(listHook);

  // libpd_set_banghook(bangHook);
  // libpd_set_floathook(floatHook);
  // libpd_set_symbolhook(symbolHook);
  // libpd_set_controlchangehook(controlChangeHook);
  // libpd_set_programchangehook(programChangeHook);
  // libpd_set_pitchbendhook(pitchBendHook);
  // libpd_set_aftertouchhook(aftertouchHook);
  // libpd_set_polyaftertouchhook(polyAftertouchHook);
  // libpd_set_midibytehook(midiByteHook);

  libpd_set_verbose(0);
  libpd_init();

  libpd_bind("oled");
  libpd_bind("gpio_out");

  libpd_init_audio(inputchan, outputchan, samplerate);

  // compute audio    [; pd dsp 1(
  libpd_start_message(1);  // one entry in list
  libpd_add_float(1.0f);
  libpd_finish_message("pd", "dsp");

  // open patch       [; pd open file folder(
  if (!libpd_openfile(filename, dirname)) {
    return -1;
  }

  // start audio processing
  error = Pa_StartStream(stream);
  if (error != paNoError) {
    fprintf(stderr, "portaudio start error: %s\n", Pa_GetErrorText(error));
    return -1;
  }

  while (1) {
    // TODO: read input GPIOs & send messages
    // TODO: read rotary-encoders (and extra buttons) & send messages
    sleep_ms(1000);
  }

  // stop audio processing
  error = Pa_StopStream(stream);
  if (error != paNoError) {
    fprintf(stderr, "portaudio stop error: %s\n", Pa_GetErrorText(error));
    return -1;
  }

  // done
  error = Pa_Terminate();
  if (error != paNoError) {
    fprintf(stderr, "portaudio terminate error: %s\n", Pa_GetErrorText(error));
    return -1;
  }

  return 0;
}