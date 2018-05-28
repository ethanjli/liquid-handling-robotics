#include "CoreProtocol.h"

#include <avr/wdt.h>

namespace LiquidHandlingRobotics {

void handleResetCommand(MessageParser &messageParser) {
  if (!(messageParser.justReceived() &&
        messageParser.channel[0] == kResetChannel &&
        messageParser.channelParsedLength() == 1)) return;
  sendChannelStart();
  sendChannelChar(kResetChannel);
  sendChannelEnd();
  sendPayload(messageParser.payload);
  hardReset();
}

void hardReset() {
  wdt_enable(WDTO_15MS);
  while (true); // Hang to force the AVR watchdog timer to reset the Arduino
}

void handleVersionCommand(MessageParser &messageParser) {
  if (!(messageParser.justReceived() &&
        messageParser.channel[0] == kVersionChannel &&
        messageParser.channelParsedLength() <= 2)) return;

  if (messageParser.channelParsedLength() == 1) sendAllVersionMessages();
  else sendVersionMessage(messageParser.channel[1]);
}

void sendVersionMessage(char versionPosition) {
  int channelPosition = versionPosition - '0';
  if (channelPosition < 0 || channelPosition >= 3) return;
  sendChannelStart();
  sendChannelChar(kVersionChannel);
  sendChannelChar(versionPosition);
  sendChannelEnd();
  sendPayload((int) pgm_read_word_near(kVersion + channelPosition));
}

void sendAllVersionMessages() {
  sendVersionMessage('2');
  wdt_reset();
  sendVersionMessage('1');
  wdt_reset();
  sendVersionMessage('0');
  wdt_reset();
}

void handleEchoCommand(MessageParser &messageParser) {
  if (!(messageParser.justReceived() &&
        messageParser.channel[0] == kEchoChannel &&
        messageParser.channelParsedLength() == 1)) return;

  sendChannelStart();
  sendChannelChar(kEchoChannel);
  sendChannelEnd();
  sendPayload(messageParser.payload);
}

void handleIOCommand(MessageParser &messageParser) {
  if (!messageParser.justReceived()) return;
  if (messageParser.channel[0] != kIOChannel) return;
  if (messageParser.channel[1] != kIOReadChannel) return;
  const int pin = messageParser.payload;

  switch (messageParser.channel[2]) {
    case kIOReadAnalogChannel:
      if (messageParser.channelParsedLength() != 3) break;
      if (pin < kAnalogReadMinPin || pin > kAnalogReadMaxPin) break;
      messageParser.sendResponse(analogRead(pin + kAnalogPinOffset));
      break;
    case kIOReadDigitalChannel:
      if (messageParser.channelParsedLength() != 3) break;
      if (pin < kDigitalReadMinPin || pin > kDigitalReadMaxPin) break;
      messageParser.sendResponse(digitalRead(pin));
      break;
  }
}

}

