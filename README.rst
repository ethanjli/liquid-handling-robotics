==========================
 liquid-handling-robotics
==========================

This repository provides control software for low-cost liquid-handling robots.

This repository is associated with the repository at `github.com/amytlam/LHR2021 <https://github.com/amytlam/LHR2021>`_, which collects all files associated with the paper "DIY Liquid Handling Robots for Integrated STEM Education and Life-Science Research".

This software was developed and tested until October 2018 and is not currently maintained or supported. Troubleshooting may be needed to be able to run some of the software in this repository today, requiring familiarity with modern version management tooling for the Python interpreter (e.g. pyenv_) and package dependencies (e.g. poetry_). Basic usage of the software provided by this repository may be possible for a user with familiar with using Arduino libraries and Snap4Arduino.

.. _pyenv: https://github.com/pyenv/pyenv
.. _poetry: https://python-poetry.org/

------------
Architecture
------------

The software is split into two domains:

- Microcontroller software running on the robot's Arduino microcontroller implements low-level motion control of the various linear actuators of the robot, specifically with PID feedback control. It also exposes a USB Serial command interface for higher-level positioning commands from an attached computer.
- Host software running on a computer connected to the Arduino by a USB cable plans, generates, and sends higher-level positioning commands for the Arduino. It maps experiment-specific layouts and setups to positioning commands. Two forms of host software are provided by this repository:

  - A Snap4Arduino support layer, and starter projects, for visual programming of host software.
  - A Python support library, and Python script tools, to assist in obtaining machine-specific tuning and calibration parameters which can then be used by Snap4Arduino projects.

--------
Contents
--------

This repository includes the following types of software:

- `src/`: An Arduino library enabling low-level motion control of liquid-handling robots.
- `examples/`: Arduino sketches using the Arduino library described above to control liquid-handling robots in various possible configurations.

  - `examples/firmataIO`: Arduino sketches exposing a Firmata-based Serial command interface, allowing the Robot to be controlled from within Snap4Arduino and from Python tools provided by this repository.

    - `examples/firmataIO/pzyxRobot`: An Arduino sketch allowing a full four-motor robot (with a pipettor and x, y, and z axes of motion) to be controlled from Snap4Arduino running on a computer connected to the Arduino.

  - `examples/asciiIO`: Arduino sketches exposing an ASCII-based Serial command interface, allowing commands to be sent to the Robot directly from the Arduino IDE's Serial Monitor. These sketches are not needed for recommended usage of the software, but are instead provided to facilitate troubleshooting.

- `s4a/`: Snap4Arduino_ block libraries and example projects for controlling liquid-handling robots from within Snap4Arduino, enabling visual programming to develop software for controlling the robot.

  - `s4a/Robot`: starter projects for controlling fully-integrated robots:

    - `s4a/Robot/serial dilution.xml`: a Snap4Arduino project with a pre-programmed sequence of actions for the robot.
    - `s4a/Robot/preset positions.xml`: a Snap4Arduino project which binds keypresses to robot actions, for interactive control of the robot.

- `lhrhost/`: A Python library enabling high-level control of liquid-handling robots, for development of high-level tools and tests.

  - `lhrhost/tests/dashboard/`: tools providing webpage dashboards for various tasks, such as tuning control parameters for the robot's motor controllers.

    - `lhrhost/tests/dashboard/pid_tuning.py`: a script providing a webpage dashboard for tuning the PID control parameters of a linear actuator in the robot.
    - `lhrhost/tests/dashboard/linear_actuator_batch.py`: a script providing a webpage dashboard for visualizing linear actuator state as the robot runs through a pre-programmed sequence of actions.

  - `lhrhost/tests/robot`: calibration tools and integration tests for fully-integrated robots.

    - `lhrhost/tests/robot/physical_calibration.py`: a tool to calibrate the sensor positions of a linear actuator to physical positions.

.. _Snap4Arduino: https://snap4arduino.rocks

-----
Usage
-----

Usage with Snap4Arduino
=======================

Recommended usage of the software provided by this repository involves setting up the robot's Arduino by uploading a provided Arduino sketch, and then opening an example Snap4Arduino project to get started with controlling the robot.

Arduino Sketch
--------------

These instructions assume a user who is experienced at installing and managing Arduino libraries, both through the Arduino IDE's library manager, and manually.

You will need to use the Arduino IDE to open and upload the sketch at `examples/firmataIO/pzyxRobot`. Install the libraries listed in the README file in that directory, and then upload the sketch for your Arduino (which must be an Arduino Mega). Note that one library will need to be installed manually, by copying it into the "libraries" directory inside your Arduino sketchbook directory.

Snap4Arduino Projects
---------------------

These instructions assume a user who already knows how to use Snap4Arduino import XML project files, to control an Arduino from Snap4Arduino, and to edit custom blocks.

