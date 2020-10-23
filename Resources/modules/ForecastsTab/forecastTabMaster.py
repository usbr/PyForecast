from datetime import datetime, timedelta
from resources.modules.Miscellaneous import loggingAndErrors
from PyQt5 import QtCore, QtGui, QtWidgets

import pandas as pd
from scipy import stats
import numpy as np
import datetime
from itertools import compress
from dateutil import parser
from statsmodels.tsa.stattools import ccf

from resources.modules.Miscellaneous.generateModel import Model
from resources.GUI.CustomWidgets.SpreadSheet import GenericTableModel
from resources.GUI.CustomWidgets.forecastList_FormattedHTML import forecastList_HTML

class forecastsTab(object):
    """
    FORECAST TAB
    The Forecast Tab contains tools for generating forecasts and hindcasts using saved models
    from the model creation tab.
    """

    def initializeForecastsTab(self):
        """
        Initializes the Tab
        """
        self.connectEventsForecastsTab()

        return

    def resetForecastsTab(self):
        self.forecastsTab.savedModelsTable.clearTable()
        self.forecastsTab.savedModelsTable.loadDataIntoModel(self.savedForecastEquationsTable)
        self.forecastsTab.forecastsPane.clearForecasts()
        self.forecastsTab.forecastsPane.setForecastTable()


        return


    def connectEventsForecastsTab(self):
        """
        Connects all the signal/slot events for the forecasting tab
        """

        # Create an update method for when the tab widget gets changed to refresh elements
        self.forecastsTab.workflowWidget.currentChanged.connect(self.selectedForecastTabChanged)

        # Connect saved model table actions
        self.savedEquationSelectionModel = self.forecastsTab.savedModelsTable.view.selectionModel()
        self.savedEquationSelectionModel.selectionChanged.connect(self.generateSavedModel)
        self.forecastsTab.savedModelsTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.forecastsTab.savedModelsTable.customContextMenuRequested.connect(self.savedModelTableRightClick)

        # Connect model data year and forecasting actions
        self.forecastsTab.modelYearSpin.valueChanged.connect(self.updateForecastYearData)
        self.forecastsTab.runModelButton.clicked.connect(self.generateModelPrediction)


        return

    def generateSavedModel(self, selected, deselected):
        # todo: doc string

        # Get model info
        tableIdx = self.forecastsTab.savedModelsTable.view.selectionModel().currentIndex()
        modelIdx = tableIdx.siblingAtColumn(0).data()
        try:
            forecastEquationTableEntry = self.forecastsTab.parent.savedForecastEquationsTable.loc[int(modelIdx)]
        except:
            return

        # Rebuild model
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.forecastsTab.selectedModel = Model(self.forecastsTab.parent, forecastEquationTableEntry)
        self.forecastsTab.selectedModel.generate()
        QtWidgets.QApplication.restoreOverrideCursor()

        # Update UI with selected model metadata
        self.forecastsTab.resultSelectedList.clear()
        self.forecastsTab.resultSelectedList.addItem('----- MODEL REGRESSION -----')
        self.forecastsTab.resultSelectedList.addItem('Model Index: ' + str(modelIdx))
        self.forecastsTab.resultSelectedList.addItem('Model Processes: ' + str(self.forecastsTab.selectedModel.forecastEquation.EquationMethod))
        self.forecastsTab.resultSelectedList.addItem('Model Predictor IDs: ' + str(self.forecastsTab.selectedModel.forecastEquation.EquationPredictors))
        self.forecastsTab.resultSelectedList.addItem('Range (years): ' + str(self.forecastsTab.selectedModel.trainingDates))
        self.forecastsTab.resultSelectedList.addItem(' ')
        self.forecastsTab.resultSelectedList.addItem('----- MODEL VARIABLES -----')
        self.forecastsTab.resultSelectedList.addItem('Predictand Y: ' + str(self.forecastsTab.parent.datasetTable.loc[self.forecastsTab.selectedModel.yID].DatasetName) + ' - ' + str(self.forecastsTab.parent.datasetTable.loc[self.forecastsTab.selectedModel.yID].DatasetParameter))
        equation = 'Y ='
        hasCoefs = True
        for i in range(len(self.forecastsTab.selectedModel.xIDs)):
            self.forecastsTab.resultSelectedList.addItem('Predictor X' + str(i+1) + ': ' + str(
                self.forecastsTab.parent.datasetTable.loc[self.forecastsTab.selectedModel.xIDs[i]].DatasetName) + ' - ' + str(
                self.forecastsTab.parent.datasetTable.loc[self.forecastsTab.selectedModel.xIDs[i]].DatasetParameter))
            try:
                if hasCoefs:
                    coef = self.forecastsTab.selectedModel.regression.coef[i]
                    const = 'X' + str(i+1)
                    if coef >= 0:
                        equation = equation + ' + (' + ("%0.5f" % coef) + ')' + const
                    else:
                        equation = equation + ' - (' + ("%0.5f" % (coef * -1.0)) + ')' + const
            except:
                hasCoefs = False

        self.forecastsTab.resultSelectedList.addItem(' ')
        if hasCoefs:
            self.forecastsTab.resultSelectedList.addItem('----- MODEL EQUATION -----')
            if self.forecastsTab.selectedModel.regression.intercept >= 0:
                equation = equation + ' + ' + ("%0.5f" % self.forecastsTab.selectedModel.regression.intercept)
            else:
                equation = equation + ' - ' + ("%0.5f" % (self.forecastsTab.selectedModel.regression.intercept * -1.0))
            self.forecastsTab.resultSelectedList.addItem('' + equation)
            self.forecastsTab.resultSelectedList.addItem(' ')
        self.forecastsTab.resultSelectedList.addItem('----- MODEL SCORES (Regular | Cross-Validated) -----')
        for scorer in self.forecastsTab.selectedModel.regression.scoringParameters:
            try:
                regScore = self.forecastsTab.selectedModel.regression.scores[scorer]
                cvScore = self.forecastsTab.selectedModel.regression.cv_scores[scorer]
                self.forecastsTab.resultSelectedList.addItem(scorer + ': ' + ("%0.5f" % regScore) + ' | ' + ("%0.5f" % cvScore))
            except:
                pass

        # Update Plots
        self.forecastsTab.resultsObservedForecstPlot.updateScatterPlot(self.forecastsTab.selectedModel.regressionData)

        # Update model run year and table
        self.forecastsTab.modelYearSpin.setMinimum(self.forecastsTab.selectedModel.years[0])
        self.forecastsTab.modelYearSpin.setMaximum(self.forecastsTab.selectedModel.years[-1])
        self.forecastsTab.modelYearSpin.setValue(self.forecastsTab.selectedModel.years[-1])
        self.updateForecastYearData()


    def updateForecastYearData(self):
        lookupYear = self.forecastsTab.modelYearSpin.value()
        try:
            lookupData = self.forecastsTab.selectedModel.predictorData.loc[int(lookupYear)]
        except:
            return
        remainingData = self.forecastsTab.selectedModel.predictorData.drop(index=lookupYear)
        remainingAvg = remainingData.mean()
        lookupAvg = 100.0 * lookupData / remainingAvg
        remainingPctls = remainingData.quantile([0,.1,.25,.5,.75,.9,1])
        predNames = []
        predIdxs = []
        for i in range(len(self.forecastsTab.selectedModel.xIDs)):
            predNames.append('X' + str(i+1) + ': ' + str(self.forecastsTab.parent.datasetTable.loc[self.forecastsTab.selectedModel.xIDs[i]].DatasetName) + \
                      ' - ' + str(self.forecastsTab.parent.datasetTable.loc[self.forecastsTab.selectedModel.xIDs[i]].DatasetParameter))
            predIdxs.append(self.forecastsTab.selectedModel.xIDs[i])
        preds = pd.Series(predNames, index=predIdxs)
        lookupDataTable = pd.concat([pd.DataFrame(data=[preds, lookupData,lookupAvg,remainingAvg]),remainingPctls])
        lookupDataTable.index = ['Predictor', str(lookupYear) + ' Value', str(lookupYear) + ' Pct-Average','Average','Min', 'P10', 'P25', 'Median', 'P75', 'P90', 'Max']
        self.forecastsTab.selectedModelDataTable.loadDataIntoModel(lookupDataTable, columnHeaders=list(lookupDataTable.index))


    def savedModelTableRightClick(self, pos):
        if self.forecastsTab.savedModelsTable.view.selectionModel().selection().indexes():
            for i in self.forecastsTab.savedModelsTable.view.selectionModel().selection().indexes():
                row, column = i.row(), i.column()
            menu = QtGui.QMenu()
            deleteAction = menu.addAction("Delete Model")
            action = menu.exec_(self.forecastsTab.savedModelsTable.view.mapToGlobal(pos))
            if action ==deleteAction:
                self.deleteSavedModelAction(row, column)


    def deleteSavedModelAction(self, row, column):
        # Get model info
        tableIdx = self.forecastsTab.savedModelsTable.view.selectionModel().currentIndex()
        modelIdx = tableIdx.siblingAtColumn(0).data()
        try:
            # Delete row from  self.forecastsTab.parent.savedForecastEquationsTable
            self.forecastsTab.parent.savedForecastEquationsTable.drop([int(modelIdx)], inplace=True)
            self.resetForecastsTab()
        except:
            return


    def generateModelPrediction(self):
        self.forecastsTab.runModelButton.setChecked(False)
        lookupYear = self.forecastsTab.modelYearSpin.value()
        predValues = self.forecastsTab.selectedModelDataTable.dataTable.loc[str(lookupYear) + ' Value']
        print('-- Generating prediction with values: ---')
        print(predValues)


    def selectedForecastTabChanged(self, tabIndex):
        # todo: doc string
        ### Get the current index the widget has been changed to ###
        #currentIndex = self.workflowWidget.currentIndex()
        #print(tabIndex)

        if tabIndex == 0:
            a=1
            #self.forecastsTab.forecastsPane.clearForecasts()
            #self.forecastsTab.forecastsPane.setForecastTable()

