#define DISABLE_LOGGING
#include <ArduinoLog.h>

#include <ASCIISerialIO.h>
#include <CoreProtocol.h>
#include <BoardProtocol.h>

using namespace LiquidHandlingRobotics;

// ASCII Serial communications
SerialMessager messager;

// Shared Components
CoreProtocol<SerialMessager> coreProtocol(messager);
BoardProtocol<SerialMessager> boardProtocol(messager);

void setup() {
  coreProtocol.setup();
  messager.setup();
  boardProtocol.setup();
#ifndef DISABLE_LOGGING
  Log.begin(LOG_LEVEL_VERBOSE, &Serial);
#endif
  messager.establishConnection();
  coreProtocol.onConnect();
  boardProtocol.onConnect();
}

void loop() {
  messager.update();
  coreProtocol.update();
  boardProtocol.update();
}
