#define DISABLE_LOGGING

#define LHR_Messaging_FirmataIO
#define LHR_Protocol_Core
#define LHR_Protocol_Board
#include <LiquidHandlingRobotics.h>
#include <StandardLiquidHandlingRobot.h>

using Transport = LiquidHandlingRobotics::Messaging::FirmataTransport;
using Messager = LiquidHandlingRobotics::Messaging::FirmataMessager;
using Core = LiquidHandlingRobotics::Protocol::Core<Messager>;
using Board = LiquidHandlingRobotics::Protocol::Board<Messager>;

// Shared Components
Transport transport;
Messager messager(transport);
LHR_makeFirmataTransportResetCallback(transport);

// Protocol
Core core(messager);
Board board(messager);

void setup() {
  core.setup();
  transport.setup();
  LHR_attachFirmataTransportResetCallback(transport);
  messager.setup();
  board.setup();

  messager.establishConnection();
  core.onConnect();
  board.onConnect();
}

void loop() {
  transport.update();
  messager.update();
  core.update();
  board.update();
}
