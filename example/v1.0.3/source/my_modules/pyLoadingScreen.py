import asyncio
from time import sleep
from math import sin, cos, tan, asin, acos, atan, degrees, radians
from PyQt5 import QtCore, QtGui, QtWidgets



class LoadingScreen(QtWidgets.QFrame):
    """ Loading screen by a.s.akulov.

        Tested on python: 3.7.4, windows: x32, x64

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

            Note:
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
        
    """
    class MyDrawingPlace(QtWidgets.QWidget):
        signalMakeStep = QtCore.pyqtSignal()
        signalUpdateDrawPlace = QtCore.pyqtSignal()
        def __init__(self, main: object,
                facesCount = 20,
                color = (255, 0, 0),
                colorRainbow = True,
                colorRainbowStep = 2,
                colorRainbowMinValues = (0, 0, 0),
                colorRainbowMaxValues = (255, 255, 255),
                lineWidth = 3,
                scale = 0.85,
                countStepsPerRound = 1440
                ):
            """INIT."""
            QtWidgets.QWidget.__init__(self)

            self.main = main
            self.setParent(self.main)
            self.worker = self._worker()
            self.signalMakeStep.connect(lambda: next(self.worker))
            self.signalUpdateDrawPlace.connect(self.update)

            self.facesCount = facesCount
            self.color = color
            self.colorRainbow = colorRainbow
            self.colorRainbowStep = colorRainbowStep
            self.colorRainbowMinValues = colorRainbowMinValues
            self.colorRainbowMaxValues = colorRainbowMaxValues
            self.lineWidth = lineWidth
            self.scale = scale
            self.countStepsPerRound = countStepsPerRound # Rotation speed

            self._colorRainbowGeneratorInstance = self._colorRainbowGenerator()
            self._currentAngle = 0
            self._lines = []


        def mouseMoveEvent(self, event: object):
            """QtWidgets.QWidget.mouseMoveEvent"""
            if self.main.isMovingAllowed:
                eventPos = event.globalPos()
                widgetSize = self.main.size()
                self.main.signalMove.emit(eventPos.x() - widgetSize.width() / 2, eventPos.y() - widgetSize.height() / 2)


        def paintEvent(self, event: object):
            """QtWidgets.QWidget.paintEvent"""
            painter = QtGui.QPainter(self)
            painter.setRenderHint(painter.RenderHint.Antialiasing)
            painter.setRenderHint(painter.RenderHint.SmoothPixmapTransform)

            # configure standart drawing
            styleOption = QtWidgets.QStyleOption()
            styleOption.initFrom(self)
            self.style().drawPrimitive(QtWidgets.QStyle.PE_Widget, styleOption, painter, self)

            # start paint
            if not self.colorRainbow:
                color = QtGui.QColor(*self.color)
            else:
                color = QtGui.QColor(*next(self._colorRainbowGeneratorInstance))
            painter.setPen(QtGui.QPen(
                QtGui.QBrush(color),
                self.lineWidth,
                cap=QtCore.Qt.RoundCap,
                join=QtCore.Qt.RoundJoin,
                ))

            for line in self._lines:
                painter.drawLine(line[0][0], line[0][1], line[1][0], line[1][1])

            # end paint
            painter.end()


        def _worker(self):
            """Lines generator."""
            counter = 0
            while True:
                # prepaire variables
                drawPlaceGeometry = self.geometry()
                center = (int(drawPlaceGeometry.width() / 2), int(drawPlaceGeometry.height() / 2))
                angleStep = 360 / self.facesCount
                radiusOuter = max(center) * self.scale
                radiusInner = radiusOuter / 2

                # angle triggers
                angleTriggerStep = (degrees(acos(((radiusInner**2 - ((2*radiusInner*sin(radians(180/self.facesCount)))/2)**2) ** 0.5) / radiusOuter)) + 360/self.facesCount/2) / 2
                angleTriggerLeft1 = 360 - angleTriggerStep
                angleTriggerRight1 = angleTriggerStep
                angleTriggerLeft2 = 180 - angleTriggerStep
                angleTriggerRight2 = 180 + angleTriggerStep

                # build lines properties
                self._lines = []

                outerDots = []
                innerDots = []
                for idx in range(self.facesCount):
                    # outer dot
                    angleDot = self._currentAngle + (angleStep * idx)
                    radiusDot = radiusOuter
                    if self._currentAngle >= angleTriggerLeft1: # decrease radius
                        radiusDot = radiusDot - (radiusDot * ((self._currentAngle - angleTriggerLeft1) / angleStep))
                    elif self._currentAngle <= angleTriggerRight1: # increase radius
                        radiusDot = radiusDot - (radiusDot * ((angleTriggerRight1 - self._currentAngle) / angleStep))

                    elif self._currentAngle >= angleTriggerLeft2 and self._currentAngle <= 180: # decrease radius
                        radiusDot = radiusDot - (radiusDot * ((self._currentAngle - angleTriggerLeft2) / angleStep))
                    elif self._currentAngle <= angleTriggerRight2 and self._currentAngle >= 180: # increase radius
                        radiusDot = radiusDot - (radiusDot * ((angleTriggerRight2 - self._currentAngle) / angleStep))

                    x = round(center[0] + cos(radians(angleDot)) * radiusDot)
                    y = round(center[1] + sin(radians(angleDot)) * radiusDot)
                    outerDots.append((x, y))

                    # inner dot
                    angleDot = - self._currentAngle - (angleStep * idx)
                    radiusDot = radiusInner
                    if self._currentAngle >= angleTriggerLeft1: # increase radius
                        radiusDot = radiusDot + (radiusDot * ((self._currentAngle - angleTriggerLeft1) / angleStep))
                    elif self._currentAngle <= angleTriggerRight1: # decrease radius
                        radiusDot = radiusDot + (radiusDot * ((angleTriggerRight1 - self._currentAngle) / angleStep))

                    elif self._currentAngle >= angleTriggerLeft2 and self._currentAngle <= 180: # increase radius
                        radiusDot = radiusDot + (radiusDot * ((self._currentAngle - angleTriggerLeft2) / angleStep))
                    elif self._currentAngle <= angleTriggerRight2 and self._currentAngle >= 180: # decrease radius
                        radiusDot = radiusDot + (radiusDot * ((angleTriggerRight2 - self._currentAngle) / angleStep))

                    x = round(center[0] + cos(radians(angleDot)) * radiusDot)
                    y = round(center[1] + sin(radians(angleDot)) * radiusDot)
                    innerDots.append((x, y))
                
                for idx in range(self.facesCount):
                    if idx == (self.facesCount - 1):
                        # outer line
                        self._lines.append((outerDots[idx], outerDots[0]))
                        # inner line
                        self._lines.append((innerDots[idx], innerDots[0]))
                    else:
                        # outer line
                        self._lines.append((outerDots[idx], outerDots[idx + 1]))
                        # inner line
                        self._lines.append((innerDots[idx], innerDots[idx + 1]))

                    # connecting line
                    self._lines.append((outerDots[idx], innerDots[-idx]))

                self.signalUpdateDrawPlace.emit()
                yield
                # make angle step
                counter += 1
                if counter < self.countStepsPerRound + 1:
                    self._currentAngle += 360/self.countStepsPerRound
                else:
                    counter = 0
                    self._currentAngle = 0
                
        
        def _colorRainbowGenerator(self):
            """Generating color for color rainbow."""
            currentColor = list(self.colorRainbowMinValues)

            stepsCount = round(3570 / self.colorRainbowStep)
            stepsByTask = round(stepsCount / 15) # 15 - count of tasks
            while True:
                for idxStep in range(stepsCount):
                    taskId = int(idxStep / stepsByTask)

                    if taskId == 0: # 0th task
                        currentColor[0] += self.colorRainbowStep
                    elif taskId == 1: # 1th task
                        currentColor[1] += self.colorRainbowStep
                    elif taskId == 2: # 2th task
                        currentColor[0] -= self.colorRainbowStep
                    elif taskId == 3: # 3th task
                        currentColor[2] += self.colorRainbowStep
                    elif taskId == 4: # 4th task
                        currentColor[1] -= self.colorRainbowStep
                    elif taskId == 5: # 5th task
                        currentColor[0] += self.colorRainbowStep
                    elif taskId == 6: # 6th task
                        currentColor[1] += self.colorRainbowStep

                    elif taskId == 7: # 7th task
                        currentColor[2] -= self.colorRainbowStep
                    elif taskId == 8: # 8th task
                        currentColor[0] -= self.colorRainbowStep
                        currentColor[2] += self.colorRainbowStep
                    elif taskId == 9: # 9th task
                        currentColor[1] -= self.colorRainbowStep
                        currentColor[0] += self.colorRainbowStep
                    elif taskId == 10: # 10th task
                        currentColor[2] -= self.colorRainbowStep
                    elif taskId == 11: # 11th task
                        currentColor[0] -= self.colorRainbowStep
                        currentColor[1] += self.colorRainbowStep
                    elif taskId == 12: # 12th task
                        currentColor[1] -= self.colorRainbowStep
                        currentColor[2] += self.colorRainbowStep
                    elif taskId == 13: # 13th task
                        currentColor[0] += self.colorRainbowStep
                        currentColor[1] += self.colorRainbowStep
                    elif taskId == 14: # 14th task
                        currentColor[0] -= self.colorRainbowStep
                        currentColor[1] -= self.colorRainbowStep
                        currentColor[2] -= self.colorRainbowStep

                    for idx in range(3):
                        if currentColor[idx] < self.colorRainbowMinValues[idx]:
                            currentColor[idx] = self.colorRainbowMinValues[idx]
                        elif currentColor[idx] > self.colorRainbowMaxValues[idx]:
                            currentColor[idx] = self.colorRainbowMaxValues[idx]
                                        
                    yield currentColor




    signalShow = QtCore.pyqtSignal()
    signalClose = QtCore.pyqtSignal()
    signalSetLabelText = QtCore.pyqtSignal(str)
    signalMove = QtCore.pyqtSignal(float, float)

    def __init__(self, 
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
            animationScale = 0.85,
            animationCountStepsPerRound = 1440,
            ):
        """INIT."""
        ################## GUI
        QtWidgets.QFrame.__init__(self)
        self.ui = QtCore.QObject()
        if parentWidget != None:
            self.setParent(parentWidget)
            self.setMinimumSize(*windowSize)
            self.setMaximumSize(*windowSize)
            self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            self.isMovingAllowed = False
        else:
            self.resize(*windowSize)
            self.isMovingAllowed = True

        self.setObjectName("LoadingScreenMainWindow")
        self.setFrameShape(self.Box)
        self.setLineWidth(mainFrameWidth)
        self.setStyleSheet(mainStyleSheet)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.signalShow.connect(self.show)
        self.signalClose.connect(self.close)
        self.signalMove.connect(self.move)

            # main layout
        self.ui.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.ui.verticalLayout.setObjectName("verticalLayout")
        self.ui.verticalLayout.setContentsMargins(0, 0, 0, 6)
        self.ui.verticalLayout.setSpacing(0)

            # draw place
        self.ui.drawPlace = self.MyDrawingPlace(self,
            facesCount=animationFacesCount,
            color=animationRGBColor,
            colorRainbow=animationColorRainbow,
            colorRainbowStep=animationColorRainbowStep,
            colorRainbowMinValues=animationColorRainbowMinValues,
            colorRainbowMaxValues=animationColorRainbowMaxValues,
            lineWidth=animationLineWidth,
            scale=animationScale,
            countStepsPerRound=animationCountStepsPerRound
            )
        self.ui.drawPlace.setObjectName("drawPlace")
        self.ui.drawPlace.setStyleSheet(mainStyleSheet)
        self.ui.verticalLayout.addWidget(self.ui.drawPlace)
            # text label
        self.ui.textLabel = QtWidgets.QLabel(self)
        self.ui.textLabel.setObjectName("textLabel")
        self.ui.textLabel.setStyleSheet(textLabelStyleSheet)
        self.ui.textLabel.setAlignment(QtCore.Qt.AlignHCenter)
        self.signalSetLabelText.connect(self.ui.textLabel.setText)
        self.ui.verticalLayout.addWidget(self.ui.textLabel)

            # other
        self.ui.verticalLayout.setStretch(0, 1)
        ################## OTHER
        self.texts = texts
        self.textUpdateDelay = textUpdateDelay

        self.exit = False
        self.isRunning = False
        self._textGeneratorInstance = self._textGenerator()

        self._window = None
        self._delayTimer = 0
        self._iterationDelay = 333e-4 # 30 frames per second
    

    def _textGenerator(self):
        """Generator for self.texts."""
        while True:
            for text in self.texts:
                yield text


    def _gui_create(self):
        """Create window for loading screen."""
        self.signalShow.emit()


    def _gui_destroy(self):
        """Destroy created loading screen."""
        self.signalClose.emit()


    def _worker(self):
        """Main cycle inner function of animation."""
        self.isRunning = True

        self._gui_create()

        # first label set text
        self.signalSetLabelText.emit(next(self._textGeneratorInstance))

        while not self.exit:
            self._delayTimer += self._iterationDelay
            if self._delayTimer > self.textUpdateDelay:
                self._delayTimer = 0
                # label set text
                self.signalSetLabelText.emit(next(self._textGeneratorInstance))
            
            # main animation
            if self.ui.drawPlace.isVisible():
                self.ui.drawPlace.signalMakeStep.emit()
            
            yield

        else:
            self.ui.drawPlace.worker.close()
            self.ui.drawPlace._colorRainbowGeneratorInstance.close()
            self._textGeneratorInstance.close()
            self._gui_destroy()
            self.isRunning = False
            return 0
    

    def worker(self):
        """Entry cycle."""
        worker = self._worker()
        while True:
            sleep(self._iterationDelay)

            # check for self.worker.exit:
            if '_exit' in self.worker.__dict__:
                if self.worker.__dict__['_exit']:
                    self.exit = True

            # make next step
            try:
                next(worker)
            except StopIteration as answer:
                state = answer.value
                break
        
        worker.close()
        return state

    
    @asyncio.coroutine
    async def worker_async(self):
        """Entry async cycle."""
        worker = self._worker()
        while True:
            await asyncio.sleep(self._iterationDelay)

            # check for self.worker.exit:
            if '_exit' in self.worker_async.__dict__:
                if self.worker_async.__dict__['_exit']:
                    self.exit = True

            # make next step
            try:
                next(worker)
            except StopIteration as answer:
                state = answer.value
                break
        
        worker.close()
        return state