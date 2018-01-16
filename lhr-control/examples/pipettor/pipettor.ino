//#define DISABLE_LOGGING
#include <ArduinoLog.h>

#include <Pipettor.h>
#include <ASCIISerialIO.h>

using namespace LiquidHandlingRobotics;

// ASCII Serial communications
ChannelParser channelParser;
IntParser intParser;

// Shared Components
LinearPositionControl::Components::Motors motors;

// Subsystems
Pipettor pipettor(channelParser, intParser, motors);

void setup() {
  Serial.begin(115200);
#ifndef DISABLE_LOGGING
  Log.begin(LOG_LEVEL_VERBOSE, &Serial);
#endif
  channelParser.setup();
  intParser.setup();
  pipettor.setup();
  waitForSerialHandshake();
}

void loop() {
  channelParser.update();
  if (channelParser.justUpdated) {
    Serial.print("Just received a message on channel ");
    Serial.println(channelParser.channel);
  }
  pipettor.update();
}
