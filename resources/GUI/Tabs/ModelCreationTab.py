"""
Script Name:    ModelCreationTab.py

Description:    Defines the layout for the Model Creation Tab. Includes all the sub-widgets
                for the stacked widget.
"""

# Import Libraries
from PyQt5 import QtWidgets, QtCore, QtGui

from resources.GUI.CustomWidgets.DatasetList_HTML_Formatted import ListHTMLFormatted, DatasetListHTMLFormatted, DatasetListHTMLFormattedMultiple
from resources.GUI.CustomWidgets.DoubleList import DoubleListMultipleInstance
from resources.GUI.CustomWidgets.htmlDataLists import HTML_LIST
from resources.GUI.CustomWidgets.AggregationOptions import AggregationOptions
from resources.GUI.CustomWidgets.PyQtGraphs import ModelTabTargetPlot, FillExtendTabPlots, ResultsTabPlots, WindowTabPlots
from resources.GUI.CustomWidgets.customTabs import EnhancedTabWidget
from resources.GUI.CustomWidgets.richTextButtons import richTextButton, richTextButtonCheckbox
from resources.GUI.CustomWidgets.SpreadSheet import SpreadSheetViewOperations, SpreadSheetForecastEquations
from resources.GUI.WebMap import webMapView
from resources.modules.ModelCreationTab.modelCreationTabMaster import *


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
        targetSelectLayout = QtWidgets.QVBoxLayout()

        self.workflowWidget = EnhancedTabWidget(self, 'above', 'vertical', True, False, True)

        # ===================================================================================================================
        # Layout the Target Selection Widget

        # Setup the control widgets
        layout = QtWidgets.QGridLayout()

        self.targetSelect = QtWidgets.QComboBox()
        #self.datasetList = HTML_LIST(self.parent, "DataTab_datasetList")#'
        self.datasetList =  DatasetListHTMLFormatted(self, datasetTable = self.parent.datasetTable, addButtons=False)
        self.targetSelect.setModel(self.datasetList.model())
        self.targetSelect.setView(self.datasetList)

        #layout.addRow("Forecast Target", self.targetSelect)
        layout.addWidget(QtWidgets.QLabel("Forecast Target"), 0, 0, 1, 1)
        layout.addWidget(self.targetSelect, 0, 1, 1, 3)
        
        self.selectedItemDisplay = DatasetListHTMLFormatted(self, addButtons=False, objectName='ModelTargetList')
        #self.selectedItemDisplay = HTML_LIST(self.parent, "ModelCreationTab_selectedTarget")
        self.selectedItemDisplay.setFixedHeight(121)
        self.selectedItemDisplay.setStyleSheet("QWidget {border-bottom: 0px solid darkgray}")
        self.selectedItemDisplay.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        
        layout.addWidget(self.selectedItemDisplay, 1, 1, 1, 3)
        
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

        layout.addWidget(QtWidgets.QLabel("Forecast Period (START)"), 2, 0, 1, 1)
        layout.addWidget(self.periodStart, 2, 1, 1, 1)
        layout.addWidget(QtWidgets.QLabel(" to (END)"), 2, 2, 1, 1, QtCore.Qt.AlignHCenter)
        layout.addWidget(self.periodEnd, 2, 3, 1, 1)

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
        #layout.addRow("Period Calculation", self.methodCombo)
        layout.addWidget(QtWidgets.QLabel("Period Calculation"), 4, 0, 1, 1)
        layout.addWidget(self.methodCombo, 4, 1, 1, 3)

        self.customMethodSpecEdit = QtWidgets.QLineEdit()
        self.customMethodSpecEdit.setPlaceholderText("Define a custom python function here. The variable 'x' represents the periodic dataset [pandas series]. Specify a unit (optional) with '|'. E.g. np.nansum(x)/12 | Feet ")
        layout.addWidget(self.customMethodSpecEdit, 5, 1, 1, 3)
        self.customMethodSpecEdit.hide()

        # Create the training and excluded years
        onlyInt = QtGui.QIntValidator()
        layout.addWidget(QtWidgets.QLabel("Model Training Period (START)"), 6, 0, 1, 1)
        self.targetPeriodStartYear = QtWidgets.QLineEdit()
        self.targetPeriodStartYear.setValidator(onlyInt)
        layout.addWidget(self.targetPeriodStartYear, 6, 1, 1, 1)
        layout.addWidget(QtWidgets.QLabel(" to (END)"), 6, 2, 1, 1, QtCore.Qt.AlignHCenter)
        self.targetPeriodEndYear = QtWidgets.QLineEdit()
        self.targetPeriodEndYear.setValidator(onlyInt)
        layout.addWidget(self.targetPeriodEndYear, 6, 3, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Excluded Year(s)"), 7, 0, 1, 1)
        self.targetPeriodExcludedYears = QtWidgets.QLineEdit()
        self.targetPeriodExcludedYears.setPlaceholderText("Comma separated years to exclude. Ex: 1980,2010,...")
        layout.addWidget(self.targetPeriodExcludedYears, 7, 1, 1, 3)

        # Create the apply button
        self.predictandApplyButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Apply</strong>')
        self.predictandApplyButton.setMaximumSize(125, 50)
        self.predictandApplyButton.setMinimumSize(100, 35)
        # self.predictandApplyButton.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        layout.addWidget(self.predictandApplyButton, 8, 3, 1, 1, QtCore.Qt.AlignRight)

        # Configure the layout spacing
        layout.setVerticalSpacing(15)
        layout.setHorizontalSpacing(5)
        layout.setContentsMargins(10, 10, 10, 10)

        # Create a group box for appearance consistency
        groupBox = QtWidgets.QGroupBox()
        groupBox.setLayout(layout)
        groupBox.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)

        # Create the data plot
        self.dataPlot = ModelTabTargetPlot(self, objectName='ModelTabPlot')
        self.dataPlot.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)

        # Create the description text for the page
        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 24px">Which variable should PyForecast forecast?</strong>')

        # Add the widgets into the main layout
        targetSelectLayout.addWidget(label)
        targetSelectLayout.addItem(QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        targetSelectLayout.addWidget(groupBox)
        targetSelectLayout.addItem(QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        targetSelectLayout.addWidget(self.dataPlot)
        targetSelectLayout.setContentsMargins(15, 15, 15, 15)

        targetSelectLayout.setSpacing(0)

        # Promote the main layout to a widget and add to the main panel
        widg = QtWidgets.QWidget()
        widg.setLayout(targetSelectLayout)
        self.workflowWidget.addTab(widg, "FORECAST<br>TARGET", "resources/GraphicalResources/icons/target-24px.svg", "#FFFFFF", iconSize=(66,66))

        # ===================================================================================================================
        ### Layout the predictor selector widget ###
        # Create the icon on the left side of the screen
        predictorWidget = QtWidgets.QWidget()

        # Setup the initial items
        predictorScrollableArea = QtWidgets.QScrollArea()
        predictorScrollableArea.setWidgetResizable(True)
        predictorLayout = QtWidgets.QVBoxLayout()
        predictorLayout.setContentsMargins(15, 15, 15, 15)

        # Create the description text for the page
        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 24px">Which variables should PyForecast use as predictors?</strong>')
        predictorLayout.addWidget(label)

        # Create the initial dialog for the type of analysis
        labelMode = QtWidgets.QLabel()
        labelMode.setTextFormat(QtCore.Qt.RichText)
        labelMode.setText('<strong style="font-size: 12px">Select workflow configuration:</strong>')
        labelMode.setFixedWidth(250)

        self.defaultPredictorButton = QtWidgets.QRadioButton('Default')
        self.defaultPredictorButton.setStyleSheet('QRadioButton{font: 8pt sans-serif;} QRadioButton::indicator { width: 12px; height: 12px;};')
        self.defaultPredictorButton.setChecked(True)
        self.defaultPredictorButton.setFixedWidth(100)
        self.expertPredictorButton = QtWidgets.QRadioButton('Expert')
        self.expertPredictorButton.setStyleSheet('QRadioButton{font: 8pt; sans-serif} QRadioButton::indicator { width: 12px; height: 12px;};')
        self.expertPredictorButton.setFixedWidth(100)

        bgroup = QtWidgets.QButtonGroup()
        bgroup.addButton(self.defaultPredictorButton)
        bgroup.addButton(self.expertPredictorButton)
        bgroup.setExclusive(True)

        predictorModeLayout = QtWidgets.QHBoxLayout()
        predictorModeLayout.addWidget(labelMode)
        predictorModeLayout.addWidget(self.defaultPredictorButton)
        predictorModeLayout.addWidget(self.expertPredictorButton)
        predictorModeLayout.setAlignment(QtCore.Qt.AlignLeft)

        gb = QtWidgets.QGroupBox("")
        gb.setLayout(predictorModeLayout)
        predictorLayout.addSpacerItem(QtWidgets.QSpacerItem(0, 5, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        predictorLayout.addWidget(gb)

        # Space between the setup options and the tabs
        predictorLayout.addSpacerItem(QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        # Create the layout for the simple analysis
        self.layoutPredictorSimpleAnalysis = QtWidgets.QScrollArea()
        self.layoutPredictorSimpleAnalysis.setContentsMargins(0, 0, 0, 0)
        self.layoutPredictorSimpleAnalysis.setWidgetResizable(True)
        self.layoutPredictorSimpleAnalysis.setFrameShape(QtWidgets.QFrame.NoFrame)

        # Create the layout object for the expert analysis
        self.layoutPredictorExpertAnalysis = QtWidgets.QVBoxLayout()
        self.layoutPredictorExpertAnalysis.setContentsMargins(0, 0, 0, 0)

        ### Create the simple analysis tab ###
        # Fill the remaining area with the layout options
        self._createSimplePredictorLayout(self.layoutPredictorSimpleAnalysis)

        ### Create the layout data tab ###
        ## Create the initial scrollable area and layout ##
        # Create the scrollable area and set it to resizeable
        layoutDataSA = QtWidgets.QScrollArea()
        layoutDataSA.setWidgetResizable(True)

        # Create the initial box layout
        layoutData = QtWidgets.QHBoxLayout()


        ## Add the webmap object to the current layout ##
        self.webMapView = webMapView.webMapView()
        layoutData.addWidget(self.webMapView)

        ## Setup the DoubleList object ##
        # Create the doublelist
        self.layoutDataDoubleList = DoubleListMultipleInstance(self.parent.datasetTable,
                                                               '<strong style="font-size: 18px">Available Datasets<strong>',
                                                               '<strong style="font-size: 18px">Selected Datasets<strong>',
                                                               operations_dataframe=self.parent.datasetOperationsTable)

        # Adjust the spacing on the doublelist
        self.layoutDataDoubleList.setContentsMargins(0, 0, 0, 0)
        self.layoutDataDoubleList.layout().setContentsMargins(10, 0, 0, 0)

        self.layoutDataDoubleList.listOutput.setContentsMargins(0, 0, 0, 0)
        self.layoutDataDoubleList.layoutOutput.setContentsMargins(0, 0, 0, 0)

        self.layoutDataDoubleList.listInput.setContentsMargins(0, 0, 0, 0)
        self.layoutDataDoubleList.layoutInput.setContentsMargins(0, 0, 0, 0)


        # Connect the DoubleList with the dataset hmtl list to keep everything in sync. This will automatically
        # populate the DoubleList entries
        self.datasetList.updateSignalToExternal.connect(self.layoutDataDoubleList.update)

        # Connect the doublelists together. This will keep the selection in sync between the simple and expert modes
        self.layoutDataDoubleList.updatedLinkedList.connect(self.layoutSimpleDoubleList.updateLinkedDoubleLists)
        self.layoutSimpleDoubleList.updatedLinkedList.connect(self.layoutDataDoubleList.updateLinkedDoubleLists)

        # Link the expert doublelist to the model operations table. Since the double lists are linked together, linking
        # only one is sufficient to ensure the table is always up-to-date
        self.layoutDataDoubleList.updatedOutputList.connect(self.layoutDataDoubleList.updateLinkedOperationsTables)

        # todo: Update the positions on the map

        # Add the widget to the layout
        layoutData.addWidget(self.layoutDataDoubleList)

        ## Finalize the tab format ##
        # Wrap the layout as a widget to make it compatible with the SA layout
        layoutDataSA.setLayout(layoutData)


        ### Create the layout fill tab ###
        # Create the scrollable area
        layoutFillSA = QtWidgets.QScrollArea()
        layoutFillSA.setWidgetResizable(True)

        # Fill the remaining area with the layout options
        self._createDataFillLayout(layoutFillSA)


        ### Create the layout extend tab ###
        # Create the scrollable area
        layoutExtendSA = QtWidgets.QScrollArea()
        layoutExtendSA.setWidgetResizable(True)

        # Fill the remaining area with the layout options
        self._createDataExtendLayout(layoutExtendSA)


        ### Create the layout window tab ###
        # Create the scrollable area
        layoutWindowSA = QtWidgets.QScrollArea()
        layoutWindowSA.setWidgetResizable(True)

        # Fill the remaining area with the layout options
        self._createDataWindowLayout(layoutWindowSA)


        ### Add the subtabs into the tab widget ###
        tabWidget = QtWidgets.QTabWidget()
        tabWidget.addTab(layoutDataSA, 'Data')
        tabWidget.addTab(layoutFillSA, 'Fill')
        tabWidget.addTab(layoutExtendSA, 'Extend')
        tabWidget.addTab(layoutWindowSA, 'Window')

        # The SA can be added directly to the stack, but will result in a window flash at program start. Wrapping in a
        # secondary layout with the visibility cll from modelCreationTabMaster prevents the startup issue.
        self.layoutPredictorSimpleAnalysis.setVisible(False)
        simplePredictorLayout = QtWidgets.QVBoxLayout()
        simplePredictorLayout.setContentsMargins(0, 0, 0, 0)
        simplePredictorLayout.addWidget(self.layoutPredictorSimpleAnalysis)
        simplePredictorWidget = QtWidgets.QWidget()
        simplePredictorWidget.setLayout(simplePredictorLayout)
        simplePredictorWidget.setVisible(False)

        # Add to the expert layout
        self.layoutPredictorExpertAnalysis.addWidget(tabWidget)
        self.expertPredictorWidget = QtWidgets.QWidget()
        self.expertPredictorWidget.setLayout(self.layoutPredictorExpertAnalysis)
        self.expertPredictorWidget.setVisible(False)

        # Create the stacked widget to handle to toggle between simple and expert analyses
        self.stackedPredictorWidget = QtWidgets.QStackedLayout()
        self.stackedPredictorWidget.addWidget(simplePredictorWidget)
        self.stackedPredictorWidget.addWidget(self.expertPredictorWidget)

        self.defaultPredictorButton.setChecked(True)
        self.defaultPredictorButton.clicked.connect(self.setPredictorDefaultStack)
        self.expertPredictorButton.clicked.connect(self.setPredictorExpertStack)
        
        stackedModePredictorWidget = QtWidgets.QWidget()
        stackedModePredictorWidget.setLayout(self.stackedPredictorWidget)

        predictorLayout.addWidget(stackedModePredictorWidget)
        predictorWidget.setLayout(predictorLayout)
        predictorScrollableArea.setWidget(predictorWidget)
        self.workflowWidget.addTab(predictorScrollableArea, "PREDICTORS", "resources/GraphicalResources/icons/bullseye-24px.svg",
                                   "#FFFFFF", iconSize=(66, 66))

        # ====================================================================================================================
        # Layout the Forecast Settings widget
        # Create the scrollable area
        SA = QtWidgets.QScrollArea()
        SA.setWidgetResizable(True)
        SA.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)

        # Construct the layout object
        optionsLayout = self._createOptionsTabLayout()
        # optionsLayout.setAlignment(QtCore.Qt.AlignTop)

        # Set the layout into the widget
        widg = QtWidgets.QWidget()
        widg.setLayout(optionsLayout)
        widg.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)

        # Add the widget to the scrollable area
        SA.setWidget(widg)
        self.workflowWidget.addTab(SA, "OPTIONS", "resources/GraphicalResources/icons/tune-24px.svg", "#FFFFFF", iconSize=(66,66))


        # ====================================================================================================================
        ### Create the run summary scrollabe area ###
        # Create the scrollable area
        summarySA = QtWidgets.QScrollArea()
        summarySA.setWidgetResizable(True)
        summarySA.setContentsMargins(0, 0, 0, 0)

        # Lay out the summary widget
        summaryWidget = QtWidgets.QWidget()

        # Create the horizontal layout widget
        summaryLayout = QtWidgets.QVBoxLayout()
        summaryLayout.setContentsMargins(15, 15, 15, 15)

        ### Setup the layout ###
        # Create the layout by calling to the setup function, returning a layout object
        self._createSummaryTabLayout(summaryLayout)

        ### Add the layout to the main window ###
        # Wrap the summary layout in the widget
        summaryWidget.setLayout(summaryLayout)

        # Wrap the scrollable area in a widget
        summarySA.setWidget(summaryWidget)

        self.workflowWidget.addTab(summarySA, "RUN", "resources/GraphicalResources/icons/run-24px.svg", "#FFFFFF", iconSize=(66,66))

        # ====================================================================================================================
        ### Create the results scrollabe area ###
        # Create the scrollable area
        resultsSA = QtWidgets.QScrollArea()
        resultsSA.setWidgetResizable(True)
        resultsSA.setContentsMargins(0, 0, 0, 0)

        # Setup the layout
        self._createResultsTabLayout(resultsSA)

        # Layout the results widget
        self.workflowWidget.addTab(resultsSA, "RESULTS", "resources/GraphicalResources/icons/clipboard-24px.svg", "#FFFFFF", iconSize=(66,66))
        
        overallLayout.addWidget(self.workflowWidget)
        #overallLayout.addWidget(self.overallStackWidget)
        self.setLayout(overallLayout)

        # ====================================================================================================================



    def _createSimplePredictorLayout(self, predictorLayoutSimple):
        """
        Lays out the full simple predictor tab

        Parameters
        ----------
        predictorLayoutSimple: scrollable area
            The area into which all layout items are placed

        Returns
        -------
        None.

        """


        ## Create the DoubleList selector object ##
        # Create the output list
        self.layoutSimpleDoubleList = DoubleListMultipleInstance(self.parent.datasetTable,
                                                                 '<strong style="font-size: 18px">Available Datasets<strong>',
                                                                 '<strong style="font-size: 18px">Selected Datasets<strong>',
                                                                 outputDefaultColor=QtCore.Qt.darkGray)
        self.layoutSimpleDoubleList.setContentsMargins(0, 0, 0, 0)
        self.layoutSimpleDoubleList.layout().setContentsMargins(0, 0, 0, 0)

        self.layoutSimpleDoubleList.listInput.setContentsMargins(0, 0, 0, 0)
        self.layoutSimpleDoubleList.layoutInput.setContentsMargins(0, 0, 0, 0)
        self.layoutSimpleDoubleList.listOutput.setContentsMargins(0, 0, 0, 0)
        self.layoutSimpleDoubleList.layoutOutput.setContentsMargins(0, 0, 0, 0)

        # Update the output colors to show that the list will be active
        self.layoutSimpleDoubleList.listOutput.itemColors = []

        # Connect the DoubleList with the dataset hmtl list to keep everything in sync. This will automatically
        # populate the DoubleList entries
        self.datasetList.updateSignalToExternal.connect(self.layoutSimpleDoubleList.update)

        ## Define the data plots
        plotLayout = QtWidgets.QVBoxLayout()
        plotLayout.setContentsMargins(0, 10, 0, 0)

        # resampling plot
        self.predictorPlot = ModelTabTargetPlot(self, objectName='PredictorPlot')#ResultsTabPlots(self, xLabel='Date', yLabel='Value')
        self.predictorPlot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # correlation plot of resampled predictor to target
        self.predictorCorrelationPlot = ResultsTabPlots(self, xLabel='Resampled Predictor', yLabel='Resampled Target', title='Resampled Data Correlation')
        self.predictorCorrelationPlot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.predictorCorrelationPlot.hide()

        # toggle button to switch plots
        self.predictorPlotButton = richTextButton('<strong style="font-size: 12px; color:darkcyan">Show resampled data correlation to target</strong>')
        self.predictorPlotButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        # add everything to layout
        plotLayout.addWidget(self.predictorPlot)
        plotLayout.addWidget(self.predictorCorrelationPlot)
        plotLayout.addWidget(self.predictorPlotButton)
        self.predictorPlotWidget = QtWidgets.QWidget()
        self.predictorPlotWidget.setLayout(plotLayout)

        # Create the left side widget
        leftLayout = QtWidgets.QVBoxLayout()
        leftLayout.setContentsMargins(0, 0, 0, 0)
        leftLayout.addWidget(self.layoutSimpleDoubleList)
        leftLayout.addWidget(self.predictorPlotWidget)
        leftLayoutWidget = QtWidgets.QWidget()
        leftLayoutWidget.setLayout(leftLayout)
        self.predictorPlotWidget.hide()

        ## Create the objects on the right side ##
        configurationLabel = QtWidgets.QLabel('<strong style="font-size: 18px">Dataset Configuration<strong>')
        configurationLabel.setContentsMargins(0, 0, 0, 0)

        # Aggregation options widget
        self.layoutAggregationOptions = AggregationOptions(False, orientation='vertical')

        # Simple fill
        self.layoutSimpleFill = richTextButtonCheckbox('<strong style="font-size: 13px; color: darkcyan">{0}</strong><br>{1}'.format(
                'Fill data', 'Automatically fill the selected time series using default properties'))
        self.layoutSimpleFill.setChecked(False)
        self.layoutSimpleFill.setDisabled(True)
        self.layoutSimpleFill.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        # Simple extend
        self.layoutSimpleExtend = richTextButtonCheckbox('<strong style="font-size: 13px; color: darkcyan">{0}</strong><br>{1}'.format(
                                                                'Extend data',
                                                                'Automatically extend the selected time series using default properties\n'))
        self.layoutSimpleExtend.setChecked(False)
        self.layoutSimpleExtend.setDisabled(True)
        self.layoutSimpleExtend.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        ### Create buttons to apply predictor operations ###
        # Create the show plots button
        self.layoutSimplePlotButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Show Plot</strong>')
        self.layoutSimplePlotButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        # Create the clear button
        self.layoutSimpleClearButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Clear</strong>')
        self.layoutSimpleClearButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        # Create the apply button
        self.layoutSimpleApplyButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Apply</strong>')
        self.layoutSimpleApplyButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        # Create the layout, wrap it, and add to the right layout
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.setContentsMargins(0, 0, 0, 0)
        buttonLayout.addWidget(self.layoutSimplePlotButton)
        buttonLayout.addWidget(self.layoutSimpleClearButton)
        buttonLayout.addWidget(self.layoutSimpleApplyButton)
        buttonLayout.setAlignment(QtCore.Qt.AlignRight)
        buttonLayoutWidget = QtWidgets.QWidget()
        buttonLayoutWidget.setLayout(buttonLayout)

        # Create the right side options layout
        layoutSimpleOptions = QtWidgets.QVBoxLayout()
        layoutSimpleOptions.setContentsMargins(0, 0, 0, 0)
        layoutSimpleOptions.setAlignment(QtCore.Qt.AlignTop)
        layoutSimpleOptions.addWidget(configurationLabel)
        layoutSimpleOptions.addWidget(self.layoutAggregationOptions)
        optionalLabel = QtWidgets.QLabel('<strong style="font-size: 18px">Timeseries Configuration<strong>')
        optionalLabel.setContentsMargins(0, 0, 0, 0)
        layoutSimpleOptions.addWidget(optionalLabel)
        layoutSimpleOptions.addWidget(self.layoutSimpleFill, alignment=QtCore.Qt.AlignTop)
        layoutSimpleOptions.addWidget(self.layoutSimpleExtend, alignment=QtCore.Qt.AlignTop)
        layoutSimpleOptions.addSpacerItem(QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        layoutSimpleOptions.addWidget(buttonLayoutWidget)

        # Wrap the right side layout in another widget
        layoutSimpleOptionsWidget = QtWidgets.QWidget()
        layoutSimpleOptionsWidget.setLayout(layoutSimpleOptions)

        ## Add the widgets into the layout ##
        # Add the items into the horizontal spacer
        layoutSimple = QtWidgets.QHBoxLayout()
        layoutSimple.setContentsMargins(0, 0, 0, 0)
        layoutSimple.addWidget(leftLayoutWidget, 2)
        layoutSimple.addSpacerItem(QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        # Add the right side to the simple layout
        layoutSimple.addWidget(layoutSimpleOptionsWidget, 1)
        predictorLayoutSimple.setLayout(layoutSimple)


    def _createDataFillLayout(self, layoutFillSA):
        """
        Lays out the fill subtab in the expert predictor mode

        Parameters
        ----------
        layoutFillSA: scrollable area
            The area into which all layout items are placed

        Returns
        -------
        None.

        """

        ## Create the selector list ##
        # Create a vertical layout
        layoutFillLeftLayout = QtWidgets.QVBoxLayout()

        # Create and add the list title
        layoutFillLeftLayout.addWidget(QtWidgets.QLabel('<strong style="font-size: 18px">Selected Data<strong>'))

        # Add the list
        self.fillList = DatasetListHTMLFormattedMultiple(inputDataset=self.layoutDataDoubleList.listOutput.datasetTable)
        self.layoutDataDoubleList.listOutput.updateSignalToExternal.connect(self.fillList.refreshDatasetListFromExtenal)
        layoutFillLeftLayout.addWidget(self.fillList)

        ## Create the right panel ##
        # Create the vertical layout
        layoutFillRightLayout = QtWidgets.QVBoxLayout()

        # Set the options available for filling the data
        fillOptions = ['None', 'Nearest', 'Linear', 'Quadratic', 'Cubic', 'Spline', 'Polynomial']

        # Create and add a dropdown selector with the available options
        layoutFillRightLayout.addWidget(QtWidgets.QLabel('<strong style="font-size: 18px">Fill Method<strong>'))

        self.layoutFillMethodSelector = QtWidgets.QComboBox()
        self.layoutFillMethodSelector.addItems(fillOptions)
        layoutFillRightLayout.addWidget(self.layoutFillMethodSelector)

        # Create a line to delineate the selector from the selector options
        lineA = QtWidgets.QFrame()
        lineA.setFrameShape(QtWidgets.QFrame.HLine)
        layoutFillRightLayout.addWidget(lineA)

        # Create the fill limit label
        self.layoutFillGapLimitLabel = QtWidgets.QLabel('Maximum Filled Gap')
        self.layoutFillGapLimitLabel.setVisible(False)
        self.layoutFillGapLimitLabel.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        # Create the fill limit widget
        self.layoutFillGapLimit = QtWidgets.QLineEdit()
        self.layoutFillGapLimit.setPlaceholderText('30')
        self.layoutFillGapLimit.setVisible(False)
        self.layoutFillGapLimit.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)

        # Create the fill order widget label
        self.layoutFillOrderLabel = QtWidgets.QLabel('Fill order')
        self.layoutFillOrderLabel.setVisible(False)
        self.layoutFillOrderLabel.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        # Create the fill order widget
        self.layoutFillOrder = QtWidgets.QComboBox()
        self.layoutFillOrder.addItems([str(x) for x in range(1, 11, 1)])
        self.layoutFillOrder.setVisible(False)
        self.layoutFillOrder.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)

        # Create the layout for the fill limit
        filledGapLayout = QtWidgets.QHBoxLayout()
        filledGapLayout.setAlignment(QtCore.Qt.AlignTop)
        filledGapLayout.addWidget(self.layoutFillGapLimitLabel)
        filledGapLayout.addWidget(self.layoutFillGapLimit)
        filledGapLayout.setContentsMargins(0, 0, 0, 0)

        # Create the layout for the fill order
        filledOrderLayout = QtWidgets.QHBoxLayout()
        filledOrderLayout.setAlignment(QtCore.Qt.AlignTop)
        filledOrderLayout.addWidget(self.layoutFillOrderLabel)
        filledOrderLayout.addWidget(self.layoutFillOrder)
        filledOrderLayout.setContentsMargins(0, 0, 0, 0)

        # Crate the widgets to wrap the conserved buttons
        filledGapLayoutWidget = QtWidgets.QWidget()
        filledGapLayoutWidget.setLayout(filledGapLayout)

        filledOrderLayoutWidget = QtWidgets.QWidget()
        filledOrderLayoutWidget.setLayout(filledOrderLayout)

        # Create a layout, widget for the conserved widgets and add to the right layout
        filledTopOptionsLayout = QtWidgets.QHBoxLayout()
        filledTopOptionsLayout.addWidget(filledGapLayoutWidget)
        filledTopOptionsLayout.addWidget(filledOrderLayoutWidget)
        filledTopOptionsLayout.setContentsMargins(0, 0, 0, 0)

        filledTopOptionsLayoutWidget = QtWidgets.QWidget()
        filledTopOptionsLayoutWidget.setLayout(filledTopOptionsLayout)
        layoutFillRightLayout.addWidget(filledTopOptionsLayoutWidget)

        # Adjust the layout of the widgets
        layoutFillRightLayout.setAlignment(QtCore.Qt.AlignTop)

        ### Create the nearest page ###
        nearestLayout = QtWidgets.QGridLayout()
        nearestLayout.setContentsMargins(0, 0, 0, 0)

        ### Create the linear page ###
        linearLayout = QtWidgets.QGridLayout()
        linearLayout.setContentsMargins(0, 0, 0, 0)

        ### Create the quadratic page ###
        quadradicLayout = QtWidgets.QGridLayout()
        quadradicLayout.setContentsMargins(0, 0, 0, 0)

        ### Create the cubic page ###
        cubicLayout = QtWidgets.QGridLayout()
        cubicLayout.setContentsMargins(0, 0, 0, 0)

        ### Create the polynomial page ###
        polyLayout = QtWidgets.QGridLayout()
        polyLayout.setContentsMargins(0, 0, 0, 0)

        ### Create the stacked layout ###
        # Initialize the layout
        self.stackedFillLayout = QtWidgets.QStackedLayout()

        # Wrap it in a widget and set visibility to false. If this is not done, a small, annoying popup window will
        # be opened separate from the main window
        stackedWidget = QtWidgets.QWidget()
        stackedWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        stackedWidget.setLayout(self.stackedFillLayout)
        stackedWidget.setVisible(False)

        # Add each of the interpolation types to it
        nearestWidget = QtWidgets.QWidget()
        nearestWidget.setLayout(nearestLayout)
        nearestWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.stackedFillLayout.addWidget(nearestWidget)

        linearWidget = QtWidgets.QWidget()
        linearWidget.setLayout(linearLayout)
        linearWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.stackedFillLayout.addWidget(linearWidget)

        quadradicWidget = QtWidgets.QWidget()
        quadradicWidget.setLayout(quadradicLayout)
        quadradicWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.stackedFillLayout.addWidget(quadradicWidget)

        cubicWidget = QtWidgets.QWidget()
        cubicWidget.setLayout(cubicLayout)
        cubicWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.stackedFillLayout.addWidget(cubicWidget)

        splineWidget = QtWidgets.QWidget()
        splineWidget.setLayout(polyLayout)
        splineWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.stackedFillLayout.addWidget(splineWidget)

        # Add the stacked layout to the main layout
        layoutFillRightLayout.addWidget(stackedWidget)
        stackedWidget.setVisible(False)

        ### Create the plot that shows the result of the selection ###
        # Create the plot
        self.layoutFillPlot = FillExtendTabPlots(self)
        self.layoutFillPlot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Add it into the layout
        layoutFillRightLayout.addWidget(self.layoutFillPlot)

        ### Create clear and apply buttons to apply operations ###
        # Create the clear button
        self.layoutFillClearButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Clear</strong>')
        self.layoutFillClearButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        # Create the apply button
        self.layoutFillApplyButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Apply</strong>')
        self.layoutFillApplyButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        # Create the layout, wrap it, and add to the right layout
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(self.layoutFillClearButton)
        buttonLayout.addWidget(self.layoutFillApplyButton)
        buttonLayout.setAlignment(QtCore.Qt.AlignRight)

        buttonLayoutWidget = QtWidgets.QWidget()
        buttonLayoutWidget.setLayout(buttonLayout)
        layoutFillRightLayout.addWidget(buttonLayoutWidget)

        ### Create the full layout ###
        layoutFill = QtWidgets.QHBoxLayout()

        leftWidget = QtWidgets.QWidget()
        leftWidget.setLayout(layoutFillLeftLayout)
        layoutFill.addWidget(leftWidget, 1)

        rightWidget = QtWidgets.QWidget()
        rightWidget.setLayout(layoutFillRightLayout)
        layoutFill.addWidget(rightWidget, 2)

        layoutFillSA.setLayout(layoutFill)

    def _createDataExtendLayout(self, layoutExtendSA):
        """
        Lays out the extend subtab in the expert predictor mode

        Parameters
        ----------
        layoutExtendSA: scrollable area
            The area into which all layout items are placed

        Returns
        -------
        None.

        """

        ## Create the selector list ##
        # Create a vertical layout
        layoutExtendLeftLayout = QtWidgets.QVBoxLayout()

        # Create and add the list title
        layoutExtendLeftLayout.addWidget(QtWidgets.QLabel('<strong style="font-size: 18px">Selected Data<strong>'))

        # Connect and add the list
        self.extendList = DatasetListHTMLFormattedMultiple(inputDataset=self.layoutDataDoubleList.listOutput.datasetTable)
        self.layoutDataDoubleList.listOutput.updateSignalToExternal.connect(self.extendList.refreshDatasetListFromExtenal)
        layoutExtendLeftLayout.addWidget(self.extendList)

        ## Create the right panel ##
        # Create the vertical layout
        layoutExtendRightLayout = QtWidgets.QVBoxLayout()

        # Set the options available for filling the data
        extendOptions = ['None', 'Linear', 'Fourier']

        # Create and add a dropdown selector with the available options
        layoutExtendRightLayout.addWidget(QtWidgets.QLabel('<strong style="font-size: 18px">Extend Method<strong>'))

        self.layoutExtendMethodSelector = QtWidgets.QComboBox()
        self.layoutExtendMethodSelector.addItems(extendOptions)
        layoutExtendRightLayout.addWidget(self.layoutExtendMethodSelector)

        # Create a line to delineate the selector from the selector options
        lineA = QtWidgets.QFrame()
        lineA.setFrameShape(QtWidgets.QFrame.HLine)
        layoutExtendRightLayout.addWidget(lineA)

        # Adjust the layout of the widgets
        layoutExtendRightLayout.setAlignment(QtCore.Qt.AlignTop)

        ### Create the none page ###
        noneLayout = QtWidgets.QVBoxLayout()
        noneLayout.setContentsMargins(0, 0, 0, 6)

        ### Create the linear page ###
        ## Create the main vertical layout ##
        linearLayout = QtWidgets.QVBoxLayout()
        linearLayout.setContentsMargins(0, 0, 0, 6)

        ## Create the horizontal layout for the first row ##
        linearHorizontalLayout = QtWidgets.QHBoxLayout()
        linearHorizontalLayout.setContentsMargins(0, 0, 0, 0)

        # Create the fill limit label
        self.layoutExtendLinearDurationLabel = QtWidgets.QLabel('Extension Duration')
        self.layoutExtendLinearDurationLabel.setVisible(False)

        # Create the fill limit widget
        self.layoutExtendLinearDurationLimit = QtWidgets.QLineEdit()
        self.layoutExtendLinearDurationLimit.setPlaceholderText('30')
        self.layoutExtendLinearDurationLimit.setVisible(False)

        # Add both widgets to the horizontal layout
        linearHorizontalLayout.addWidget(self.layoutExtendLinearDurationLabel)
        linearHorizontalLayout.addWidget(self.layoutExtendLinearDurationLimit)

        ## Add the horizontal layout into the linear vertical layout ##
        # Wrap the layout in a widget
        horizontalWidget = QtWidgets.QWidget()
        horizontalWidget.setLayout(linearHorizontalLayout)

        # Add the widget into the vertical layout
        linearLayout.addWidget(horizontalWidget)

        ### Create the fourier page ###
        ## Create the main vertical layout ##
        fourierLayout = QtWidgets.QVBoxLayout()
        fourierLayout.setContentsMargins(0, 0, 0, 6)

        ## Create the horizontal layout for the first row ##
        fourierHorizontalLayout = QtWidgets.QHBoxLayout()
        fourierHorizontalLayout.setContentsMargins(0, 0, 0, 0)

        # Create the fill limit label
        self.layoutExtendFourierDurationLabel = QtWidgets.QLabel('Extension Duration')
        self.layoutExtendFourierDurationLabel.setVisible(False)

        # Create the fill limit widget
        self.layoutExtendFourierDurationLimit = QtWidgets.QLineEdit()
        self.layoutExtendFourierDurationLimit.setPlaceholderText('30')
        self.layoutExtendFourierDurationLimit.setVisible(False)

        # Create the filter label
        self.layoutExtendFourierFilterLabel = QtWidgets.QLabel('Filter Duration')
        self.layoutExtendFourierFilterLabel.setVisible(False)

        # Create the fill filter widget
        self.layoutExtendFourierFilter = QtWidgets.QComboBox()
        self.layoutExtendFourierFilter.addItems(['Day', 'Week', 'Month', 'Year'])
        self.layoutExtendFourierFilter.setVisible(False)

        # Add the widgets into the horizontal layout
        fourierHorizontalLayout.addWidget(self.layoutExtendFourierDurationLabel)
        fourierHorizontalLayout.addWidget(self.layoutExtendFourierDurationLimit)
        fourierHorizontalLayout.addWidget(self.layoutExtendFourierFilterLabel)
        fourierHorizontalLayout.addWidget(self.layoutExtendFourierFilter)

        ## Add the horizontal layout into the linear vertical layout ##
        # Wrap the layout in a widget
        horizontalWidget = QtWidgets.QWidget()
        horizontalWidget.setLayout(fourierHorizontalLayout)

        # Add the widget into the vertical layout
        fourierLayout.addWidget(horizontalWidget)

        ### Create the stacked layout ###
        # Initialize the layout
        self.stackedExtendLayout = QtWidgets.QStackedLayout()
        # self.stackedExtendLayout.setContentsMargins(0, 0, 0, 4)

        # Wrap it in a widget and set visibility to false. If this is not done, a small, annoying popup window will
        # be opened separate from the main window
        stackedWidget = QtWidgets.QWidget()
        stackedWidget.setLayout(self.stackedExtendLayout)
        stackedWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)

        # Add each of the interpolation types to it, specifying how to scale with the screen
        noneWidget = QtWidgets.QWidget()
        noneWidget.setLayout(noneLayout)
        noneWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.stackedExtendLayout.addWidget(noneWidget)

        linearWidget = QtWidgets.QWidget()
        linearWidget.setLayout(linearLayout)
        linearWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.stackedExtendLayout.addWidget(linearWidget)

        fourierWidget = QtWidgets.QWidget()
        fourierWidget.setLayout(fourierLayout)
        fourierWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.stackedExtendLayout.addWidget(fourierWidget)

        # Add the stacked layout to the main layout
        layoutExtendRightLayout.addWidget(stackedWidget)

        ### Create the plot that shows the result of the selection ###
        # Create the plot
        self.layoutExtendPlot = FillExtendTabPlots()
        self.layoutExtendPlot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Add it into the layout
        layoutExtendRightLayout.addWidget(self.layoutExtendPlot)

        ### Create clear and apply buttons to apply operations ###
        # Create the clear button
        self.layoutExtendClearButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Clear</strong>')
        self.layoutExtendClearButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        # Create the apply button
        self.layoutExtendApplyButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Apply</strong>')
        self.layoutExtendApplyButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        # Create the layout, wrap it, and add to the right layout
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(self.layoutExtendClearButton)
        buttonLayout.addWidget(self.layoutExtendApplyButton)
        buttonLayout.setAlignment(QtCore.Qt.AlignRight)

        buttonLayoutWidget = QtWidgets.QWidget()
        buttonLayoutWidget.setLayout(buttonLayout)
        layoutExtendRightLayout.addWidget(buttonLayoutWidget)

        ## Create the full layout ##
        # Create the horizontal layout
        layoutExtend = QtWidgets.QHBoxLayout()

        # Wrap the left layout in a widget and add to the layout
        leftWidget = QtWidgets.QWidget()
        leftWidget.setLayout(layoutExtendLeftLayout)
        layoutExtend.addWidget(leftWidget, 1)

        # Wrap the right layout in a widget and add to the layout
        rightWidget = QtWidgets.QWidget()
        rightWidget.setLayout(layoutExtendRightLayout)
        layoutExtend.addWidget(rightWidget, 2)

        # Add the layout to the extend scrollable area
        layoutExtendSA.setLayout(layoutExtend)

    def _createDataWindowLayout(self, layoutWindowSA):
        """
        Lays out the windowing subtab in the expert predictor mode

        Parameters
        ----------
        layoutWindowSA: scrollable area
            The area into which all layout items are placed

        Returns
        -------
        None.

        """

        ## Create the selector list ##
        # Create a vertical layout
        layoutWindowLeftLayout = QtWidgets.QVBoxLayout()

        # Create and add the list title
        layoutWindowLeftLayout.addWidget(QtWidgets.QLabel('<strong style="font-size: 18px">Selected Data<strong>'))

        # Connect and add the list
        self.windowList = DatasetListHTMLFormattedMultiple(inputDataset=self.layoutDataDoubleList.listOutput.datasetTable)
        self.layoutDataDoubleList.listOutput.updateSignalToExternal.connect(self.windowList.refreshDatasetListFromExtenal)
        layoutWindowLeftLayout.addWidget(self.windowList)

        ## Create the right panel ##
        # Create the layouts for subsequent use
        layoutWindowRightLayout = QtWidgets.QVBoxLayout()
        layoutWindowRightLayout.setContentsMargins(0, 0, 0, 0)

        layoutWindowRightOptionsLayout = QtWidgets.QGridLayout()
        layoutWindowRightOptionsLayout.setContentsMargins(0, 0, 0, 0)

        ### Setup the upper plot ###
        # Create the tab widget
        self.stackedWindowLayout = QtWidgets.QStackedLayout()

        stackedWindowLayoutWidget = QtWidgets.QWidget()
        stackedWindowLayoutWidget.setLayout(self.stackedWindowLayout)
        stackedWindowLayoutWidget.setVisible(False)

        # Create a line/bar plot object and add it into the stacked layout
        self.layoutWindowPlotStandard = ModelTabTargetPlot()
        self.layoutWindowPlotStandard.hide()
        self.stackedWindowLayout.addWidget(self.layoutWindowPlotStandard)

        # Create the layout for the windowed plot
        layoutWindowedPlotLayout = QtWidgets.QVBoxLayout()

        # Create windowed plot
        self.layoutWindowPlot = WindowTabPlots()

        # Add into the main layout
        layoutWindowedPlotLayout.addWidget(self.layoutWindowPlot)

        ## Create the start time widget ##
        # Create the label
        periodStartLabel = QtWidgets.QLabel('Start Date:')
        periodStartLabel.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)

        # Create the date widget
        self.periodStartWindow = QtWidgets.QDateTimeEdit()
        self.periodStartWindow.setDisplayFormat("MMMM d")
        self.periodStartWindow.setCalendarPopup(True)
        self.periodStartWindow.setMinimumDate(QtCore.QDate(1900, 1, 1))
        self.periodStartWindow.setMaximumDate(QtCore.QDate(QtCore.QDate().currentDate().year(), 12, 31))
        self.periodStartWindow.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)

        # Add the widgets to the layout
        periodLayout = QtWidgets.QHBoxLayout()
        periodLayout.setAlignment(QtCore.Qt.AlignLeft)
        periodLayout.addWidget(periodStartLabel)
        periodLayout.addWidget(self.periodStartWindow)

        ## Add a spacer widget ##
        spacer = QtWidgets.QSpacerItem(15, 0)
        periodLayout.addItem(spacer)

        ## Create the stop time widget ##
        # Create the label
        periodEndLabel = QtWidgets.QLabel('End Date:')
        periodEndLabel.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)

        # Create the date widget
        self.periodEndWindow = QtWidgets.QDateTimeEdit()
        self.periodEndWindow.setDisplayFormat("MMMM d")
        self.periodEndWindow.setCalendarPopup(True)
        self.periodEndWindow.setMinimumDate(QtCore.QDate(1900, 1, 1))
        self.periodEndWindow.setMaximumDate(QtCore.QDate(QtCore.QDate().currentDate().year(), 12, 31))
        self.periodEndWindow.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)

        # Add the widgets to the layout
        periodLayout.addWidget(periodEndLabel)
        periodLayout.addWidget(self.periodEndWindow)

        # Convert the layout to a widget and add to the parent layout
        periodLayoutWidget = QtWidgets.QWidget()
        periodLayoutWidget.setLayout(periodLayout)
        layoutWindowedPlotLayout.addWidget(periodLayoutWidget)

        # Promote the layout to a widget and add to the stack
        layoutWindowedPlotLayoutWidget = QtWidgets.QWidget()
        layoutWindowedPlotLayoutWidget.setLayout(layoutWindowedPlotLayout)
        self.stackedWindowLayout.addWidget(layoutWindowedPlotLayoutWidget)

        layoutWindowRightLayout.addWidget(stackedWindowLayoutWidget)

        ### Create a line to delineate the selector from the selector options ###
        lineA = QtWidgets.QFrame()
        lineA.setFrameShape(QtWidgets.QFrame.HLine)
        layoutWindowRightLayout.addWidget(lineA)

        ### Create a horizontal layout to accept the plotting rows ###
        layoutWindowRightBottom = QtWidgets.QHBoxLayout()

        ### Add the plotting layout options ###
        # Create the group
        layoutWindowPlottingGroup = QtWidgets.QGroupBox("Define the plotting variable:")

        # Create a plotting group layout
        plottingGroupLayout = QtWidgets.QVBoxLayout()
        plottingGroupLayout.setAlignment(QtCore.Qt.AlignTop)

        # Create the plotting selector
        self.layoutWindowPlottingOptionAggregated = QtWidgets.QRadioButton('Aggregated')
        self.layoutWindowPlottingOptionAggregated.setChecked(True)
        self.layoutWindowPlottingOptionRawCrossCorrelation = QtWidgets.QRadioButton('Raw Cross-correlation')
        self.layoutWindowPlottingOptionAggregatedCrossCorrelation = QtWidgets.QRadioButton('Aggregated Cross-correlation')

        # Add the widget/group to the layout
        plottingGroupLayout.addWidget(self.layoutWindowPlottingOptionAggregated)
        plottingGroupLayout.addWidget(QtWidgets.QLabel('       Summary of the selected variable with aggregation applied.'))
        plottingGroupLayout.addWidget(self.layoutWindowPlottingOptionRawCrossCorrelation)
        plottingGroupLayout.addWidget(QtWidgets.QLabel('       Cross-correlation of the selected timeseries before aggregation.'))
        plottingGroupLayout.addWidget(self.layoutWindowPlottingOptionAggregatedCrossCorrelation)
        plottingGroupLayout.addWidget(QtWidgets.QLabel('       Cross-correlation of the selected timeseries after aggregation'))

        # Set the layout into the group object
        layoutWindowPlottingGroup.setLayout(plottingGroupLayout)

        # Add the widget into the bottom layout
        layoutWindowRightBottom.addWidget(layoutWindowPlottingGroup)

        ### Add in summary statistics plot ###
        # Create the group
        layoutWindowCorrelationGroup = QtWidgets.QGroupBox("Correlation Statistics")

        # Create the group layout
        correlationGroupLayout = QtWidgets.QVBoxLayout()
        correlationGroupLayout.setAlignment(QtCore.Qt.AlignTop)

        # Create the raw label and box, adding to the layout
        rawCorrelationLabel = QtWidgets.QLabel('Raw Correlation')
        self.rawCorrelation = QtWidgets.QLineEdit('N/A')
        self.rawCorrelation.setReadOnly(True)

        correlationGroupLayout.addWidget(rawCorrelationLabel)
        correlationGroupLayout.addWidget(self.rawCorrelation)

        # Create the aggregated label and box, adding to tha layout
        aggregatedCorrelationLabel = QtWidgets.QLabel('Aggregated Correlation')
        self.aggregatedCorrelation = QtWidgets.QLineEdit('N/A')
        self.aggregatedCorrelation.setReadOnly(True)

        correlationGroupLayout.addWidget(aggregatedCorrelationLabel)
        correlationGroupLayout.addWidget(self.aggregatedCorrelation)

        # Promote the correlation group to a widget and add to the horizontal layout
        layoutWindowCorrelationGroup.setLayout(correlationGroupLayout)
        layoutWindowRightBottom.addWidget(layoutWindowCorrelationGroup)

        ### Add the aggregation options ###
        # Create the widget
        self.layoutWindowAggregationGroup = AggregationOptions(False, orientation='horizontal')
        self.layoutWindowAggregationGroup.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)

        # Add it into the page
        layoutWindowRightBottom.addWidget(self.layoutWindowAggregationGroup)
        # layoutWindowRightLayout.setAlignment(QtCore.Qt.AlignHCenter)

        ### Add the bottom layout into the right panel ###
        # Promote the layout to a widget
        layoutWindowRightBottomWidget = QtWidgets.QWidget()
        layoutWindowRightBottomWidget.setLayout(layoutWindowRightBottom)

        # Add the widget into the panel
        layoutWindowRightLayout.addWidget(layoutWindowRightBottomWidget)

        ### Create clear and apply buttons to apply operations ###
        # Create the clear button
        self.layoutWindowClearButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Clear</strong>')
        self.layoutWindowClearButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        # Create the apply button
        self.layoutWindowApplyButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Apply</strong>')
        self.layoutWindowApplyButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)

        # Create the layout, wrap it, and add to the right layout
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(self.layoutWindowClearButton)
        buttonLayout.addWidget(self.layoutWindowApplyButton)
        buttonLayout.setAlignment(QtCore.Qt.AlignRight)

        buttonLayoutWidget = QtWidgets.QWidget()
        buttonLayoutWidget.setLayout(buttonLayout)

        ## Create the full layout ##
        # Add the items to the right layout
        layoutWindowRightLayout.addWidget(buttonLayoutWidget)
        layoutWindowRightLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)

        # Create the horizontal layout
        layoutWindow = QtWidgets.QHBoxLayout()

        # Wrap the left layout in a widget and add to the layout
        leftWidget = QtWidgets.QWidget()
        leftWidget.setLayout(layoutWindowLeftLayout)
        layoutWindow.addWidget(leftWidget, 1)

        # Wrap the Right layout in a widget and add to the layout
        rightWidget = QtWidgets.QWidget()
        rightWidget.setLayout(layoutWindowRightLayout)
        layoutWindow.addWidget(rightWidget, 2)

        # Add the layout to the extend scrollable area
        layoutWindowSA.setLayout(layoutWindow)

        # Reenable the page to prevent window flashes
        stackedWindowLayoutWidget.setVisible(True)

    def _createOptionsTabLayout(self):
        """
        Lays out the options tab

        Parameters
        ----------
        None.

        Returns
        -------
        layoutMain: QT layout object
            Object containing all layout information to be placed in the widgets tab

        """

        # Create the page master layout
        layoutMain = QtWidgets.QVBoxLayout()
        layoutMain.setContentsMargins(15, 15, 15, 15)

        # Create the description text for the page
        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 24px">How should PyForecast build and evaluate models?</strong>')
        label.setSizePolicy( QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        layoutMain.addWidget(label)

        ### Create the initial dialog for the type of analysis ###
        labelMode = QtWidgets.QLabel()
        labelMode.setTextFormat(QtCore.Qt.RichText)
        labelMode.setText('<strong style="font-size: 12px">Select modeling configuration:</strong>')
        labelMode.setFixedWidth(250)

        self.defButton = QtWidgets.QRadioButton('Default')
        self.defButton.setStyleSheet('QRadioButton{font: 8pt sans-serif;} QRadioButton::indicator { width: 12px; height: 12px;};')
        self.defButton.setChecked(False)
        self.defButton.setFixedWidth(100)
        self.expertButton = QtWidgets.QRadioButton('Expert')
        self.expertButton.setStyleSheet('QRadioButton{font: 8pt; sans-serif} QRadioButton::indicator { width: 12px; height: 12px;};')
        self.expertButton.setChecked(True)
        self.expertButton.setFixedWidth(100)

        bgroup = QtWidgets.QButtonGroup()
        bgroup.addButton(self.defaultPredictorButton)
        bgroup.addButton(self.expertPredictorButton)
        bgroup.setExclusive(True)

        predictorModeLayout = QtWidgets.QHBoxLayout()
        predictorModeLayout.addWidget(labelMode)
        predictorModeLayout.addWidget(self.defButton)
        predictorModeLayout.addWidget(self.expertButton)
        predictorModeLayout.setAlignment(QtCore.Qt.AlignLeft)

        gb = QtWidgets.QGroupBox("")
        gb.setLayout(predictorModeLayout)
        gb.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        layoutMain.addSpacerItem(QtWidgets.QSpacerItem(0, 5, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))
        layoutMain.addWidget(gb)
        layoutMain.addSpacerItem(QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        ### Setup the cross-validation algorithms ###
        ## Create the label ##
        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Cross-Validation Algorithms</strong>')
        label.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        layoutMain.addWidget(label)

        label = QtWidgets.QLabel("Select one algorithm:")
        label.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        layoutMain.addWidget(label)

        ## Set the boxes containing options into the layout grid ##
        # Create and format the layout
        crossValidationLayout = QtWidgets.QGridLayout()
        crossValidationLayout.setContentsMargins(1, 1, 1, 1)

        # Loop and fill the layout
        self.optionsCrossValidators = []
        numCrossValidators = len(self.parent.crossValidators.keys())
        for i in range(int(numCrossValidators / 3) + 1 if numCrossValidators % 3 != 0 else int(numCrossValidators / 3)):
            for j in range(3):
                if (i * 3) + j < numCrossValidators:
                    cvKey = list((self.parent.crossValidators.keys()))[(3 * i) + j]
                    cvText = '<strong style="font-size: 13px; color: darkcyan">{0}</strong><br>{1}'.format(
                        self.parent.crossValidators[cvKey]['name'], self.parent.crossValidators[cvKey]['description'])
                    button = richTextButtonCheckbox(cvText)
                    button.setObjectName(str(cvKey))

                    # Add the button to the layout and the tracking list
                    crossValidationLayout.addWidget(button, i, j, 1, 1)
                    self.optionsCrossValidators.append(button)

        # Promote the layout to a widget
        crossValidationLayoutWidget = QtWidgets.QWidget()
        crossValidationLayoutWidget.setLayout(crossValidationLayout)
        crossValidationLayoutWidget.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)

        # layoutMain.addLayout(crossValidationLayout)
        layoutMain.addWidget(crossValidationLayoutWidget)
        layoutMain.addSpacerItem(QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        ### Setup the preprocessing algorithms ###
        ## Create the label ##
        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Preprocessing Algorithms</strong>')
        label.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        layoutMain.addWidget(label)

        label = QtWidgets.QLabel("Select one or more algorithms:")
        label.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        layoutMain.addWidget(label)

        ## Set the boxes containing options into the layout grid ##
        # Create and format the layout
        optionsPreprocessorLayout = QtWidgets.QGridLayout()
        optionsPreprocessorLayout.setContentsMargins(1, 1, 1, 1)

        # Loop and fill the layout
        self.optionsPreprocessor = []
        numPreProcessors = len(self.parent.preProcessors.keys())
        for i in range(int(numPreProcessors / 3) + 1 if numPreProcessors % 3 != 0 else int(numPreProcessors / 3)):
            for j in range(3):
                if (i * 3) + j < numPreProcessors:
                    prKey = list((self.parent.preProcessors.keys()))[(3 * i) + j]
                    regrText = '<strong style="font-size: 13px; color: darkcyan">{0}</strong><br>{1}'.format(
                        self.parent.preProcessors[prKey]['name'], self.parent.preProcessors[prKey]['description'])
                    button = richTextButtonCheckbox(regrText)
                    button.setObjectName(str(prKey))

                    # Add the button to the layout and the tracking list
                    optionsPreprocessorLayout.addWidget(button, i, j, 1, 1)
                    self.optionsPreprocessor.append(button)

        # Promote the layout to a widget
        optionsPreprocessorLayoutWidget = QtWidgets.QWidget()
        optionsPreprocessorLayoutWidget.setLayout(optionsPreprocessorLayout)

        # layoutMain.addLayout(optionsPreprocessorLayout)
        layoutMain.addWidget(optionsPreprocessorLayoutWidget)
        layoutMain.addSpacerItem(QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        ### Setup the regression algorithms ###
        ## Create the label ##
        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Regression Algorithms</strong>')
        label.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        layoutMain.addWidget(label)

        label = QtWidgets.QLabel("Select one or more algorithms:")
        label.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        layoutMain.addWidget(label)

        ## Set the boxes containing options into the layout grid ##
        # Create and format the layout
        optionsRegressionLayout = QtWidgets.QGridLayout()
        optionsRegressionLayout.setContentsMargins(1, 1, 1, 1)

        # Loop and fill the layout
        self.optionsRegression = []
        numRegressionModels = len(self.parent.regressors.keys())
        for i in range(int(numRegressionModels / 3) + 1 if numRegressionModels % 3 != 0 else int(numRegressionModels / 3)):
            for j in range(3):
                if (i * 3) + j < numRegressionModels:
                    regrKey = list((self.parent.regressors.keys()))[(3 * i) + j]
                    regrText = '<strong style="font-size: 13px; color: darkcyan">{0}</strong><br>{1}<br>More Info: {2}'.format(
                        self.parent.regressors[regrKey]['name'], self.parent.regressors[regrKey]['description'],
                        self.parent.regressors[regrKey]['website'])
                    button = richTextButtonCheckbox(regrText)
                    button.setObjectName(str(regrKey))

                    # Add the button to the layout and the tracking list
                    optionsRegressionLayout.addWidget(button, i, j, 1, 1)
                    self.optionsRegression.append(button)

        # Promote the layout to a widget
        optionsRegressionLayoutWidget = QtWidgets.QWidget()
        optionsRegressionLayoutWidget.setLayout(optionsRegressionLayout)

        # layoutMain.addLayout(optionsRegressionLayout)
        layoutMain.addWidget(optionsRegressionLayoutWidget)
        layoutMain.addSpacerItem(QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        ### Setup the model selection algorithms ###
        ## Create the label ##
        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Model Selection Algorithms</strong>')
        label.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        layoutMain.addWidget(label)

        label = QtWidgets.QLabel("Select one or more algorithms:")
        label.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        layoutMain.addWidget(label)

        ## Set the boxes containing options into the layout grid ##
        # Create and format the layout
        optionsSelectionLayout = QtWidgets.QGridLayout()
        optionsSelectionLayout.setContentsMargins(1, 1, 1, 1)

        # Loop and fill the layout
        self.optionsSelection = []
        numFeatSelectors = len(self.parent.featureSelectors.keys())
        for i in range(int(numFeatSelectors / 3) + 1 if numFeatSelectors % 3 != 0 else int(numFeatSelectors / 3)):
            for j in range(3):
                if (i * 3) + j < numFeatSelectors:
                    regrKey = list((self.parent.featureSelectors.keys()))[(3 * i) + j]
                    regrText = '<strong style="font-size: 13px; color: darkcyan">{0}</strong><br>{1}'.format(
                        self.parent.featureSelectors[regrKey]['name'],
                        self.parent.featureSelectors[regrKey]['description'])
                    button = richTextButtonCheckbox(regrText)
                    button.setObjectName(str(regrKey))

                    # Add the button to the layout and the holding list
                    optionsSelectionLayout.addWidget(button, i, j, 1, 1)
                    self.optionsSelection.append(button)

        # Promote the layout to a widget
        optionsSelectionLayoutWidget = QtWidgets.QWidget()
        optionsSelectionLayoutWidget.setLayout(optionsSelectionLayout)

        # layoutMain.addLayout(optionsSelectionLayout)
        layoutMain.addWidget(optionsSelectionLayoutWidget)
        layoutMain.addSpacerItem(QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        ### Setup the model scoring algorithms ###
        ## Create the label ##
        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 18px">Model Scoring</strong>')
        label.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        layoutMain.addWidget(label)

        label = QtWidgets.QLabel("Select one or more scoring parameters (used to rank models):")
        label.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        layoutMain.addWidget(label)

        ## Set the boxes containing options into the layout grid ##
        # Create and format the layout
        optionsScoringLayout = QtWidgets.QGridLayout()
        optionsScoringLayout.setContentsMargins(1, 1, 1, 1)

        # Loop and fill the layout
        self.optionsScoring = []
        numScorers = len(self.parent.scorers['info'].keys())
        for i in range(int(numScorers / 3) + 1 if numScorers % 3 != 0 else int(numScorers / 3)):
            # layout2 = QtWidgets.QHBoxLayout()
            # layout2.setContentsMargins(1,1,1,1)
            for j in range(3):
                if (i * 3) + j < numScorers:
                    nameKey = list((self.parent.scorers['info'].keys()))[(3 * i) + j]
                    regrText = '<strong style="font-size: 13px; color:darkcyan">{2}</strong><br>{0}'.format(
                        self.parent.scorers['info'][nameKey]['NAME'], self.parent.scorers['info'][nameKey]['WEBSITE'],
                        self.parent.scorers['info'][nameKey]['HTML'])
                    button = richTextButtonCheckbox(regrText)
                    button.setObjectName(str(nameKey))

                    # Add the button to the layout and the holding list
                    optionsScoringLayout.addWidget(button, i, j, 1, 1)
                    self.optionsScoring.append(button)

        # Promote the layout ot a widget
        optionsScoringLayoutWidget = QtWidgets.QWidget()
        optionsScoringLayoutWidget.setLayout(optionsScoringLayout)

        # layoutMain.addLayout(optionsScoringLayout)
        layoutMain.addWidget(optionsScoringLayoutWidget)

        # items = (layout.itemAt(i) for i in range(layout.count()))
        # print(items)
        # for w in items:
        #     w.ResizeEvent()

        # layout2.addWidget(richTextButton(self, '<strong style="color:maroon">Multiple Linear Regression</strong><br>Ordinary Least Squares'))
        # layout2.addWidget(richTextButton(self, '<strong style="color:maroon">Principal Components Regression</strong><br>Ordinary Least Squares'))
        # layout2.addWidget(richTextButton(self, '<strong style="color:maroon">Z-Score Regression</strong><br>Ordinary Least Squares'))

        #layoutMain.addSpacerItem(QtWidgets.QSpacerItem(100, 100, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        return layoutMain

    def _createSummaryTabLayout(self, mainLayout):
        """
        Lays out the summary tab

        Parameters
        ----------
        None.

        Returns
        -------
        layoutMain: QT layout object
            Object containing all layout information to be placed in the widgets tab

        """

        ### Create the description text for the page ###
        label = QtWidgets.QLabel()
        label.setTextFormat(QtCore.Qt.RichText)
        label.setText('<strong style="font-size: 24px">Summary of the PyForecast analysis</strong>')
        mainLayout.addWidget(label)

        ### Create a horizontal layout to add the left and right pages into ###
        tabLayout = QtWidgets.QHBoxLayout()
        tabLayout.setContentsMargins(0, 0, 0, 0)

        ### Create the left side dataset summary table ###
        # Create a vertical layout
        listLayout = QtWidgets.QVBoxLayout()
        listLayout.setContentsMargins(0, 10, 5, 0)

        #listLayout.setContentsMargins(2, 2, 2, 2)
        listLayout.addWidget(QtWidgets.QLabel('<strong style="font-size: 18px">Model Training Period<strong>'))
        self.summaryLayoutLabel1 = QtWidgets.QLabel('     Period: None')
        listLayout.addWidget(self.summaryLayoutLabel1)
        listLayout.addWidget(QtWidgets.QLabel(''))
        listLayout.addWidget(QtWidgets.QLabel('<strong style="font-size: 18px">Predictand<strong>'))
        self.summaryLayoutLabel2 = QtWidgets.QLabel('     Predictand: None')
        self.summaryLayoutLabel3 = QtWidgets.QLabel('     Predictand Period: None')
        self.summaryLayoutLabel4 = QtWidgets.QLabel('     Predictand Method: None')
        listLayout.addWidget(self.summaryLayoutLabel2)
        listLayout.addWidget(self.summaryLayoutLabel3)
        listLayout.addWidget(self.summaryLayoutLabel4)
        listLayout.addWidget(QtWidgets.QLabel(''))
        listLayout.addWidget(QtWidgets.QLabel('<strong style="font-size: 18px">Predictors<strong>'))

        # Create the list widget
        self.summaryListWidget = SpreadSheetViewOperations(self.parent.datasetTable, self.parent.datasetOperationsTable,
                                                           parent=self)

        # Connect the summary list to change with the operations table
        listLayout.addWidget(self.summaryListWidget)
        listLayout.addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        # Force the background color to prevent bleed through of the SA color in the headings
        listLayoutWidget = QtWidgets.QWidget()
        listLayoutWidget.setLayout(listLayout)
        #listLayoutWidget.setStyleSheet("background-color:white;")

        # Add to the layout
        tabLayout.addWidget(listLayoutWidget)

        ### Create the right side of the pane ###
        ## Create a vertical layout ##
        summaryRightLayout = QtWidgets.QVBoxLayout()
        summaryRightLayout.setContentsMargins(5, 10, 0, 0)

        ## Layout the cross validators grid ##
        # Create the label
        crossValidatorLabelWidget = QtWidgets.QLabel('<strong style="font-size: 18px">Cross-Validators</strong>')

        # Add the label into the right layout
        summaryRightLayout.addWidget(crossValidatorLabelWidget)

        # Create the grid layout
        crossValidatorLayout = QtWidgets.QGridLayout()
        crossValidatorLayout.setContentsMargins(0, 0, 0, 0)

        # Loop and fill the cross validation options
        numCrossValidators = len(self.parent.crossValidators.keys())
        counter = 0
        for i in range(int(numCrossValidators/3) + 1 if numCrossValidators%3 != 0 else int(numCrossValidators/3)):
            for j in range(3):
                if (i*3)+j < numCrossValidators:
                    cvKey = list((self.parent.crossValidators.keys()))[(3*i)+j]
                    cvText = '<strong style="font-size: 13px; color: darkcyan">{0}</strong>'.format(self.parent.crossValidators[cvKey]['name'])

                    # Disable the button to prevent user adjustements
                    button = richTextButtonCheckbox(cvText)
                    button.setDisabled(True)

                    # Add the button into the layout
                    crossValidatorLayout.addWidget(button, i, j, 1, 1)

                    # Link the button with the corresponding box on the options tab
                    recipricalBox = self.optionsCrossValidators[counter]
                    recipricalBox.updateLinkedButton.connect(button.update_from_external)
                    counter += 1

        # Wrap the layout in a widget and add to the layout
        crossValidatorLayoutWidget = QtWidgets.QWidget()
        crossValidatorLayoutWidget.setLayout(crossValidatorLayout)
        summaryRightLayout.addWidget(crossValidatorLayoutWidget)
        summaryRightLayout.addSpacerItem(QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        ## Layout the preprocessors grid ##
        # Create the label
        preprocessorLabelWidget = QtWidgets.QLabel('<strong style="font-size: 18px">Preprocessors</strong>')

        # Add the label into the right layout
        summaryRightLayout.addWidget(preprocessorLabelWidget)

        # Create the grid layout
        preprocessorLayout = QtWidgets.QGridLayout()
        preprocessorLayout.setContentsMargins(0, 0, 0, 0)

        # Loop and fill the preprocessor options
        numPreProcessors = len(self.parent.preProcessors.keys())
        counter = 0
        for i in range(int(numPreProcessors/3) + 1 if numPreProcessors%3 != 0 else int(numPreProcessors/3)):
            for j in range(3):
                if (i*3)+j < numPreProcessors:
                    prKey = list((self.parent.preProcessors.keys()))[(3*i)+j]
                    regrText = '<strong style="font-size: 13px; color: darkcyan">{0}</strong>'.format(self.parent.preProcessors[prKey]['name'])

                    # Disable the button to prevent user adjustements
                    button = richTextButtonCheckbox(regrText)
                    button.setDisabled(True)

                    # Add the button into the layout
                    preprocessorLayout.addWidget(button, i, j, 1, 1)

                    # Link the button with the corresponding box on the options tab
                    recipricalBox = self.optionsPreprocessor[counter]
                    recipricalBox.updateLinkedButton.connect(button.update_from_external)
                    counter += 1

        # Wrap the layout in a widget and add to the layout
        preprocessorLayoutWidget = QtWidgets.QWidget()
        preprocessorLayoutWidget.setLayout(preprocessorLayout)
        summaryRightLayout.addWidget(preprocessorLayoutWidget)
        summaryRightLayout.addSpacerItem(QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        ## Layout the regressors grid ##
        # Create the label
        regressorLabelWidget = QtWidgets.QLabel('<strong style="font-size: 18px">Regressors</strong>')

        # Add the label into the right layout
        summaryRightLayout.addWidget(regressorLabelWidget)

        # Create the grid layout
        regressorLayout = QtWidgets.QGridLayout()
        regressorLayout.setContentsMargins(0, 0, 0, 0)

        # Loop and fill the preprocessor options
        numRegressors = len(self.parent.regressors.keys())
        counter = 0
        for i in range(int(numRegressors / 3) + 1 if numRegressors % 3 != 0 else int(numRegressors / 3)):
            for j in range(3):
                if (i * 3) + j < numRegressors:
                    prKey = list((self.parent.regressors.keys()))[(3 * i) + j]
                    regrText = '<strong style="font-size: 13px; color: darkcyan">{0}</strong>'.format(self.parent.regressors[prKey]['name'])

                    # Disable the button to prevent user adjustements
                    button = richTextButtonCheckbox(regrText)
                    button.setDisabled(True)

                    # Add the button into the layout
                    regressorLayout.addWidget(button, i, j, 1, 1)

                    # Link the button with the corresponding box on the options tab
                    recipricalBox = self.optionsRegression[counter]
                    recipricalBox.updateLinkedButton.connect(button.update_from_external)
                    counter += 1


        # Wrap the layout in a widget and add to the layout
        regressorLayoutWidget = QtWidgets.QWidget()
        regressorLayoutWidget.setLayout(regressorLayout)
        summaryRightLayout.addWidget(regressorLayoutWidget)
        summaryRightLayout.addSpacerItem(QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        ## Layout the feature selectors grid ##
        # Create the label
        selectorLabelWidget = QtWidgets.QLabel('<strong style="font-size: 18px">Feature Selectors</strong>')

        # Add the label into the right layout
        summaryRightLayout.addWidget(selectorLabelWidget)

        # Create the grid layout
        selectorLayout = QtWidgets.QGridLayout()
        selectorLayout.setContentsMargins(0, 0, 0, 0)

        # Loop and fill the preprocessor options
        numSelector = len(self.parent.featureSelectors.keys())
        counter = 0
        for i in range(int(numSelector / 3) + 1 if numSelector % 3 != 0 else int(numSelector / 3)):
            for j in range(3):
                if (i * 3) + j < numSelector:
                    prKey = list((self.parent.featureSelectors.keys()))[(3 * i) + j]
                    regrText = '<strong style="font-size: 13px; color: darkcyan">{0}</strong>'.format(self.parent.featureSelectors[prKey]['name'])

                    # Disable the button to prevent user adjustments
                    button = richTextButtonCheckbox(regrText)
                    button.setDisabled(True)

                    # Add the button into the layout
                    selectorLayout.addWidget(button, i, j, 1, 1)

                    # Link the button with the corresponding box on the options tab
                    recipricalBox = self.optionsSelection[counter]
                    recipricalBox.updateLinkedButton.connect(button.update_from_external)
                    counter += 1

        # Wrap the layout in a widget and add to the layout
        selectorLayoutWidget = QtWidgets.QWidget()
        selectorLayoutWidget.setLayout(selectorLayout)
        summaryRightLayout.addWidget(selectorLayoutWidget)
        summaryRightLayout.addSpacerItem(QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed))

        ## Layout the scoring grid ##
        # Create the label
        scoringLabelWidget = QtWidgets.QLabel('<strong style="font-size: 18px">Model Scoring</strong>')

        # Add the label into the right layout
        summaryRightLayout.addWidget(scoringLabelWidget)

        # Create the grid layout
        scoringLayout = QtWidgets.QGridLayout()
        scoringLayout.setContentsMargins(0, 0, 0, 0)

        # Loop and fill the preprocessor options
        numScorers = len(self.parent.scorers['info'].keys())
        counter = 0
        for i in range(int(numScorers/3) + 1 if numScorers%3 != 0 else int(numScorers/3)):
            for j in range(3):
                if (i*3)+j < numScorers:
                    nameKey = list((self.parent.scorers['info'].keys()))[(3*i)+j]
                    regrText = '<strong style="font-size: 13px; color:darkcyan">{0}</strong>'.format(self.parent.scorers['info'][nameKey]['NAME'])

                    # Disable the button to prevent user adjustements
                    button = richTextButtonCheckbox(regrText)
                    button.setDisabled(True)

                    # Add to the layout object
                    scoringLayout.addWidget(button, i, j, 1, 1)

                    # Link the button with the corresponding box on the options tab
                    recipricalBox = self.optionsScoring[counter]
                    recipricalBox.updateLinkedButton.connect(button.update_from_external)
                    counter += 1

        # Wrap the layout in a widget and add to the layout
        scoringLayoutWidget = QtWidgets.QWidget()
        scoringLayoutWidget.setLayout(scoringLayout)
        summaryRightLayout.addWidget(scoringLayoutWidget)

        ## Add a spacer to prevent strange box sizes ##
        summaryRightLayout.addSpacerItem(QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.MinimumExpanding))

        ## Set a horizontal break line ##
        # Create a line to delineate the selector from the selector options
        lineA = QtWidgets.QFrame()
        lineA.setFrameShape(QtWidgets.QFrame.HLine)
        summaryRightLayout.addWidget(lineA)

        ## Create and add the activation buttons ##
        # Create the clear button
        self.summaryClearButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Clear</strong>')
        self.summaryClearButton.setMaximumSize(125, 65)

        # Create the start button
        self.summaryStartButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Start</strong>')
        self.summaryStartButton.setMaximumSize(125, 65)

        # Add placeholder for potential error messages
        self.summaryLayoutErrorLabel = QtWidgets.QLabel('')
        self.summaryLayoutErrorLabel.setVisible(False)
        self.summaryLayoutErrorLabel.setWordWrap(True)

        # Create an horizontal layout, aligned to the right
        summaryButtonsLayout = QtWidgets.QHBoxLayout()
        summaryButtonsLayout.setAlignment(QtCore.Qt.AlignRight)
        summaryRightLayout.addWidget(self.summaryLayoutErrorLabel)

        summaryButtonsLayout.addWidget(self.summaryClearButton)
        summaryButtonsLayout.addWidget(self.summaryStartButton)

        # Wrap the layout as a widget and add to the main layout
        summaryButtonsLayoutWidget = QtWidgets.QWidget()
        summaryButtonsLayoutWidget.setLayout(summaryButtonsLayout)
        summaryRightLayout.addWidget(summaryButtonsLayoutWidget)

        ## Add the summary right pane to the summary layout ##
        # Create the widget to wrap the layout
        rightLayoutWidget = QtWidgets.QWidget()
        rightLayoutWidget.setLayout(summaryRightLayout)

        # Add the widget to the main layout
        tabLayout.addWidget(rightLayoutWidget)

        ### Promote the tab layout to a widget and add to the main layout ###
        tabLayoutWidget = QtWidgets.QWidget()
        tabLayoutWidget.setLayout(tabLayout)
        mainLayout.addWidget(tabLayoutWidget)

    def _createResultsTabLayout(self, resultSA):
        """
        Lays out the results tab

        Parameters
        ----------
        None.

        Returns
        -------
        resultSA: QT scrollable area


        """

        ### Create the left side dataset summary table ###
        # Create a horizontal layout
        topLayout = QtWidgets.QHBoxLayout()
        topLayout.setContentsMargins(0, 0, 0, 5)

        # Create the list of model filters
        ## Create the table to show the metrics ##
        topInfoLayoutTable = QtWidgets.QVBoxLayout()
        topInfoLayoutTable.setContentsMargins(0, 0, 5, 0)

        resultSelectedLabel = QtWidgets.QLabel('<strong style="font-size: 18px">Available Regressions<strong>')
        self.exportResultModelsButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Generated Models Analysis</strong>')
        self.exportResultModelsButton.setMaximumSize(250, 50)
        self.exportResultModelsButton.setEnabled(True)
        tableHeaderLayout = QtWidgets.QHBoxLayout()
        tableHeaderLayout.addWidget(resultSelectedLabel)
        tableHeaderLayout.addWidget(self.exportResultModelsButton)
        tableHeaderWidget = QtWidgets.QWidget()
        tableHeaderWidget.setLayout(tableHeaderLayout)
        topInfoLayoutTable.addWidget(tableHeaderWidget)

        self.resultsMetricTable = SpreadSheetForecastEquations(self.parent.forecastEquationsTable, parent=self)
        topInfoLayoutTable.addWidget(self.resultsMetricTable)

        topInfoLayoutTableWidget = QtWidgets.QWidget()
        topInfoLayoutTableWidget.setLayout(topInfoLayoutTable)
        topInfoLayoutTableWidget.setContentsMargins(0, 0, 0, 0)
        topLayout.addWidget(topInfoLayoutTableWidget)

        # Create a list for the selected model metadata
        topInfoLayout = QtWidgets.QVBoxLayout()
        topInfoLayout.setContentsMargins(5, 0, 0, 0)

        resultSelectedLabel = QtWidgets.QLabel('<strong style="font-size: 18px">Selected Model Info<strong>')
        topInfoLayout.addWidget(resultSelectedLabel)

        self.resultSelectedList = QtWidgets.QListWidget()
        topInfoLayout.addWidget(self.resultSelectedList)

        topInfoLayoutWidget = QtWidgets.QWidget()
        topInfoLayoutWidget.setLayout(topInfoLayout)
        topInfoLayoutWidget.setContentsMargins(0, 0, 0, 0)

        topLayout.addWidget(topInfoLayoutWidget)

        ### Create the right side items ###
        ## Create the initial layouts ##
        bottomLayout = QtWidgets.QHBoxLayout()
        bottomLayout.setContentsMargins(0, 5, 0, 0)

        bottomLayoutHorizontal = QtWidgets.QHBoxLayout()
        bottomLayoutHorizontal.setContentsMargins(0, 0, 5, 0)

        rightLayoutVertical = QtWidgets.QVBoxLayout()
        rightLayoutVertical.setContentsMargins(5, 0, 0, 0)

        ## Create the main left observed/forecast plot ##
        self.resultsObservedForecstPlot = ResultsTabPlots(self, xLabel='Observed', yLabel='Prediction')
        self.resultsObservedForecstPlot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        ## Create the upper right inflow/year plot ##
        self.resultsInflowYearPlot = ResultsTabPlots(self, xLabel='Year', yLabel='Value')
        self.resultsInflowYearPlot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)


        ## Create the lower right residual/year plot ##
        self.resultsResidualYearPlot = ResultsTabPlots(self, xLabel='Year', yLabel='Error')
        self.resultsResidualYearPlot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        ## Add items into the layouts ##
        # Add the subplots to the vertical layout
        rightLayoutVertical.addWidget(self.resultsInflowYearPlot)
        rightLayoutVertical.addWidget(self.resultsResidualYearPlot)

        # Wrap the vertical layout as a widget 
        rightLayoutVerticalWidget = QtWidgets.QWidget()
        rightLayoutVerticalWidget.setLayout(rightLayoutVertical)
        rightLayoutVerticalWidget.setContentsMargins(0, 0, 0, 0)

        # Add items to the horizontal layout
        bottomLayoutHorizontal.addWidget(self.resultsObservedForecstPlot)

        # Wrap the horizontal layout as a widget
        rightLayoutHorizontalWidget = QtWidgets.QWidget()
        rightLayoutHorizontalWidget.setLayout(bottomLayoutHorizontal)
        rightLayoutHorizontalWidget.setContentsMargins(0, 0, 0, 0)

        # Add items into the main right layout
        bottomLayout.addWidget(rightLayoutHorizontalWidget)
        bottomLayout.addWidget(rightLayoutVerticalWidget)

        ### Add the items into the layout ###
        # Create the horizontal layout
        layoutMain = QtWidgets.QVBoxLayout()
        layoutMain.setContentsMargins(15, 15, 15, 15)

        ## Add the left layout ##
        # Promote the layout to a widget
        topLayoutWidget = QtWidgets.QWidget()
        topLayoutWidget.setLayout(topLayout)

        # Add it to the layout
        layoutMain.addWidget(topLayoutWidget)

        ## Add the right layout ##
        # Promote the right layout to a widget
        bottomLayoutWidget = QtWidgets.QWidget()
        bottomLayoutWidget.setLayout(bottomLayout)

        # Add it into the layout
        layoutMain.addWidget(bottomLayoutWidget)

        ## Add into the scrollable area ##
        layoutMainWidget = QtWidgets.QWidget()
        layoutMainWidget.setLayout(layoutMain)
        resultSA.setWidget(layoutMainWidget)

    def setPredictorDefaultStack(self):
        self.stackedPredictorWidget.setCurrentIndex(0)

    def setPredictorExpertStack(self):      
        self.stackedPredictorWidget.setCurrentIndex(1)

