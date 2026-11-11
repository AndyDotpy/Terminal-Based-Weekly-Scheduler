# Terminal-Based-Weekly-Scheduler

A terminal based weekly scheduler with persistent storage that stores 8 different schedules, 7 for each day of the week and 1 for the current day.

## Overview

This weekly scheduler is built to keep track of what you do on a weekly basis and update your current schedule daily. 
It keeps track of what you do through events and each schedule has their own events. These schedules and events can be 
modified through the several commands shown on the terminal interface. It is recommended to start with the [h] help option 
to best understand the scheduler.

## Tech Stack
- Python 3.10
- Pickle

## Installation

1. Clone repository: git clone https://github.com/AndyDotpy/Terminal-Based-Weekly-Scheduler.git
2. Install pyinstaller: pip install pyinstaller
3. Create the executable: pyinstaller --onefile --name "Weekly Scheduler" --icon=Modern-Weekly-Calendar-Icon.ico main.py
