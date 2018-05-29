#define DISABLE_LOGGING
#include <ArduinoLog.h>

#include <ASCIISerialIO.h>
#include <CoreProtocol.h>
#include <Modules.h>

using namespace LiquidHandlingRobotics;

// ASCII Serial communications
SerialMessager messager;

// Shared Components
CoreProtocol<SerialMessager> coreProtocol(messager);
LinearPositionControl::Components::Motors motors;

// Subsystems
AbsoluteLinearActuator<SerialMessager> pipettor(messager, motors, kPipettorParams);
AbsoluteLinearActuator<SerialMessager> verticalPositioner(messager, motors, kVerticalPositionerParams);

void setup() {
  coreProtocol.setup();
  messager.setup();
#ifndef DISABLE_LOGGING
  Log.begin(LOG_LEVEL_VERBOSE, &Serial);
#endif
  pipettor.setup();
  verticalPositioner.setup();
  messager.establishConnection();
  coreProtocol.onConnect();
}

void loop() {
  messager.update();
  coreProtocol.update();
  // Modules
  pipettor.update();
  verticalPositioner.update();
}
