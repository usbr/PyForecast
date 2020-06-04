"""
Script Name:    ModelCreationTabV2.py

Description:    Defines the layout for the Model Creation Tab. Includes all the sub-widgets
                for the stacked widget.
"""

# Import Libraries
from    PyQt5   import  QtWidgets, \
                        QtCore, \
                        QtGui

from resources.GUI.CustomWidgets.DatasetList_HTML_Formatted import DatasetList_HTML_Formatted
from resources.GUI.CustomWidgets.PyQtGraphs import ModelTabPlots
from resources.GUI.CustomWidgets.customTabs import EnhancedTabWidget
import pandas as pd

WIDTH_BIGGEST_REGR_BUTTON = 0

class richTextButton(QtWidgets.QPushButton):
    
    def __init__(self, parent = None, richText = ""):
        global WIDTH_BIGGEST_REGR_BUTTON

        QtWidgets.QPushButton.__init__(self)
        self.setCheckable(True)
        self.setAutoExclusive(False)
        self.lab = QtWidgets.QLabel(richText, self)
        self.lab.mousePressEvent = lambda ev: self.click()
        self.lab.setTextFormat(QtCore.Qt.RichText)
        
        self.richTextChecked = """
        <table border=0>
        <tr><td><img src="resources/GraphicalResources/icons/check_box-24px.svg"></td>
        <td>{0}</td></tr>
        </table>
        """.format(richText)

        self.richTextUnChecked = """
        <table border=0>
        <tr><td><img src="resources/GraphicalResources/icons/check_box_outline_blank-24px.svg"></td>
        <td>{0}</td></tr>
        </table>
        """.format(richText)

        self.lab.setText(self.richTextUnChecked)
        self.lab.setWordWrap(True)
        self.lab.setContentsMargins(10,10,10,10)
        self.lab.setFixedWidth(self.width())
        self.lab.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        
        
        if self.lab.height() > WIDTH_BIGGEST_REGR_BUTTON:
            WIDTH_BIGGEST_REGR_BUTTON = self.lab.height()
        else:
            self.lab.setMinimumHeight(WIDTH_BIGGEST_REGR_BUTTON)
        self.setFixedHeight(self.lab.height())

        self.lab.setAlignment(QtCore.Qt.AlignTop)
        
    def click(self):
        QtWidgets.QAbstractButton.click(self)
        if self.isChecked():
            self.lab.setText(self.richTextChecked)
        else:
            self.lab.setText(self.richTextUnChecked)

    def resizeEvent(self, ev):
        global WIDTH_BIGGEST_REGR_BUTTON
        QtWidgets.QPushButton.resizeEvent(self,ev)
        self.lab.setFixedWidth(self.width())
        if self.lab.height() > WIDTH_BIGGEST_REGR_BUTTON:
            WIDTH_BIGGEST_REGR_BUTTON = self.lab.height()
        else:
            self.lab.setMinimumHeight(WIDTH_BIGGEST_REGR_BUTTON)
        self.setFixedHeight(WIDTH_BIGGEST_REGR_BUTTON)


