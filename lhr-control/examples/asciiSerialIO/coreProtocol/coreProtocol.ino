#define DISABLE_LOGGING
#include <ArduinoLog.h>

#define LHR_Messaging_ASCIIIO
#define LHR_Protocol_Core
#define LHR_Protocol_Board
#include <LiquidHandlingRobotics.h>

using namespace LiquidHandlingRobotics;

// ASCII Serial communications
Messager messager;

// Shared Components
Core core(messager);
Board board(messager);

void setup() {
  core.setup();
  messager.setup();
#ifndef DISABLE_LOGGING
  Log.begin(LOG_LEVEL_VERBOSE, &Serial);
#endif
  board.setup();

  messager.establishConnection();

  core.onConnect();
  board.onConnect();
}

void loop() {
  messager.update();
  core.update();
  board.update();
}
