#ifndef ASCIISerialIO_h
#define ASCIISerialIO_h

#include "Messages.h"

namespace LiquidHandlingRobotics {

void waitForSerialHandshake(char handshakeChar = '~', unsigned long waitDelay = 500);

}

#endif