class ModelCreationTab(QtWidgets.QWidget):
    """
    This is the overall tab layout. 
    """

    def __init__(self, parent=None):

        QtWidgets.QWidget.__init__(self, parent, objectName = 'tabPage')
        
        self.parent = parent

        # Set up the overall layouts
        overallLayout = QtWidgets.QHBoxLayout()
        overallLayout.setContentsMargins(0,0,0,0)
        overallLayout.setSpacing(0)
        self.overallStackWidget = QtWidgets.QStackedWidget()
        targetSelectLayout = QtWidgets.QGridLayout()
        predictorLayout = QtWidgets.QVBoxLayout()
        optionsLayout = QtWidgets.QVBoxLayout()
        summaryLayout = QtWidgets.QVBoxLayout()
        workflowLayout = QtWidgets.QVBoxLayout()


        self.workflowWidget = EnhancedTabWidget(self, 'above', 'vertical', True, False, True)


        # ===================================================================================================================

        # Layout the Target Selection Widget
        widg = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout()
        self.dataPlot = ModelTabPlots(self, objectName='ModelTabPlot')
        self.dataPlot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.targetSelect = QtWidgets.QComboBox()
        self.datasetList = DatasetList_HTML_Formatted(self, datasetTable = self.parent.datasetTable, addButtons = False )
        self.targetSelect.setModel(self.datasetList.model())
        self.targetSelect.setView(self.datasetList)

        layout.addRow("Forecast Target", self.targetSelect)
        
        self.selectedItemDisplay = DatasetList_HTML_Formatted(self, addButtons = False, objectName = 'ModelTargetList')
        self.selectedItemDisplay.setFixedHeight(99)
        self.selectedItemDisplay.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        
        layout.addWidget(self.selectedItemDisplay)
        
        self.periodStart = QtWidgets.QDateTimeEdit()
        self.periodStart.setDisplayFormat("MMMM d")
        self.periodStart.setCalendarPopup(True)
        self.periodStart.setMinimumDate(QtCore.QDate(QtCore.QDate().currentDate().year(), 1, 1))
        self.periodStart.setMaximumDate(QtCore.QDate(QtCore.QDate().currentDate().year(), 12, 31))
        self.periodEnd = QtWidgets.QDateTimeEdit()
        self.periodEnd.setDisplayFormat("MMMM d")
        self.periodEnd.setCalendarPopup(True)
        self.periodEnd.setMinimumDate(QtCore.QDate(QtCore.QDate().currentDate().year(), 1, 1))
        self.periodEnd.setMaximumDate(QtCore.QDate(QtCore.QDate().currentDate().year(), 12, 31))

        layout.addRow("Target Period (Start)", self.periodStart)
        layout.addRow("Target Period (End)", self.periodEnd)

        # Initialize dates
        self.periodStart.setDate(QtCore.QDate(QtCore.QDate().currentDate().year(), 4, 1))
        self.periodEnd.setDate(QtCore.QDate(QtCore.QDate().currentDate().year(), 7, 31))

        self.methodCombo = QtWidgets.QComboBox()
        itemList = [
            ("Accumulation - CFS to KAF (Accumulate the values over the period and convert to 1000 Acre-Feet)", "accumulation_cfs_kaf"),
            ("Accumulation (Accumulate the values over the period)", "accumulation"),
            ("Average (Average value over the forecast period)","average"),
            ("Minimum (Minimum value over the forecast period)", "min"),
            ("Maximum (Maximum value over the forecast period)", "max"),
            ("First (First value of the forecast period)", "first"),
            ("Custom (Define a custom aggregator function)", "custom")
        ]
        for item in itemList:
            self.methodCombo.addItem(item[0], item[1])
        layout.addRow("Period Calculation", self.methodCombo)

        self.customMethodSpecEdit = QtWidgets.QLineEdit()
        self.customMethodSpecEdit.setPlaceholderText("Define a custom python function here. The variable 'x' represents the periodic dataset [pandas series]. Specify a unit (optional) with '|'. E.g. np.nansum(x)/12 | Feet ")
        layout.addWidget(self.customMethodSpecEdit)
        self.customMethodSpecEdit.hide()
        
        widg.setLayout(layout)
        targetSelectLayout.addWidget(widg, 0, 0, 1, 1)
        targetSelectLayout.addWidget(self.dataPlot, 1, 0, 1, 1)
        widg = QtWidgets.QWidget()
        widg.setLayout(targetSelectLayout)
        self.workflowWidget.addTab(widg, "FORECAST<br>TARGET", "resources/GraphicalResources/icons/target-24px.svg", "#FFFFFF", iconSize=(66,66))

        # ===================================================================================================================

        # Layout the predictor selector widget

        widg = QtWidgets.QWidget()
        self.workflowWidget.addTab(widg, "PREDICTORS", "resources/GraphicalResources/icons/bullseye-24px.svg", "#FFFFFF", iconSize=(66,66))
        
        
        # ====================================================================================================================

        # Layout the Forecast Settings widget
        SA = QtWidgets.QScrollArea()
        SA.setWidgetResizable(True)
        widg = QtWidgets.QWidget()        
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)

        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 24px">How should PyForecast build and evaluate models?</strong>')
        layout.addWidget(label)

        # Forecast Issue Date
        # Model Training Period
        

        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Select options below or choose the default options<strong>')
        layout.addWidget(label)
        self.defButton = QtWidgets.QRadioButton("Choose Defaults")
        self.defButton.setChecked(True)
        self.expertButton = QtWidgets.QRadioButton("I'm an expert! Let me choose")
        bgroup = QtWidgets.QButtonGroup()
        gb = QtWidgets.QGroupBox("")
        bgroup.addButton(self.defButton)
        bgroup.addButton(self.expertButton)
        bgroup.setExclusive(True)
        layout2 = QtWidgets.QVBoxLayout()
        layout2.addWidget(self.defButton)
        layout2.addWidget(self.expertButton)
        gb.setLayout(layout2)
        layout.addWidget(gb)
        

        label  = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Preprocessing Algorithms</strong>')
        layout.addWidget(label)
        layout.addWidget(QtWidgets.QLabel("Select one or more algorithms:"))
        
        numPreProcessors = len(self.parent.preProcessors.keys())
        layout2 = QtWidgets.QGridLayout()
        layout2.setContentsMargins(1,1,1,1)
        for i in range(int(numPreProcessors/3) + 1 if numPreProcessors%3 != 0 else int(numPreProcessors/3)):
            for j in range(3):
                if (i*3)+j < numPreProcessors:
                    prKey = list((self.parent.preProcessors.keys()))[(3*i)+j]
                    regrText = '<strong style="font-size: 13px; color: darkcyan">{0}</strong><br>{1}'.format(self.parent.preProcessors[prKey]['name'], self.parent.preProcessors[prKey]['description'])
                    layout2.addWidget(richTextButton(self, regrText),i,j,1,1)
        layout.addLayout(layout2)

        label  = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Regression Algorithms</strong>')
        layout.addWidget(label)
        layout.addWidget(QtWidgets.QLabel("Select one or more algorithms:"))
        
        numRegressionModels = len(self.parent.regressors.keys())
        layout2 = QtWidgets.QGridLayout()
        layout2.setContentsMargins(1,1,1,1)
        for i in range(int(numRegressionModels/3) + 1 if numRegressionModels%3 != 0 else int(numRegressionModels/3)):
            for j in range(3):
                if (i*3)+j < numRegressionModels:
                    regrKey = list((self.parent.regressors.keys()))[(3*i)+j]
                    regrText = '<strong style="font-size: 13px; color: darkcyan">{0}</strong><br>{1}'.format(self.parent.regressors[regrKey]['name'], self.parent.regressors[regrKey]['description'])
                    layout2.addWidget(richTextButton(self, regrText),i,j,1,1)
        layout.addLayout(layout2)

        label  = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Model Selection Algorithms</strong>')
        layout.addWidget(label)
        layout.addWidget(QtWidgets.QLabel("Select one or more algorithms:"))
        
        numFeatSelectors = len(self.parent.featureSelectors.keys())
        layout2 = QtWidgets.QGridLayout()
        layout2.setContentsMargins(1,1,1,1)
        for i in range(int(numFeatSelectors/3) + 1 if numFeatSelectors%3 != 0 else int(numFeatSelectors/3)):
            for j in range(3):
                if (i*3)+j < numFeatSelectors:
                    regrKey = list((self.parent.featureSelectors.keys()))[(3*i)+j]
                    regrText = '<strong style="font-size: 13px; color: darkcyan">{0}</strong><br>{1}'.format(self.parent.featureSelectors[regrKey]['name'], self.parent.featureSelectors[regrKey]['description'])
                    layout2.addWidget(richTextButton(self, regrText), i, j, 1, 1)
        layout.addLayout(layout2)

        label  = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Model Scoring</strong>')
        layout.addWidget(label)
        layout.addWidget(QtWidgets.QLabel("Select one or more scoring parameters (used to rank models):"))

        numScorers = len(self.parent.scorers['info'].keys())
        layout2 = QtWidgets.QGridLayout()
        layout2.setContentsMargins(1,1,1,1)
        for i in range(int(numScorers/3) + 1 if numScorers%3 != 0 else int(numScorers/3)):
            #layout2 = QtWidgets.QHBoxLayout()
            #layout2.setContentsMargins(1,1,1,1)
            for j in range(3):
                if (i*3)+j < numScorers:
                    nameKey = list((self.parent.scorers['info'].keys()))[(3*i)+j]
                    regrText = '<strong style="font-size: 13px; color:darkcyan">{2}</strong><br>{0}'.format(self.parent.scorers['info'][nameKey]['NAME'], self.parent.scorers['info'][nameKey]['WEBSITE'], self.parent.scorers['info'][nameKey]['HTML'])
                    layout2.addWidget(richTextButton(self, regrText), i, j, 1, 1)
        layout.addLayout(layout2)
        
        #layout2.addWidget(richTextButton(self, '<strong style="color:maroon">Multiple Linear Regression</strong><br>Ordinary Least Squares'))
        #layout2.addWidget(richTextButton(self, '<strong style="color:maroon">Principal Components Regression</strong><br>Ordinary Least Squares'))
        #layout2.addWidget(richTextButton(self, '<strong style="color:maroon">Z-Score Regression</strong><br>Ordinary Least Squares'))
        
        layout.addSpacerItem(QtWidgets.QSpacerItem(100,100,QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        widg.setLayout(layout)
        SA.setWidget(widg)
        self.workflowWidget.addTab(SA, "OPTIONS", "resources/GraphicalResources/icons/tune-24px.svg", "#FFFFFF", iconSize=(66,66))
        # ====================================================================================================================

        # Lay out the summary widget
        widg = QtWidgets.QWidget()
        self.workflowWidget.addTab(widg, "SUMMARY", "resources/GraphicalResources/icons/clipboard-24px.svg", "#FFFFFF", iconSize=(66,66))

        # ====================================================================================================================

        # Layout the results widget
        widg = QtWidgets.QWidget()
        self.workflowWidget.addTab(widg, "RESULTS", "resources/GraphicalResources/icons/run-24px.svg", "#FFFFFF", iconSize=(66,66))


        
        
        overallLayout.addWidget(self.workflowWidget)
        #overallLayout.addWidget(self.overallStackWidget)
        self.setLayout(overallLayout)

    