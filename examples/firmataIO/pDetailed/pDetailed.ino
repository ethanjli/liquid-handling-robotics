#define DISABLE_LOGGING

#define LHR_Messaging_FirmataIO
#define LHR_Protocol_Core
#define LHR_Protocol_AbsoluteLinearActuatorAxis
#include <LiquidHandlingRobotics.h>
#include <StandardLiquidHandlingRobot.h>

using Transport = LiquidHandlingRobotics::Messaging::FirmataTransport;
using Messager = LiquidHandlingRobotics::Messaging::FirmataMessager;
using Core = LiquidHandlingRobotics::Protocol::Core<Messager>;
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
AbsoluteLinearActuatorAxis pipettorAxis(messager, motors, LHR_kPipettorParams);

void setup() {
  core.setup();
  transport.setup();
  LHR_attachFirmataTransportResetCallback(transport);
  messager.setup();
  pipettorAxis.setup();

  messager.establishConnection();
  core.onConnect();
  pipettorAxis.onConnect();
}

void loop() {
  transport.update();
  messager.update();
  core.update();
  pipettorAxis.update();
}
