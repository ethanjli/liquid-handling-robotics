#ifndef CoreProtocol_tpp
#define CoreProtocol_tpp

#include <avr/wdt.h>

namespace LiquidHandlingRobotics {

template<class Transport>
void handleResetCommand(Messager<Transport> &messager) {
  if (!(messager.parser.justReceived() &&
        messager.parser.channel[0] == kResetChannel &&
        messager.parser.channelParsedLength() == 1)) return;
  messager.sender.sendChannelStart();
  messager.sender.sendChannelChar(kResetChannel);
  messager.sender.sendChannelEnd();
  messager.sender.sendPayload(messager.parser.payload);
  hardReset();
}

void hardReset() {
  wdt_enable(WDTO_15MS);
  while (true); // Hang to force the AVR watchdog timer to reset the Arduino
}

template<class Transport>
void handleVersionCommand(Messager<Transport> &messager) {
  if (!(messager.parser.justReceived() &&
        messager.parser.channel[0] == kVersionChannel &&
        messager.parser.channelParsedLength() <= 2)) return;

  if (messager.parser.channelParsedLength() == 1) sendAllVersionMessages(messager.sender);
  else sendVersionMessage(messager.parser.channel[1], messager.sender);
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
void handleEchoCommand(Messager<Transport> &messager) {
  if (!(messager.parser.justReceived() &&
        messager.parser.channel[0] == kEchoChannel &&
        messager.parser.channelParsedLength() == 1)) return;

  messager.sender.sendChannelStart();
  messager.sender.sendChannelChar(kEchoChannel);
  messager.sender.sendChannelEnd();
  messager.sender.sendPayload(messager.parser.payload);
}

template<class Transport>
void handleIOCommand(Messager<Transport> &messager) {
  if (!messager.parser.justReceived()) return;
  if (messager.parser.channel[0] != kIOChannel) return;
  if (messager.parser.channel[1] != kIOReadChannel) return;
  const int pin = messager.parser.payload;

  switch (messager.parser.channel[2]) {
    case kIOReadAnalogChannel:
      if (messager.parser.channelParsedLength() != 3) break;
      if (pin < kAnalogReadMinPin || pin > kAnalogReadMaxPin) break;
      messager.sendResponse(analogRead(pin + kAnalogPinOffset));
      break;
    case kIOReadDigitalChannel:
      if (messager.parser.channelParsedLength() != 3) break;
      if (pin < kDigitalReadMinPin || pin > kDigitalReadMaxPin) break;
      messager.sendResponse(digitalRead(pin));
      break;
  }
}

}

#endif

