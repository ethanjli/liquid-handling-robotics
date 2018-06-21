#define DISABLE_LOGGING
#include <ArduinoLog.h>

#define LPC_Components_Motors
#include <LinearPositionControl.h>

#define LHR_Messaging_ASCIIIO
#define LHR_Protocol_Core
#define LHR_Protocol_Board
#define LHR_Protocol_AbsoluteLinearActuatorAxis
#include <LiquidHandlingRobotics.h>
#include <Modules.h>

using namespace LiquidHandlingRobotics;

// Shared Components
LinearPositionControl::Components::Motors motors;
Messager messager;

// Protocol
Core core(messager);
Board board(messager);
AbsoluteLinearActuatorAxis pipettor(messager, motors, kPipettorParams);

void setup() {
  core.setup();
  messager.setup();
#ifndef DISABLE_LOGGING
  Log.begin(LOG_LEVEL_VERBOSE, &Serial);
#endif
  board.setup();
  pipettor.setup();

  messager.establishConnection();

  core.onConnect();
  board.onConnect();
  pipettor.onConnect();
}

void loop() {
  messager.update();
  core.update();
  board.update();
  pipettor.update();
}
