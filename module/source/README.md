# py-loading-screen

Module for Python - animated loading screen
Used modules:
  1. asyncio
  2. time.sleep
  3. math.sin, math.cos, math,radians
  4. PyQt5.QtCore, PyQt5.QtWidgets, PyQt5.QtGui

Tested on python: 3.7.4, windows: x32, x64

Installing:

    $ pip install py-loading-screen

import:

    $ from pyLoadingScreen import LoadingScreen

If by some reason you have not python interpreter - you can see compiled demo-application (windows): 'example\compiled'

LoadingScreen(PyQt5.QtWidgets.QFrame)

Params:

    texts = ['Loading', 'Loading.', 'Loading..', 'Loading...'],
    textUpdateDelay = 0.75,
    parentWidget = None,
    windowSize = (350, 350),
    mainStyleSheet = "background-color: black; color: rgb(80, 0, 255);",
    mainFrameWidth = 3,
    textLabelStyleSheet = "background-color: black; color: white; font: bold 18px;",
    animationFacesCount = 20,
    animationRGBColor = (255, 0, 0),
    animationColorRainbow = True,
    animationColorRainbowStep = 2,
    animationColorRainbowMinValues = (0, 0, 0),
    animationColorRainbowMaxValues = (255, 255, 255),
    animationLineWidth = 3,
    animationScale = 0.9,
    animationCountStepsPerRound = 1440


Notes:

    1. I recommend running this in a new thread. Anyway, you need to create instance of LoadingScreen at main thread, then start worker function in any thread.
        If you want to start in new 'clear' thread - use 'worker' function, else if you wont to create task with asyncio - use 'worker_asyncio' coroutine.
        Variable with LoadingScreen instance must exist all time while script is running!
        - New thread start example:
        "self.screen = LoadingScreen()
         self.thread = threading.Thread(target=self.screen.worker)
         self.thread.start()"
        - Asyncio create task example:
        "self.screen = LoadingScreen()
         loop = asyncio.get_event_loop()
         asyncio.gather(self.screen.worker_async(), loop=loop)"
    
    2. To stop work use 'exit' attribute of LoadingScreen instance or create attribute '_exit' in 'worker' or 'worker_async' function.
        Work is stop after some time after signal to exit. You can check LoadingScreen instance state by 'isRunning' attribute.
        Example:
        "self.screen = LoadingScreen()
         self.thread = threading.Thread(target=self.screen.worker)
         self.thread.start()
         self.screen.exit = True
         self.screen.worker.__dict__['exit'] = True # Equivalent to 'self.screen.exit = True'
         self.screen.worker_async.__dict__['exit'] = True # Equivalent to 'self.screen.exit = True', but in this case - will not take any effect, because 'worker' is using insted ('self.thread = threading.Thread(target=self.screen.worker)')
         while True:
             time.sleep(1)
             if self.screen.isRunning:
                 print('LoadingScreen is still running)
             else:
                 print('LoadingScreen is not running)
                 break"

    3. If you set parentWidget - don't forget add LoadingScreen to parentWidget's layout!
        Example:
        "self.screen = LoadingScreen(parentWidget=self.ui.myParentWidget)
         myParentWidget.layout().addWidget(self.screen)"
    4. If animationColorRainbow == True, then param 'animationRGBColor' ignored

    5. If animationColorRainbow == False, then params ignored:
        animationColorRainbowStep,
        animationColorRainbowMinValues,
        animationColorRainbowMaxValues
    
    6. animationCountStepsPerRound - speed of rotation. animationCountStepsPerRound increases - rotation speed decreases

    7. By some reason i can't create instance of LoadingScreen in Spyder (Anaconda, Python 3.7.4), but in outer program this work fine.




































