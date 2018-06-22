#define DISABLE_LOGGING

#define LHR_Messaging_FirmataIO
#define LHR_Protocol_Core
#define LHR_Protocol_Board
#define LHR_Protocol_AbsoluteLinearActuatorAxis
#include <LiquidHandlingRobotics.h>
#include <StandardLiquidHandlingRobot.h>

using Transport = LiquidHandlingRobotics::Messaging::FirmataTransport;
using Messager = LiquidHandlingRobotics::Messaging::FirmataMessager;
using Core = LiquidHandlingRobotics::Protocol::Core<Messager>;
using Board = LiquidHandlingRobotics::Protocol::Board<Messager>;
using AbsoluteLinearActuatorAxis = LiquidHandlingRobotics::Protocol::LinearActuatorAxis<
  LinearPositionControl::Control::AbsoluteLinearActuator,
  Messager
>;

// Shared Components
LinearPositionControl::Components::Motors motors;
Transport transport;
Messager messager(transport);
LHR_makeFirmataTransportResetCallback(transport);

// Protocol
Core core(messager);
Board board(messager);
AbsoluteLinearActuatorAxis pipettorAxis(messager, motors, LHR_kPipettorParams);
AbsoluteLinearActuatorAxis zAxis(messager, motors, LHR_kVerticalPositionerParams);

void setup() {
  core.setup();
  transport.setup();
  LHR_attachFirmataTransportResetCallback(transport);
  messager.setup();
  board.setup();
  pipettorAxis.setup();
  zAxis.setup();

  messager.establishConnection();
  core.onConnect();
  board.onConnect();
  pipettorAxis.onConnect();
  zAxis.onConnect();
}

void loop() {
  transport.update();
  messager.update();
  core.update();
  board.update();
  pipettorAxis.update();
  zAxis.update();
}
