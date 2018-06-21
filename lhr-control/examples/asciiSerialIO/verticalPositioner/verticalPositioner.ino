#define DISABLE_LOGGING
#include <ArduinoLog.h>

#include <AbsoluteLinearPositionControl.h>

#include <ASCIISerialIO.h>
#include <CoreProtocol.h>
//#include <BoardProtocol.h>
#include <Modules.h>

using namespace LiquidHandlingRobotics;
using Core = CoreProtocol<SerialMessager>;
//using Board = BoardProtocol<SerialMessager>;
using AbsoluteAxis = AbsoluteLinearActuator<SerialMessager>;

// ASCII Serial communications
SerialMessager messager;

// Shared Components
Core coreProtocol(messager);
//Board boardProtocol(messager);
LinearPositionControl::Components::Motors motors;

// Subsystems
AbsoluteAxis pipettor(messager, motors, kPipettorParams);
AbsoluteAxis verticalPositioner(messager, motors, kVerticalPositionerParams);

void setup() {
  coreProtocol.setup();
  messager.setup();
#ifndef DISABLE_LOGGING
  Log.begin(LOG_LEVEL_VERBOSE, &Serial);
#endif
  //boardProtocol.setup();
  pipettor.setup();
  verticalPositioner.setup();

  messager.establishConnection();

  coreProtocol.onConnect();
  //boardProtocol.onConnect();
  pipettor.onConnect();
  verticalPositioner.onConnect();
}

void loop() {
  messager.update();
  coreProtocol.update();
  //boardProtocol.update();
  // Modules
  pipettor.update();
  verticalPositioner.update();
}
