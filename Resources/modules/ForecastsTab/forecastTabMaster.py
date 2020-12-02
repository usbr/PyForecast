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
import tempfile, os, csv

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
        self.forecastsTab.savedForecastsPane.clearForecasts()
        self.forecastsTab.savedForecastsPane.setForecastTable()


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
        self.forecastsTab.exportSavedModelsButton.clicked.connect(self.generateSavedModelsAnalysis)

        # Connect model data year and forecasting actions
        self.forecastsTab.modelYearSpin.valueChanged.connect(self.updateForecastYearData)
        self.forecastsTab.runModelButton.clicked.connect(self.generateModelPrediction)
        self.forecastsTab.saveModelButton.clicked.connect(self.saveModelPrediction)
        self.forecastsTab.exportModelButton.clicked.connect(self.exportModelRun)

        # Connect forecast comparison actions
        self.savedForecastSelectionModel = self.forecastsTab.savedForecastsPane.selectionModel()
        self.savedForecastSelectionModel.selectionChanged.connect(self.generateSavedForecast)

        return


    # ====================================================================================================================
    # FORECAST DETAIL TAB FUNCTIONS
    # <editor-fold desc="Expand Forecast Detail tab functions...">
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
        self.updateStatusMessage('Regenerating model...')
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.forecastsTab.selectedModel = Model(self.forecastsTab.parent, forecastEquationTableEntry)
        self.forecastsTab.selectedModel.equationID = modelIdx
        self.forecastsTab.selectedModel.generate()
        QtWidgets.QApplication.restoreOverrideCursor()

        # Update UI with selected model metadata
        self.forecastsTab.selectedModel.report(self.forecastsTab.resultSelectedList)

        # Update Plots
        self.forecastsTab.resultsObservedForecstPlot.updateScatterPlot(self.forecastsTab.selectedModel.regressionData)

        # Update model run year and table
        self.forecastsTab.modelYearSpin.setRange(self.forecastsTab.selectedModel.years[0], self.forecastsTab.selectedModel.years[-1])
        self.forecastsTab.modelYearSpin.setValue(self.forecastsTab.selectedModel.years[-1])
        self.updateForecastYearData()
        self.forecastsTab.runModelButton.setEnabled(True)
        self.forecastsTab.saveModelButton.setEnabled(False)
        self.updateStatusMessage('')


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
        self.forecastsTab.selectedModelDataTable.loadDataIntoModel(lookupDataTable, rowHeaders=list(lookupDataTable.columns), columnHeaders=list(lookupDataTable.index))


    def savedModelTableRightClick(self, pos):
        if self.forecastsTab.savedModelsTable.view.selectionModel().selection().indexes():
            for i in self.forecastsTab.savedModelsTable.view.selectionModel().selection().indexes():
                row, column = i.row(), i.column()
            menu = QtGui.QMenu()
            deleteAction = menu.addAction("Delete Model")
            action = menu.exec_(self.forecastsTab.savedModelsTable.view.mapToGlobal(pos))
            if action ==deleteAction:
                self.deleteSavedModelAction(row, column)


    def generateSavedModelsAnalysis(self):
        self.forecastsTab.exportSavedModelsButton.setChecked(False)
        modelsTable = self.savedForecastEquationsTable
        self.buildModelAnalysisReport(modelsTable)
        return


    def buildModelAnalysisReport(self, modelsTable):
        if modelsTable.shape[0] < 1:
            return
        print('INFO: Generating model analyis')
        datasetTable = self.datasetTable
        predictorsTable = self.datasetOperationsTable
        # Create dataframe for output
        df = pd.DataFrame(columns=[str(i) for i in predictorsTable.index.values.tolist()])
        df.insert(0, "modelmetric", 0)
        df.insert(0, "modelpreproc", 0)
        df.insert(0, "modelregres", 0)
        df.insert(0, "modelcv", 0)
        df.insert(0, "modelnum", 0)
        # Create metadata rows
        df = df.append(pd.Series(name='colheader'))
        df = df.append(pd.Series(name='predname'))
        df = df.append(pd.Series(name='agency'))
        df = df.append(pd.Series(name='extids'))
        df = df.append(pd.Series(name='units'))
        df = df.append(pd.Series(name='accummethod'))
        df = df.append(pd.Series(name='accumperiod'))
        df = df.append(pd.Series(name='selectcount'))
        df = df.append(pd.Series(name='forcedflag'))
        df = df.append(pd.Series(name='modheader'))
        # Populate predictor metadata cells
        for index, row in predictorsTable.iterrows():
            df.loc['colheader', str(index)] = '|PREDICTOR|'
            df.loc['predname', str(index)] = datasetTable.loc[index[0]].DatasetName + '-' + datasetTable.loc[
                index[0]].DatasetParameter
            df.loc['agency', str(index)] = datasetTable.loc[index[0]].DatasetAgency
            df.loc['extids', str(index)] = datasetTable.loc[index[0]].DatasetExternalID
            df.loc['units', str(index)] = datasetTable.loc[index[0]].DatasetUnits
            df.loc['accummethod', str(index)] = predictorsTable.loc[index].AccumulationMethod
            df.loc['accumperiod', str(index)] = predictorsTable.loc[index].AccumulationPeriod
            df.loc['forcedflag', str(index)] = str(predictorsTable.loc[index].ForcingFlag).lower()
            df.loc['modheader', str(index)] = '|PREDICTOR SELECTED|'
        # Populate predictand metadata cells
        predictandID = modelsTable.loc[0].EquationPredictand
        df.loc['colheader', 'modelpreproc'] = '|PREDICTAND|'
        df.loc['predname', 'modelpreproc'] = datasetTable.loc[predictandID].DatasetName + '-' + datasetTable.loc[
            predictandID].DatasetParameter
        df.loc['agency', 'modelpreproc'] = datasetTable.loc[predictandID].DatasetAgency
        df.loc['extids', 'modelpreproc'] = datasetTable.loc[predictandID].DatasetExternalID
        df.loc['units', 'modelpreproc'] = datasetTable.loc[predictandID].DatasetUnits
        df.loc['accummethod', 'modelpreproc'] = modelsTable.loc[0].PredictandMethod
        df.loc['accumperiod', 'modelpreproc'] = modelsTable.loc[0].PredictandPeriod
        df.loc['accumperiod', 'modelpreproc'] = modelsTable.loc[0].PredictandPeriod
        # Populate model rows
        for index, row in modelsTable.iterrows():
            df = df.append(pd.Series(name=str(index)))
            df.loc[str(index), 'modelnum'] = str(index)
            df.loc[str(index), 'modelpreproc'] = self.preProcessors[row.EquationMethod.split('/')[1]]['name']
            df.loc[str(index), 'modelregres'] = self.regressors[row.EquationMethod.split('/')[2]]['name']
            df.loc[str(index), 'modelcv'] = self.crossValidators[row.EquationMethod.split('/')[3]]['name']
            df.loc[str(index), 'modelmetric'] = str(row.EquationSkill)
            preds = row.EquationPredictors
            predStrings = []
            for pred in preds:
                instanceCounter = 0
                predString = '(' + str(pred) + ', ' + str(instanceCounter) + ')'
                while predString in predStrings:
                    instanceCounter = instanceCounter + 1
                    predString = '(' + str(pred) + ', ' + str(instanceCounter) + ')'
                predStrings.append(predString)
            for predString in predStrings:
                df.loc[str(index), predString] = 1
        # Sum predictor-selected counts
        selCount = df[df == 1].sum()
        selCount['modelnum', 'modelcv', 'modelregres', 'modelpreproc', 'modelmetric'] = [np.nan, np.nan, np.nan, np.nan, np.nan]
        df.loc['selectcount'] = selCount
        # Populate column header labels
        df.loc['colheader', 'modelmetric'] = '|TYPE|'
        df.loc['predname', 'modelmetric'] = '|NAME|'
        df.loc['agency', 'modelmetric'] = '|AGENCY SOURCE|'
        df.loc['extids', 'modelmetric'] = '|AGENCY ID|'
        df.loc['units', 'modelmetric'] = '|UNITS|'
        df.loc['accummethod', 'modelmetric'] = '|ACCUMULATION METHOD|'
        df.loc['accumperiod', 'modelmetric'] = '|ACCUMULATION PERIOD|'
        df.loc['selectcount', 'modelmetric'] = '|SELECTED COUNT|'
        df.loc['forcedflag', 'modelmetric'] = '|PREDICTOR FORCED|'
        # Populate row header labels
        df.loc['modheader', 'modelnum'] = '|MODEL ID|'
        df.loc['modheader', 'modelcv'] = '|MODEL CROSS VALIDATION|'
        df.loc['modheader', 'modelregres'] = '|MODEL REGRESSION|'
        df.loc['modheader', 'modelpreproc'] = '|MODEL PRE-PROCESSOR|'
        df.loc['modheader', 'modelmetric'] = '|MODEL SCORING METRIC(S)|'
        # Write to temp csv file and open
        handle, fn = tempfile.mkstemp(suffix='.csv')
        with os.fdopen(handle, "w", encoding='utf8', errors='surrogateescape', newline='\n') as f:
            try:
                df.to_csv(fn, index=False, header=False)
                print('INFO: Model analysis exported to file ' + fn)
                os.startfile(fn)
            except Exception as e:
                print('WARNING: Model analysis export error:', e)
        print('INFO: Exporting model analyis')
        return


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
        self.updateStatusMessage('Generating prediction...')
        self.forecastsTab.runModelButton.setChecked(False)
        lookupYear = self.forecastsTab.modelYearSpin.value()
        self.forecastsTab.selectedModel.predictionYear = lookupYear
        # Get data from the displayed table
        xData = pd.Series()
        for i in range(len(self.forecastsTab.selectedModelDataTable.dataTable.columns)):
            xData.loc[i] = float(self.forecastsTab.selectedModelDataTable.model.item(1, i).text())
        xData.index = self.forecastsTab.selectedModelDataTable.dataTable.columns
        self.forecastsTab.selectedModel.predict(xData=xData)
        # Get data based on the toggled year
        #self.forecastsTab.selectedModel.predict(year=str(lookupYear))
        self.forecastsTab.resultsObservedForecstPlot.appendForecast(self.forecastsTab.selectedModel.prediction,
                                                                    self.forecastsTab.selectedModel.predictionRange.loc[[10,25,75,90]])
        self.forecastsTab.saveModelButton.setEnabled(True)
        self.updateStatusMessage('')


    def saveModelPrediction(self):
        ### Reset the button state ###
        self.forecastsTab.saveModelButton.setChecked(False)
        print('INFO: Saving prediction. Prediction=' + ('%0.0f' % self.forecastsTab.selectedModel.prediction) +
              ' - Bootstrapped Prediction Range: [10%=' + ('%0.0f' % self.forecastsTab.selectedModel.predictionRange.loc[10]) +
              ', 25%=' + ('%0.0f' % self.forecastsTab.selectedModel.predictionRange.loc[25]) +
              ', 50%=' + ('%0.0f' % self.forecastsTab.selectedModel.predictionRange.loc[50]) +
              ', 75%=' + ('%0.0f' % self.forecastsTab.selectedModel.predictionRange.loc[75]) +
              ', 90%=' + ('%0.0f' % self.forecastsTab.selectedModel.predictionRange.loc[90]) + ']')
        eqID = int(self.forecastsTab.selectedModel.equationID)
        fcastYear = self.forecastsTab.selectedModel.predictionYear
        fcastExc  = 0.5
        fcastIdx = [(eqID, fcastYear, fcastExc)]
        if self.forecastsTable.index.isin(fcastIdx).any():
            self.forecastsTable.drop(fcastIdx, inplace=True)
        self.forecastsTab.selectedModel.predictionRange.loc[-1] = self.forecastsTab.selectedModel.prediction
        self.forecastsTable.loc[eqID,fcastYear,fcastExc]=[self.forecastsTab.selectedModel.predictionRange]


    def exportModelRun(self):
        ### Reset the button state ###
        self.forecastsTab.exportModelButton.setChecked(False)
        print('INFO: Exporting model')
        self.forecastsTab.selectedModel.export()

    # </editor-fold>


    # ====================================================================================================================
    # COMPARE FORECASTS TAB FUNCTIONS
    # <editor-fold desc="Expand Compare Forecasts tab functions...">
    def generateSavedForecast(self):

        self.forecastsTab.savedForecastsCharts.clearPlot()
        selectedSavedForecasts = self.forecastsTab.savedForecastsPane.selectedItems()
        try:
            # Remove non-forecast card items
            nonFcastIdxs = []
            for i in range(len(selectedSavedForecasts)):
                if not hasattr(selectedSavedForecasts[i],'modelID'):
                    nonFcastIdxs.append(i)
            selectedSavedForecasts = [i for j, i in enumerate(selectedSavedForecasts) if j not in nonFcastIdxs]
            boxPlotData = []
            fcastCounter = 10
            for fcast in selectedSavedForecasts:
                # boxPlotData = [  ## fields are (xVal, P50, P25, P75, P10, P90, fcast).
                #     (10, 11, 10, 13, 5, 15, 12),
                #     (20, 15, 13, 17, 9, 20, 14),
                #     ...
                # ]
                boxPlotData.append((int(fcastCounter), fcast.forecastValues.loc[50].values[0],
                                    fcast.forecastValues.loc[25].values[0], fcast.forecastValues.loc[75].values[0],
                                    fcast.forecastValues.loc[10].values[0], fcast.forecastValues.loc[90].values[0],
                                    fcast.forecastValues.loc[-1].values[0]))
                fcastCounter = fcastCounter + 10

            #self.forecastsTab.savedForecastsCharts.appendSavedForecast(fcast.forecastValues, fcast.modelID)
            self.forecastsTab.savedForecastsCharts.appendSavedForecast(boxPlotData)
        except:
            return
    # </editor-fold>


    # ====================================================================================================================
    # TAB CHANGE FUNCTIONS


    def selectedForecastTabChanged(self, tabIndex):
        # todo: doc string
        ### Get the current index the widget has been changed to ###
        #currentIndex = self.workflowWidget.currentIndex()
        #print(tabIndex)

        if tabIndex == 0:
            self.forecastsTab.savedModelsTable.clearTable()
            self.forecastsTab.savedModelsTable.loadDataIntoModel(self.savedForecastEquationsTable)

        if tabIndex == 1:
            self.forecastsTab.savedForecastsPane.clearForecasts()
            self.forecastsTab.savedForecastsPane.setForecastTable()

