# SPDX-License-Identifier: Apache-2.0
#
# CMakeLists.txt — Zephyr application build manifest
#
# This tells the Zephyr build system: "this directory is a Zephyr app.
# Find the Zephyr workspace, pull in the build system, and compile my
# source files into a firmware binary for the target board."
#
# The build is invoked with: west build -b nucleo_h753zi firmware
# (or just `west build` from inside the firmware/ directory)

cmake_minimum_required(VERSION 3.20.0)

# find_package(Zephyr) locates the Zephyr workspace and imports the
# Zephyr build system. This is what connects our app to the Zephyr
# tree at C:\Users\dengle\zephyrproject\zephyr.
# REQUIRED HINTS ... tells CMake where to look if the workspace isn't
# auto-discovered. On Windows with west installed, it's usually found
# automatically via the CMake package registry.
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})

# project() sets the project name. This appears in build metadata
# and is required by CMake.
project(phone)

# target_sources() adds our C source files to the build.
# As we add more modules (at_parser.c, keypad.c, display.c, etc.),
# they get listed here.
target_sources(app PRIVATE
    src/main.c
)
