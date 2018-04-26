#include "ASCIISerialIO.h"

#include <avr/wdt.h>

namespace LiquidHandlingRobotics {

void waitForSerialHandshake(char handshakeChar, unsigned long waitDelay) {
  while (!Serial) {;}
  while (Serial.available() < 1) {
    Serial.print(handshakeChar);
    delay(waitDelay);
  }
  while (Serial.available() > 0) {
    if (Serial.read() == '\n') break;
  }
  Serial.println();
  delay(waitDelay);
}

// Message RX/TX

void sendMessage(const String &channel, int payload) {
  sendChannel(channel);
  sendPayload(payload);
}
void sendMessage(const char *channel, int payload) {
  sendChannel(channel);
  sendPayload(payload);
}
void sendChannel(const String &channel) {
  Serial.print(kChannelStartDelimiter);
  // FIXME: Revert
  //Serial.print(channel);
  Serial.print(F("Error"));
  Serial.print(kChannelEndDelimiter);
}
void sendChannel(const char *channel) {
  Serial.print(kChannelStartDelimiter);
  // FIXME: use simple implementation if this is unnecessary
  char *curr = channel;
  while (curr != nullptr && *curr != '\0') {
    if (*curr != 0x7f) Serial.print(*curr);
    ++curr;
  }
  Serial.print(kChannelEndDelimiter);
}
void sendChannelStart() {
  Serial.print(kChannelStartDelimiter);
}
void sendChannelChar(char channelChar) {
  if (channelChar != 0x7f) Serial.print(channelChar); // FIXME: temporary test. Remove if unneeded.
}
void sendChannelEnd() {
  Serial.print(kChannelEndDelimiter);
}
void sendPayloadStart() {
  Serial.print(kPayloadStartDelimiter);
}
void sendPayloadEnd() {
  Serial.print(kPayloadEndDelimiter);
}
void sendPayload(int payload) {
  Serial.print(kPayloadStartDelimiter);
  Serial.print(payload);
  Serial.print(kPayloadEndDelimiter);
  Serial.println();
}

// General Protocol Functionalities

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


// MessageParser

void MessageParser::setup() {
  channelBuffer[0] = '\0';
  state.setup(State::awaitingChannel);
}

void MessageParser::update() {
  if (state.current() == State::parsedMessage) state.update(State::awaitingChannel);
  while (Serial.available() > 0) {
    char current = Serial.read();
    switch (state.current()) {
      case State::awaitingChannel:
        if (current == kChannelStartDelimiter) {
          onParsingChannel();
          state.update(State::parsingChannel);
        }
        break;
      case State::parsingChannel:
        if (current == kChannelEndDelimiter) {
          state.update(State::awaitingPayload);
          onAwaitingPayload();
        } else if (current == kChannelStartDelimiter) {
          onParsingChannel();
          Log.warning(F("Channel name starting with '%s' was interrupted in the middle by a '%c' character. Resetting channel name!" CR), channelBufferString, current);
        } else {
          parseChannel(current);
          state.update(State::parsingChannel, true);
        }
        break;
      case State::awaitingPayload:
        if (current == kPayloadStartDelimiter) {
          onParsingPayload();
          state.update(State::parsingPayload);
        }
        break;
      case State::parsingPayload:
        if (current == kPayloadEndDelimiter) {
          onParsedMessage();
          state.update(State::parsedMessage);
          return; // don't parse more messages until the next update() call
        } else {
          parsePayload(current);
          state.update(State::parsingPayload, true);
        }
    }
  }
}

bool MessageParser::isChannel(const char queryChannel[]) const {
  return strncmp(queryChannel, channel, kChannelMaxLength + 1) == 0;
}

bool MessageParser::justReceived(const char queryChannel[]) const {
  return state.justEntered(State::parsedMessage) && isChannel(queryChannel);
}

bool MessageParser::justReceived() const {
  return state.justEntered(State::parsedMessage);
}

unsigned int MessageParser::payloadParsedLength() const {
  return payloadLength;
}

unsigned int MessageParser::channelParsedLength() const {
  return channelLength;
}

void MessageParser::sendResponse(int payload) {
  sendMessage(channel, payload);
}

void MessageParser::onParsingChannel() {
  memset(channelBuffer, '\0', kChannelMaxLength + 1);
  channelLength = 0;
  channelBufferPosition = 0;
}

void MessageParser::onAwaitingPayload() {
  channelBuffer[channelBufferPosition] = '\0';
  channelBufferPosition = -1;
  strlcpy(channel, channelBuffer, kChannelMaxLength + 1);
}

void MessageParser::onParsingPayload() {
  receivedNumber = 0;
  payloadLength = 0;
  negative = false;
}

void MessageParser::onParsedMessage() {
  if (negative) payload = -1 * receivedNumber;
  else payload = receivedNumber;
}

void MessageParser::parseChannel(char current) {
  if (channelBufferPosition >= 0) {
    if (isAlphaNumeric(current)) {
      if (channelBufferPosition < kChannelMaxLength) {
        channelBuffer[channelBufferPosition] = current;
        ++channelBufferPosition;
        ++channelLength;
      } else {
        Log.error(F("Channel name starting with '%s' is too long. Ignoring extra character '%c'!" CR), channelBufferString, current);
      }
    } else if (!isControl(current)) {
      Log.warning(F("Channel name starting with '%s' has unknown character '%c'. Ignoring it!" CR), channelBufferString, current);
    }
  }
}

void MessageParser::parsePayload(char current) {
  if (current == '-' && state.justEntered(State::parsingPayload)) {
    negative = true;
    ++payloadLength;
  } else if (isDigit(current)) {
    receivedNumber *= 10;
    receivedNumber += current - '0';
    ++payloadLength;
  } else if (!isControl(current)) {
    Log.warning(F("Payload on channel '%s' has unknown character '%c'. Ignoring it!" CR), channelBufferString, current);
  }
}

}

