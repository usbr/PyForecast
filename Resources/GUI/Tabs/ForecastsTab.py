"""
Script Name:        ForecastsTab.py

Description:      
"""
import sys
import os
#sys.path.append(r"C:\Users\KFoley\Documents\NextFlow")

from PyQt5 import  QtWidgets, QtCore, QtGui
from resources.GUI.CustomWidgets.forecastList_FormattedHTML import forecastList_HTML
from resources.GUI.CustomWidgets.customTabs import EnhancedTabWidget
from resources.GUI.CustomWidgets.SpreadSheet import SpreadSheetForecastEquations
from resources.GUI.CustomWidgets.PyQtGraphs_V2 import ResultsTabPlots
from resources.modules.ForecastsTab.forecastTabMaster import *
from resources.GUI.CustomWidgets.richTextButtons import richTextButton, richTextButtonCheckbox, richTextDescriptionButton


class ForecastsTab(QtWidgets.QWidget):
    """
    """

    def __init__(self, parent = None):

        QtWidgets.QWidget.__init__(self, parent)

        self.parent = parent

        # Overall layouts
        overallLayout = QtWidgets.QHBoxLayout()
        overallLayout.setContentsMargins(0,0,0,0)

        # Right side tab widget
        self.workflowWidget = EnhancedTabWidget(self, "above", "vertical", True, True, True)

        # ===================================================================================================================

        # Layout the Forecast Detail Widget

        # Create the scrollable area
        forecastDetail = QtWidgets.QScrollArea()
        forecastDetail.setWidgetResizable(True)
        self._createForecastDetailTabLayout(forecastDetail)
        #forecastDetail = QtWidgets.QWidget()

        self.workflowWidget.addTab(forecastDetail, "FORECAST<br>DETAIL", "resources/GraphicalResources/icons/chart_scatter-24px.svg",
                         "#FFFFFF", iconSize=(25, 25))

        # ===================================================================================================================

        # Layout the Forecast Comparison Widget

        # Create the scrollable area
        forecastComparison = QtWidgets.QScrollArea()
        forecastComparison.setWidgetResizable(True)
        self._createForecastComparisonTabLayout(forecastComparison)
        #aggPage = QtWidgets.QWidget()

        self.workflowWidget.addTab(forecastComparison, "COMPARE<br>FORECASTS", "resources/GraphicalResources/icons/chart_bellcurve-24px.svg",
                         "#FFFFFF", iconSize=(25, 25))

        # ===================================================================================================================

        # Layout the Configuration Widget

        configPage = QtWidgets.QWidget()
        self.workflowWidget.addTab(configPage, "CONFIGURE", "resources/GraphicalResources/icons/settings-24px.svg",
                               "#FFFFFF", iconSize=(20, 20))

        # ===================================================================================================================

        #self.forecastsPane = forecastList_HTML(self.parent)
        #self.forecastsPane.setFixedWidth(300)
        #self.forecastsPane.setContentsMargins(0,0,0,0)
        #overallLayout.addWidget(self.forecastsPane)
        overallLayout.addWidget(self.workflowWidget)


        # Set the widgets layout
        self.setLayout(overallLayout)
        self.setContentsMargins(0,0,0,0)


    def _createForecastDetailTabLayout(self, forecastDetail):
        """
        Lays out the forecast detail tab

        Parameters
        ----------
        None.

        Returns
        -------
        forecastDetail: QT scrollable area


        """

        ### Create the left side dataset summary table ###
        # Create a horizontal layout
        topLayout = QtWidgets.QHBoxLayout()

        # Create the list of model filters
        ## Create the table to show the metrics ##
        topInfoLayoutTable = QtWidgets.QVBoxLayout()

        resultSelectedLabel = QtWidgets.QLabel('<strong style="font-size: 18px">Saved Models<strong>')
        topInfoLayoutTable.addWidget(resultSelectedLabel)

        self.savedModelsTable = SpreadSheetForecastEquations(self.parent.forecastEquationsTable, parent=self)
        topInfoLayoutTable.addWidget(self.savedModelsTable)

        topInfoLayoutTableWidget = QtWidgets.QWidget()
        topInfoLayoutTableWidget.setLayout(topInfoLayoutTable)
        topInfoLayoutTableWidget.setContentsMargins(0, 0, 0, 0)

        topLayout.addWidget(topInfoLayoutTableWidget)

        # Create a list for the selected model metadata
        topInfoLayout = QtWidgets.QVBoxLayout()

        resultSelectedLabel = QtWidgets.QLabel('<strong style="font-size: 18px">Selected Model Info<strong>')
        topInfoLayout.addWidget(resultSelectedLabel)

        self.resultSelectedList = QtWidgets.QListWidget()
        topInfoLayout.addWidget(self.resultSelectedList)

        topInfoLayoutWidget = QtWidgets.QWidget()
        topInfoLayoutWidget.setLayout(topInfoLayout)
        topInfoLayoutWidget.setContentsMargins(0, 0, 0, 0)

        topLayout.addWidget(topInfoLayoutWidget)

        ### Create the bottom items ###
        bottomLayout = QtWidgets.QHBoxLayout()

        ### Create the bottom right side items ###
        bottomRightLayout = QtWidgets.QHBoxLayout()
        bottomRightLayout.setContentsMargins(0, 0, 0, 0)

        ## Create the main left observed/forecast plot ##
        self.resultsObservedForecstPlot = ResultsTabPlots(self, xLabel='Observed', yLabel='Prediction')
        self.resultsObservedForecstPlot.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Add items to the horizontal layout
        bottomRightLayout.addWidget(self.resultsObservedForecstPlot)

        # Wrap the horizontal layout as a widget
        bottomRightLayoutWidget = QtWidgets.QWidget()
        bottomRightLayoutWidget.setLayout(bottomRightLayout)

        ### Create the bottom left side items ###
        bottomLeftLayout = QtWidgets.QVBoxLayout()
        bottomLeftLayout.setContentsMargins(0, 0, 0, 0)

        selectedModelLabel = QtWidgets.QLabel('<strong style="font-size: 18px">Selected Model Data<strong>')
        bottomLeftLayout.addWidget(selectedModelLabel)

        selectedModelYearLayout = QtWidgets.QHBoxLayout()
        selectedModelYearLabel = QtWidgets.QLabel('<strong>Model Run Year:<strong>')
        selectedModelYearLayout.addWidget(selectedModelYearLabel)
        modelYearSpin = QtWidgets.QSpinBox()
        selectedModelYearLayout.addWidget(modelYearSpin)
        selectedModelYearLayoutWidget = QtWidgets.QWidget()
        selectedModelYearLayoutWidget.setLayout(selectedModelYearLayout)

        ## Create the main left observed/forecast plot ##
        self.selectedModelDataTable = QtWidgets.QTableView()

        self.runModelButton = richTextButton('<strong style="font-size: 16px; color:darkcyan">Run Model</strong>')

        # Add items to the bottom left layout
        bottomLeftLayout.addWidget(selectedModelYearLayoutWidget)
        bottomLeftLayout.addWidget(self.selectedModelDataTable)
        bottomLeftLayout.addWidget(self.runModelButton)

        # Wrap the horizontal layout as a widget
        bottomLeftLayoutWidget = QtWidgets.QWidget()
        bottomLeftLayoutWidget.setLayout(bottomLeftLayout)

        ### Populate the bottom layout ###
        # Add items into the main right layout
        bottomLayout.addWidget(bottomLeftLayoutWidget)
        bottomLayout.addWidget(bottomRightLayoutWidget)

        ### Add the items into the layout ###
        # Create the horizontal layout
        layoutMain = QtWidgets.QVBoxLayout()

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
        forecastDetail.setWidget(layoutMainWidget)


    def _createForecastComparisonTabLayout(self, forecastComparison):
        """
        Lays out the forecast comparison tab

        Parameters
        ----------
        None.

        Returns
        -------
        forecastComparison: QT scrollable area


        """

        ### Create the left side forecast cards container ###
        # Create a vertical layout
        leftLayout = QtWidgets.QVBoxLayout()

        self.forecastsPane = forecastList_HTML(self.parent)
        #self.forecastsPane.setFixedWidth(300)
        self.forecastsPane.setContentsMargins(0,0,0,0)

        leftLayout.addWidget(self.forecastsPane)
        leftLayoutWidget = QtWidgets.QWidget()
        leftLayoutWidget.setLayout(leftLayout)

        ### Create the right side forecast visualizer ###
        # Create a vertical layout
        rightLayout = QtWidgets.QVBoxLayout()

        ## Create the main left observed/forecast plot ##
        self.forecastsCharts = ResultsTabPlots(self, xLabel='Percentile', yLabel='Prediction')
        self.forecastsCharts.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        #self.forecastsCharts = QtWidgets.QWidget()

        rightLayout.addWidget(self.forecastsCharts)
        rightLayoutWidget = QtWidgets.QWidget()
        rightLayoutWidget.setLayout(rightLayout)

        ### Add the items into the layout ###
        layoutMain = QtWidgets.QHBoxLayout()
        layoutMain.addWidget(leftLayoutWidget)
        layoutMain.addWidget(rightLayoutWidget)

        ## Add into the scrollable area ##
        layoutMainWidget = QtWidgets.QWidget()
        layoutMainWidget.setLayout(layoutMain)
        forecastComparison.setWidget(layoutMainWidget)


if __name__ == '__main__':
    
    app  = QtWidgets.QApplication(sys.argv)
    mw = QtWidgets.QWidget()
    widg = ForecastsTab(mw)
    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(widg)
    mw.setLayout(layout)
    mw.show()
    sys.exit(app.exec_())