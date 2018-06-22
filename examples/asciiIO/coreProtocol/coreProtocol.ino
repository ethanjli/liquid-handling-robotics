#define DISABLE_LOGGING
#include <ArduinoLog.h>

#define LHR_Messaging_ASCIIIO
#define LHR_Protocol_Core
#define LHR_Protocol_Board
#include <LiquidHandlingRobotics.h>
#include <StandardLiquidHandlingRobot.h>

using namespace LiquidHandlingRobotics;

LHR_instantiateMessaging(transport, messager);
LHR_instantiateBasics(core, board);

void setup() {
  LHR_setupMessaging(transport, messager, core);
#ifndef DISABLE_LOGGING
  Log.begin(LOG_LEVEL_VERBOSE, &Serial);
#endif
  LHR_setupBasics(core, board);

  LHR_connectMessaging(transport, messager);
  LHR_connectBasics(core, board);
}

void loop() {
  LHR_updateMessaging(transport, messager);
  LHR_updateBasics(core, board);
}