This repository's software for Snap4Arduino was developed for Snap4Arduino version `1.2.6 <https://github.com/bromagosa/Snap4Arduino/releases/tag/1.2.6>`_, which was released in May 2018; it may or may not work on current versions of Snap4Arduino. To use the software, go to Snap4Arduino's File menu, select the "Import..." entry, and open either of the following example projects in order to run it:

- `s4a/Robot/serial dilution.xml`
- `s4a/Robot/preset positions.xml`

Run the Serial Dilution Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plug the Arduino into the computer. Then, in the "Arduino" block palette of Snap4Arduino, press the "Connect Arduino" button.

Then press the Green Flag button; the robot should begin executing its preprogrammed sequence of actions, and the canvas should visualize the state of the robot.

Run the Preset Positions Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plug the Arduino into the computer. Then, in the "Arduino" block palette of Snap4Arduino, press the "Connect Arduino" button.

Then press the Green Flag button; Snap4Arduino should then begin communication with the robot, the robot should move to its home position, and the canvas should print instructions for interactively controlling the robot.

Adjust Robot Tunings & Calibrations
-----------------------------------

Each axis of the robot is associated with a Snap4Arduino block for position sensor calibration and a Snap4Arduino block for motor controller tuning. Different assembled units of the robot will need different configurations for these blocks, due to mechanical variations. These blocks can be found in the "Other" section of the Snap4Arduino block palette, and should be edited for different assembled robot units as needed. The blocks to edit are:

- Sensor calibrations: `p-axis calibration`, `z-axis calibration`, `y-axis calibration`, `x-axis calibration`. These parameters define a linear conversion of position sensor values to physical length units.
- Motor controller tunings: `p-axis controller tunings`, `z-axis controller tunings`, `y-axis controller tunings`, `x-axis controller tunings`. These parameters define the PID control parameters for the different motors.

You can try to optimize these parameters by trial-and-error within Snap4Arduino, or you can try to use the Python tools for assistance with parameter optimization (see next section).

Create Your Own Software
------------------------

It is recommended to use either the Serial Dilution example project or the Preset Positions example project as a starting point for creating your own project with custom behavior for controlling the robot. Robot control blocks are all in the "Other" section of the Snap4Arduino block palette.

Usage of Python Tools
=====================

The Python tools were developed using Python 3.6, with package dependency versions collected in `lhrhost/requirements.txt`. These tools may not work with earlier or later versions of Python; they probably will not work with earlier or later versions of the package dependencies.

These instructions assume a user who is familiar with running Python scripts from a command line, and who has correctly configured the software dependencies described in the previous paragraph. Additionally, these instructions assume that the robot's Arduino was set up according to the instructions in the "Usage with Snap4Arduino" section.

Controller Parameter Tuning
---------------------------

Run the `lhrhost.tests.dashboard.pid_tuning` script with the following command-line arguments:

- `--parser=firmata`: to communicate with an Arduino running the sketch at `examples/firmataIO/pzyxRobot`
- `--axis=p`, `--axis=z`, `--axis=y`, or `--axis=x` to select which linear actuator of the robot to tune.

The script will start a web server at `localhost:5006`; open a web browser at that address to use the graphical dashboard for PID control parameter adjustment. The script will also run a command line to repeatedly move the linear actuator between two target positions while the dashboard visualizes the state of the linear actuator.

Once controller parameters are adjusted so that the controller moves between a variety of target positions accurately and reliably, their values can be manually recorded for editing the Snap4Arduino controller tuning blocks described in the previous "Adjust Robot Tunings & Calibrations" section.

Position Sensor Calibration
---------------------------

Run the `lhrhost.tests.dashboard.physical_calibration` script with the following command-line arguments:

- `--parser=firmata`: to communicate with an Arduino running the sketch at `examples/firmataIO/pzyxRobot`
- `--axis=p`, `--axis=z`, `--axis=y`, or `--axis=x` to select which linear actuator of the robot to calibrate.

The script will repeatedly move the linear actuator to various positions and ask the user to input their physical measurement of the resulting actuator position. After a sufficient number of calibration measurement samples are collected, the script performs linear regression and outputs a slope and intercept value. These values can be manually recorded for editing the Snap4Arduino sensor calibration blocks described in the previous "Adjust Robot Tunings & Calibrations" section.

-----------------------------
Other Associated Repositories
-----------------------------

The Arduino sketches in this repository also rely two other Arduino libraries which were created for this project, but which are provided by two other repositories due to the way Arduino library management works:

- `github.com/ethanjli/linear-position-control <https://github.com/ethanjli/linear-position-control>`_, which provides hardware abstractions for control of the linear actuators designed for this project.
- `github.com/ethanjli/TLV493D-A1B6-3DMagnetic-Sensor <https://github.com/ethanjli/TLV493D-A1B6-3DMagnetic-Sensor>`_, which is a fork of Infineon's official Arduino library for controlling the TLV493D-A1B6 magnetic sensors used in the x and y-axis linear actuators of the robot designed for this project. The fork used by this project only includes two small fixes to make the library work correctly when this software was being developed in 2018.