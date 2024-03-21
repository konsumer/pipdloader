cmake_minimum_required(VERSION 3.18)

project(pdloader
  DESCRIPTION "Load puredata files and interact with hardware"
  HOMEPAGE_URL "https://github.com/konsumer/pdloader"
  VERSION 0.0.1
  LANGUAGES C
)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS ON)

include(FetchContent)
set(FETCHCONTENT_QUIET 0)

set(CMAKE_BUILD_TYPE Release)

file(DOWNLOAD
   https://raw.githubusercontent.com/DieTime/c-flags/master/single-header/c-flags.h
    ${CMAKE_BINARY_DIR}/include/c-flags.h
    SHOW_PROGRESS
)

file(DOWNLOAD
   https://raw.githubusercontent.com/Mashpoe/c-vector/master/vec.c
    ${CMAKE_BINARY_DIR}/include/vec.c
    SHOW_PROGRESS
)

file(DOWNLOAD
   https://raw.githubusercontent.com/Mashpoe/c-vector/master/vec.h
    ${CMAKE_BINARY_DIR}/include/vec.h
    SHOW_PROGRESS
)

# this will make libpd work on mac. need to work them out for other platforms
if(APPLE)
  add_definitions(-DHAVE_ALLOCA_H -DHAVE_MACHINE_ENDIAN_H -D_DARWIN_C_SOURCE -DHAVE_LIBDL)
endif()

FetchContent_Declare(
  portaudioremote
  GIT_REPOSITORY https://github.com/PortAudio/portaudio.git
  GIT_TAG v19.7.0
  GIT_PROGRESS TRUE
  GIT_SHALLOW 1
)
FetchContent_MakeAvailable(portaudioremote)

FetchContent_Declare(
  libpdremote
  GIT_REPOSITORY https://github.com/libpd/libpd.git
  GIT_TAG 0.14.1
  GIT_PROGRESS TRUE
  GIT_SHALLOW 1
)
FetchContent_MakeAvailable(libpdremote)
include_directories(${libpdremote_SOURCE_DIR}/libpd_wrapper)
include_directories(${libpdremote_SOURCE_DIR}/pure-data/src)
include_directories(${CMAKE_BINARY_DIR}/include)

add_executable(${PROJECT_NAME}
  src/main.c
  ${CMAKE_BINARY_DIR}/include/vec.c
)
target_link_libraries(${PROJECT_NAME} libpd_static portaudio)

add_executable(test_hardware
  src/test_hardware.c
)
target_link_libraries(test_hardware wiringPi)

