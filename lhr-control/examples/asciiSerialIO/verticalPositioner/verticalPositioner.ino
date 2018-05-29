#include <avr/wdt.h>

#define DISABLE_LOGGING
#include <ArduinoLog.h>

#include <ASCIISerialIO.h>
#include <CoreProtocol.h>
#include <Modules.h>

using namespace LiquidHandlingRobotics;

// ASCII Serial communications
SerialMessager messager;

// Shared Components
LinearPositionControl::Components::Motors motors;

// Subsystems
AbsoluteLinearActuator<SerialMessager> pipettor(messager, motors, kPipettorParams);
AbsoluteLinearActuator<SerialMessager> verticalPositioner(messager, motors, kVerticalPositionerParams);

void setup() {
  wdt_disable();
  Serial.begin(115200);
#ifndef DISABLE_LOGGING
  Log.begin(LOG_LEVEL_VERBOSE, &Serial);
#endif
  messager.setup();
  pipettor.setup();
  verticalPositioner.setup();
  waitForSerialHandshake();
  wdt_enable(WDTO_2S);
  sendAllVersionMessages(messager.sender);
}

void loop() {
  wdt_reset();
  messager.update();
  // Standard protocol
  wdt_reset();
  handleResetCommand(messager);
  handleVersionCommand(messager);
  handleEchoCommand(messager);
  handleIOCommand(messager);
  // Modules
  wdt_reset();
  pipettor.update();
  wdt_reset();
  verticalPositioner.update();
}
