#define DISABLE_LOGGING

#include <FirmataIO.h>
#include <CoreProtocol.h>
#include <Modules.h>

using namespace LiquidHandlingRobotics;

// Firmata communications
FirmataTransport transport;
FirmataMessager messager(transport);
makeFirmataTransportResetCallback(transport);

// Shared components
CoreProtocol<FirmataMessager> coreProtocol(messager);
LinearPositionControl::Components::Motors motors;

// Subsystems
AbsoluteLinearActuator<FirmataMessager> pipettor(messager, motors, kPipettorParams);

void setup()
{
  coreProtocol.setup();
  transport.setup();
  attachFirmataTransportResetCallback(transport);
  messager.setup();
  pipettor.setup();
  messager.establishConnection();
  coreProtocol.onConnect();
}

void loop() {
  transport.update();
  messager.update();
  coreProtocol.update();
  // Modules
  pipettor.update();
}
