#ifndef CoreProtocol_tpp
#define CoreProtocol_tpp

#include <avr/wdt.h>

namespace LiquidHandlingRobotics {

template<class Transport>
void handleResetCommand(MessageParser<Transport> &messageParser, MessageSender<Transport> &messageSender) {
  if (!(messageParser.justReceived() &&
        messageParser.channel[0] == kResetChannel &&
        messageParser.channelParsedLength() == 1)) return;
  messageSender.sendChannelStart();
  messageSender.sendChannelChar(kResetChannel);
  messageSender.sendChannelEnd();
  messageSender.sendPayload(messageParser.payload);
  hardReset();
}

void hardReset() {
  wdt_enable(WDTO_15MS);
  while (true); // Hang to force the AVR watchdog timer to reset the Arduino
}

template<class Transport>
void handleVersionCommand(MessageParser<Transport> &messageParser, MessageSender<Transport> &messageSender) {
  if (!(messageParser.justReceived() &&
        messageParser.channel[0] == kVersionChannel &&
        messageParser.channelParsedLength() <= 2)) return;

  if (messageParser.channelParsedLength() == 1) sendAllVersionMessages(messageSender);
  else sendVersionMessage(messageParser.channel[1], messageSender);
}

template<class Transport>
void sendVersionMessage(char versionPosition, MessageSender<Transport> &messageSender) {
  int channelPosition = versionPosition - '0';
  if (channelPosition < 0 || channelPosition >= 3) return;
  messageSender.sendChannelStart();
  messageSender.sendChannelChar(kVersionChannel);
  messageSender.sendChannelChar(versionPosition);
  messageSender.sendChannelEnd();
  messageSender.sendPayload((int) pgm_read_word_near(kVersion + channelPosition));
}

template<class Transport>
void sendAllVersionMessages(MessageSender<Transport> &messageSender) {
  sendVersionMessage('2', messageSender);
  wdt_reset();
  sendVersionMessage('1', messageSender);
  wdt_reset();
  sendVersionMessage('0', messageSender);
  wdt_reset();
}

template<class Transport>
void handleEchoCommand(MessageParser<Transport> &messageParser, MessageSender<Transport> &messageSender) {
  if (!(messageParser.justReceived() &&
        messageParser.channel[0] == kEchoChannel &&
        messageParser.channelParsedLength() == 1)) return;

  messageSender.sendChannelStart();
  messageSender.sendChannelChar(kEchoChannel);
  messageSender.sendChannelEnd();
  messageSender.sendPayload(messageParser.payload);
}

template<class Transport>
void handleIOCommand(MessageParser<Transport> &messageParser, MessageSender<Transport> &messageSender) {
  if (!messageParser.justReceived()) return;
  if (messageParser.channel[0] != kIOChannel) return;
  if (messageParser.channel[1] != kIOReadChannel) return;
  const int pin = messageParser.payload;

  switch (messageParser.channel[2]) {
    case kIOReadAnalogChannel:
      if (messageParser.channelParsedLength() != 3) break;
      if (pin < kAnalogReadMinPin || pin > kAnalogReadMaxPin) break;
      //messageParser.sendResponse(analogRead(pin + kAnalogPinOffset));
      messageSender.sendMessage(messageParser.channel, messageParser.payload);
      break;
    case kIOReadDigitalChannel:
      if (messageParser.channelParsedLength() != 3) break;
      if (pin < kDigitalReadMinPin || pin > kDigitalReadMaxPin) break;
      //messageParser.sendResponse(digitalRead(pin));
      messageSender.sendMessage(messageParser.channel, digitalRead(pin));
      break;
  }
}

}

#endif

