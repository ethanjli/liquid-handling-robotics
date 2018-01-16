#include "ASCIISerialIO.h"

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
  delay(waitDelay);
}

void sendMessage(
    const String &channel, int payload,
    char channelStartDelimiter, char channelEndDelimiter,
    char payloadStartDelimiter, char payloadEndDelimiter
) {
  Serial.print(channelStartDelimiter);
  Serial.print(channel);
  Serial.print(channelEndDelimiter);
  Serial.print(payloadStartDelimiter);
  Serial.print(payload);
  Serial.print(payloadEndDelimiter);
  Serial.println();
}

// ChannelParser

ChannelParser::ChannelParser(char startDelimiter, char endDelimiter) :
  startDelimiter(startDelimiter), endDelimiter(endDelimiter) {}

void ChannelParser::setup() {
  channelBuffer[0] = '\0';
}

void ChannelParser::update() {
  justUpdated = false;
  while (Serial.available() > 0) {
    char current = Serial.read();
    if (current == startDelimiter) {
      bufferPosition = 0;
      justUpdated = false;
    } else if (current == endDelimiter) {
      channelBuffer[bufferPosition] = '\0';
      bufferPosition = -1;
      strlcpy(channel, channelBuffer, kChannelMaxLength + 1);
      justUpdated = true;
      break;
    } else if (bufferPosition >= 0) {
      if (isAlphaNumeric(current)) {
        if (bufferPosition < kChannelMaxLength) {
          channelBuffer[bufferPosition] = current;
          ++bufferPosition;
        } else {
          Log.error(F("Channel name overflowed, ignoring extra character %c!" CR), current);
        }
      } else if (!isWhitespace(current) && !isControl(current)) {
        Log.error(F("Channel name has illegal character %c, ignoring it!" CR), current);
      }
    }
  }
}

// IntParser

IntParser::IntParser(char startDelimiter, char endDelimiter) :
  startDelimiter(startDelimiter), endDelimiter(endDelimiter) {}

void IntParser::setup() {
  result.setup(0);
}

void IntParser::update() {
  result.update(result.current());
  justUpdated = false;
  while (Serial.available() > 0) {
    char current = Serial.read();
    received.update(current);
    if (current == endDelimiter || current == startDelimiter) {
      if (current == endDelimiter) {
        if (negative) result.update(-1 * receivedNumber, true);
        else result.update(receivedNumber, true);
        justUpdated = true;
        break;
      }
      receivedNumber = 0;
      negative = false;
    } else if (current == '-' && received.previous() == startDelimiter) {
      negative = true;
    } else if (isDigit(current)) {
      receivedNumber *= 10;
      receivedNumber += current - '0';
    }
  }
}

}

