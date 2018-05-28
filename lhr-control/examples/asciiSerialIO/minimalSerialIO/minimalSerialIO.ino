#include <avr/wdt.h>

#define DISABLE_LOGGING
#include <ArduinoLog.h>

#include <ASCIISerialIO.h>
#include <CoreProtocol.h>

using namespace LiquidHandlingRobotics;

// ASCII Serial communications
SerialMessageParser messageParser;
SerialMessageSender messageSender;

void setup() {
  wdt_disable();
  Serial.begin(115200);
#ifndef DISABLE_LOGGING
  Log.begin(LOG_LEVEL_VERBOSE, &Serial);
#endif
  messageParser.setup();
  waitForSerialHandshake();
  wdt_enable(WDTO_2S);
  sendAllVersionMessages(messageSender);
}

void loop() {
  wdt_reset();
  messageParser.update();
  // Standard protocol
  wdt_reset();
  handleResetCommand(messageParser, messageSender);
  handleVersionCommand(messageParser, messageSender);
  handleEchoCommand(messageParser, messageSender);
  handleIOCommand(messageParser, messageSender);
}
