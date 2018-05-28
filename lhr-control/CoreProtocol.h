#ifndef CoreProtocol_h
#define CoreProtocol_h

#include "Messages.h"

namespace LiquidHandlingRobotics {

const uint16_t kVersion[] PROGMEM = {
  0, // Major
  1, // Minor
  0  // Patch
};

const char kResetChannel = 'r';
const char kVersionChannel = 'v';
const char kEchoChannel = 'e';
const char kIOChannel = 'i';
const char kIOReadChannel = 'r';
const char kIOReadAnalogChannel = 'a';
const char kIOReadDigitalChannel = 'd';

const uint8_t kAnalogPinOffset = 14;
const uint8_t kAnalogReadMinPin = 0;
const uint8_t kAnalogReadMaxPin = 5;
const uint8_t kDigitalReadMinPin = 2;
const uint8_t kDigitalReadMaxPin = 13;

void handleResetCommand(MessageParser &messageParser);
void hardReset();
void handleVersionCommand(MessageParser &messageParser);
void sendVersionMessage(char versionPosition);
void sendAllVersionMessages();
void handleEchoCommand(MessageParser &messageParser);
void handleIOCommand(MessageParser &messageParser);

}

#endif

