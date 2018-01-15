//#define DISABLE_LOGGING
#include <ArduinoLog.h>

#include <Pipettor.h>
#include <ASCIISerialIO.h>

using namespace LiquidHandlingRobotics;

LinearPositionControl::Components::Motors motors;
Pipettor pipettor(motors);

void setup() {
  Serial.begin(115200);
#ifndef DISABLE_LOGGING
  Log.begin(LOG_LEVEL_VERBOSE, &Serial);
#endif
  pipettor.setup();
  waitForSerialHandshake();
}

void loop() {
  pipettor.update();
}
