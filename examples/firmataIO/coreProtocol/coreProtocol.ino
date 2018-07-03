#define DISABLE_LOGGING

#define LHR_Messaging_FirmataIO
#define LHR_Protocol_Core
#define LHR_Protocol_Board
#include <LiquidHandlingRobotics.h>
#include <StandardLiquidHandlingRobot.h>

using namespace LiquidHandlingRobotics;

LHR_instantiateMessaging(transport, messager);
LHR_instantiateBasics(core, board);

void setup()
{
  LHR_setupMessaging(transport, messager, core);
  LHR_setupBasics(core, board);

  LHR_connectMessaging(transport, messager);
  LHR_connectBasics(core, board);
}

void loop() {
  LHR_updateMessaging(transport, messager);
  LHR_updateBasics(core, board);
}
