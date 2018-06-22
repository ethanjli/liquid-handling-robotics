#ifndef LHR_Protocol_Placeholder_h
#define LHR_Protocol_Placeholder_h

#include <avr/wdt.h>

namespace LiquidHandlingRobotics { namespace Protocol {

class Placeholder {
  public:
    void setup() {}
    void update() {}
    void onConnect() {}
};

} }

#endif

