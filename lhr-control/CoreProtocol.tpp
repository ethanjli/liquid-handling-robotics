#ifndef CoreProtocol_tpp
#define CoreProtocol_tpp

#include <avr/wdt.h>

namespace LiquidHandlingRobotics {

void hardReset() {
  wdt_enable(static_cast<uint8_t>(WatchdogTimeout::to15ms));
  while (true); // Hang to force the AVR watchdog timer to reset the Arduino
}

// CoreProtocol

template<class Messager>
CoreProtocol<Messager>::CoreProtocol(Messager &messager) :
  led(LED_BUILTIN), messager(messager)
{}

template<class Messager>
void CoreProtocol<Messager>::setup() {
  if (setupCompleted) return;

  wdt_disable();
  led.setup();

  setupCompleted = true;
}

template<class Messager>
void CoreProtocol<Messager>::update() {
  /*
  wdt_reset();
  handleResetCommand();
  wdt_reset();
  handleVersionCommand();
  wdt_reset();
  handleEchoCommand();
  wdt_reset();
  handleIOCommand();
  wdt_reset();
  */
  handleBuiltinLEDCommand();
  led.update();
  wdt_reset();
}

template<class Messager>
void CoreProtocol<Messager>::onConnect(WatchdogTimeout timeout) {
  sendAllVersionMessages();
  wdt_enable(static_cast<uint8_t>(timeout));
}

template<class Messager>
void CoreProtocol<Messager>::sendVersionMessage(char versionPosition) {
  int channelPosition = versionPosition - '0';
  if (channelPosition < 0 || channelPosition >= 3) return;
  messager.sender.sendChannelStart();
  messager.sender.sendChannelChar(kVersionChannel);
  messager.sender.sendChannelChar(versionPosition);
  messager.sender.sendChannelEnd();
  messager.sender.sendPayload((int) pgm_read_word_near(kVersion + channelPosition));
}

template<class Messager>
void CoreProtocol<Messager>::sendAllVersionMessages() {
  sendVersionMessage('2');
  wdt_reset();
  sendVersionMessage('1');
  wdt_reset();
  sendVersionMessage('0');
  wdt_reset();
}

template<class Messager>
void CoreProtocol<Messager>::handleResetCommand() {
  if (!(messager.parser.justReceived() &&
        messager.parser.channel[0] == kResetChannel &&
        messager.parser.channelParsedLength() == 1)) return;
  messager.sender.sendChannelStart();
  messager.sender.sendChannelChar(kResetChannel);
  messager.sender.sendChannelEnd();
  messager.sender.sendPayload(messager.parser.payload);
  hardReset();
}

template<class Messager>
void CoreProtocol<Messager>::handleVersionCommand() {
  if (!(messager.parser.justReceived() &&
        messager.parser.channel[0] == kVersionChannel &&
        messager.parser.channelParsedLength() <= 2)) return;

  if (messager.parser.channelParsedLength() == 1) sendAllVersionMessages();
  else sendVersionMessage(messager.parser.channel[1]);
}

template<class Messager>
void CoreProtocol<Messager>::handleEchoCommand() {
  if (!(messager.parser.justReceived() &&
        messager.parser.channel[0] == kEchoChannel &&
        messager.parser.channelParsedLength() == 1)) return;

  messager.sendResponse(messager.parser.payload);
}

template<class Messager>
void CoreProtocol<Messager>::handleIOCommand() {
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

template<class Messager>
void CoreProtocol<Messager>::handleBuiltinLEDCommand() {
  if (!(messager.parser.justReceived() &&
        messager.parser.channel[0] == kBuiltinLEDChannel &&
        messager.parser.channelParsedLength() == 1)) return;

  switch (messager.parser.payload) {
    case 0:
      led.off();
      break;
    case 1:
      led.on();
      break;
    case -1:
      led.blink();
      break;
  }

  //messager.sendResponse(messager.parser.payload);
}

}

#endif

