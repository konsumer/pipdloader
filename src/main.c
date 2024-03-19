#include "pipdloader.h"

int main(int argc, char* argv[]) {
  if (argc > 0) {
    c_flags_set_application_name(argv[0]);
  }
  c_flags_set_positional_args_description("<file-path>");
  c_flags_set_description("Load puredata patches and interact with pi hardware.");

  bool* help = c_flag_bool("help", "h", "show usage", false);
  bool* oled = c_flag_bool("oled", "s", "Use SSD1306 OLED on GPIO 2/3", false);
  char** input_all = c_flag_string("input", "i", "Comma-seperated list of input GPIO pins", "");
  char** output_all = c_flag_string("output", "o", "Comma-seperated list of output GPIO pins", "");

  c_flags_parse(&argc, &argv, false);

  if (*help) {
    c_flags_usage();
    return 0;
  }

  if (argc == 0) {
    printf("ERROR: required file path not specified\n\n");
    c_flags_usage();
    return 1;
  }

  int* input_gpios = vector_create();
  char* ch = strtok(*input_all, ",");
  while (ch != NULL) {
    vector_add(&input_gpios, atoi(ch));
    ch = strtok(NULL, ",");
  }

  int* output_gpios = vector_create();
  ch = strtok(*output_all, ",");
  while (ch != NULL) {
    vector_add(&output_gpios, atoi(ch));
    ch = strtok(NULL, ",");
  }

  if (!file_exists(argv[0])) {
    printf("ERROR: file not found or not readable: %s\n\n", argv[0]);
    c_flags_usage();
    return 1;
  }

  char* dir = dirname(argv[0]);

  return piploader_run(argv[0], dir, *oled, input_gpios, vector_size(input_gpios), output_gpios, vector_size(output_gpios));
}
