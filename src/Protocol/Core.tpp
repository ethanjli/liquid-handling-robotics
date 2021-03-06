#ifndef LHR_Protocol_Core_tpp
#define LHR_Protocol_Core_tpp

namespace LiquidHandlingRobotics { namespace Protocol {

void hardReset() {
  wdt_enable(static_cast<uint8_t>(WatchdogTimeout::to15ms));
  while (true); // Hang to force the AVR watchdog timer to reset the Arduino
}

// Core

template<class Messager>
Core<Messager>::Core(Messager &messager) :
  messager(messager), parser(messager.parser), sender(messager.sender)
{}

template<class Messager>
void Core<Messager>::setup() {
  if (setupCompleted) return;

  wdt_disable();

  setupCompleted = true;
}

template<class Messager>
void Core<Messager>::update() {
  wdt_reset();
  handleResetCommand();
  wdt_reset();
  handleVersionCommand();
  wdt_reset();
  handleEchoCommand();
  wdt_reset();
}

template<class Messager>
void Core<Messager>::onConnect(WatchdogTimeout timeout) {
  sendAllVersionMessages();
  wdt_enable(static_cast<uint8_t>(timeout));
}

template<class Messager>
void Core<Messager>::sendVersionMessage(char versionPosition) {
  int channelPosition = versionPosition - '0';
  if (channelPosition < 0 || channelPosition >= 3) return;
  sender.sendChannelStart();
  sender.sendChannelChar(Channels::Core::kVersion);
  sender.sendChannelChar(versionPosition);
  sender.sendChannelEnd();
  sender.sendPayload((int) pgm_read_word_near(kVersion + channelPosition));
}

template<class Messager>
void Core<Messager>::sendAllVersionMessages() {
  sendVersionMessage('0');
  wdt_reset();
  sendVersionMessage('1');
  wdt_reset();
  sendVersionMessage('2');
  wdt_reset();
}

template<class Messager>
void Core<Messager>::handleResetCommand() {
  using namespace Channels::Core;

  if (!(parser.justReceived() && parser.channel[0] == kReset &&
        parser.channelParsedLength == 1)) return;
  // parsed as: r
  bool reset = false;
  sender.sendChannelStart();
  sender.sendChannelChar(kReset);
  sender.sendChannelEnd();
  reset = (parser.receivedPayload() && parser.payload == 1);
  sender.sendPayload(reset);
  if (reset) hardReset();
}

template<class Messager>
void Core<Messager>::handleVersionCommand() {
  if (!(parser.justReceived() && parser.channel[0] == Channels::Core::kVersion &&
        parser.channelParsedLength <= 2)) return;

  if (parser.channelParsedLength == 1) sendAllVersionMessages(); // parsed as: v
  else sendVersionMessage(parser.channel[1]); // parsed as: v*
}

template<class Messager>
void Core<Messager>::handleEchoCommand() {
  using namespace Channels::Core;

  if (!(parser.justReceived() && parser.channel[0] == kEcho &&
        parser.channelParsedLength == 1)) return;
  // parsed as: e
  if (parser.receivedPayload()) echoValue = parser.payload;

  messager.sendResponse(echoValue);
}

} }

#endif

