#define DISABLE_LOGGING
#include <ArduinoLog.h>

#include <AbsoluteLinearPositionControl.h>

#include <ASCIISerialIO.h>
#include <CoreProtocol.h>
#include <BoardProtocol.h>
#include <Modules.h>

using namespace LiquidHandlingRobotics;

// ASCII Serial communications
SerialMessager messager;

// Shared Components
CoreProtocol<SerialMessager> coreProtocol(messager);
BoardProtocol<SerialMessager> boardProtocol(messager);
LinearPositionControl::Components::Motors motors;

// Subsystems
AbsoluteLinearActuator<SerialMessager> pipettor(messager, motors, kPipettorParams);

void setup() {
  coreProtocol.setup();
  messager.setup();
#ifndef DISABLE_LOGGING
  Log.begin(LOG_LEVEL_VERBOSE, &Serial);
#endif
  boardProtocol.setup();
  pipettor.setup();
  messager.establishConnection();
  coreProtocol.onConnect();
  boardProtocol.onConnect();
}

void loop() {
  messager.update();
  coreProtocol.update();
  boardProtocol.update();
  // Modules
  pipettor.update();
}
