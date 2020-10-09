from datetime import datetime, timedelta
from resources.modules.Miscellaneous import loggingAndErrors
from PyQt5 import QtCore, QtGui

import pandas as pd
import numpy as np
import datetime
from itertools import compress
from dateutil import parser
from statsmodels.tsa.stattools import ccf

from resources.modules.ModelCreationTab import RegressionWorker
from resources.modules.ModelCreationTab.Operations.Fill import fill_missing
from resources.modules.ModelCreationTab.Operations.Extend import extend

class modelCreationTab(object):
    """
    STATISTICAL MODELS TAB
    The Statistical Models Tab contains tools for creating
    new statistical models (i.e. forecast equations). 
    """

    def initializeModelCreationTab(self):
        """
        Initialize the Tab
        """
        self.connectEventsModelCreationTab()

        return

    def resetModelCreationTab(self):
        #TODO: Need to update the predictor list boxes with what is in the loaded tables
        self.modelTab.summaryListWidget.model().loadDataIntoModel(self.datasetTable, self.datasetOperationsTable)
        for idx, rows in self.datasetOperationsTable.iterrows():
            dsetRow = self.datasetTable.loc[idx[0]]
            self.modelTab.layoutSimpleDoubleList.listOutput.datasetTable.loc[(idx[0], idx[1]), list(self.datasetTable.columns)] = list(dsetRow)

        self.modelTab.layoutDataDoubleList.updateLinkedOperationsTables()
        self.modelTab.layoutSimpleDoubleList.listInput.refreshDatasetList()
        self.modelTab.layoutSimpleDoubleList.listOutput.refreshDatasetList()

        # Emit for the updated linked doublelists
        self.modelTab.layoutSimpleDoubleList.updatedLinkedList.emit(self.modelTab.layoutSimpleDoubleList.listInput, self.modelTab.layoutSimpleDoubleList.listOutput)
        self.modelTab.layoutSimpleDoubleList.updatedOutputList.emit()

        return


    def connectEventsModelCreationTab(self):
        """
        Connects all the signal/slot events for the dataset tab
        """

        ### Setup page level actions ##
        self.modelTab.datasetList.itemPressed.connect(lambda x: self.modelTab.targetSelect.setCurrentIndex(self.modelTab.datasetList.row(x)))
        self.modelTab.targetSelect.currentIndexChanged.connect(lambda x: self.modelTab.targetSelect.hidePopup())
        self.modelTab.targetSelect.currentIndexChanged.connect(lambda x: self.plotTarget() if x >= 0 else None)
        self.modelTab.periodStart.dateChanged.connect(lambda x: self.plotTarget())
        self.modelTab.periodEnd.dateChanged.connect(lambda x: self.plotTarget())
        self.modelTab.methodCombo.currentIndexChanged.connect(lambda x: self.plotTarget())
        self.modelTab.customMethodSpecEdit.editingFinished.connect(self.plotTarget)
        self.modelTab.targetSelect.currentIndexChanged.connect(lambda x: self.modelTab.selectedItemDisplay.setDatasetTable(self.datasetTable.loc[self.modelTab.datasetList.item(x).data(QtCore.Qt.UserRole).name])  if x >= 0 else None)
        self.modelTab.methodCombo.currentIndexChanged.connect(lambda x: self.modelTab.customMethodSpecEdit.show() if self.modelTab.methodCombo.itemData(x) == 'custom' else self.modelTab.customMethodSpecEdit.hide())
        self.modelTab.defButton.toggled.connect(lambda checked: self.updateModelSettings(checked))

        # Create an update method for when the tab widget gets changed to refresh elements
        self.modelTab.workflowWidget.currentChanged.connect(self.updateTabDependencies)


        ### Connect the simple setup page ###
        # Link the doublelist to the output
        # self.modelTab.layoutSimpleDoubleList.listOutput.currentRowChanged.connect(self.updateSimpleLayoutAggregationOptions)
        self.modelTab.layoutSimpleDoubleList.listOutput.itemSelectionChanged.connect(self.updateSimpleLayoutAggregationOptions)

        # Set the button actions
        self.modelTab.layoutSimpleClearButton.clicked.connect(self.applySimpleClear)
        self.modelTab.layoutSimpleApplyButton.clicked.connect(self.applySimpleOptions)

        # Setup the prediction button
        self.modelTab.predictandApplyButton.clicked.connect(self.applyPredictandAggregationOption)


        ### Connect the fill page ###
        # Connect the list widget to the right panel to adjust the display
        self.modelTab.fillList.currentRowChanged.connect(self.updateFillOptionsOnDataset)

        # Link the button to the clear function
        self.modelTab.layoutFillClearButton.clicked.connect(self.applyFillClearToDataset)
        self.modelTab.layoutFillClearButton.clicked.connect(self.updateFillSubtab)

        # Link the button to the apply function
        self.modelTab.layoutFillApplyButton.clicked.connect(self.applyFillOptionsToDataset)

        # Connect the stacked widget with the selection combo box
        self.modelTab.layoutFillMethodSelector.currentIndexChanged.connect(self.updateFillSubtab)


        ### Connect the extend page ###
        # Connect the list widget to the right panel to adjust the display
        self.modelTab.extendList.currentRowChanged.connect(self.updateExtendOptionsOnDataset)

        # Connect the methods selector with the update function
        self.modelTab.layoutExtendMethodSelector.currentIndexChanged.connect(self.updateExtendSubtab)

        # Link the button to the clear function
        self.modelTab.layoutExtendClearButton.clicked.connect(self.applyExtendClearToDataset)
        self.modelTab.layoutExtendClearButton.clicked.connect(self.updateExtendSubtab)

        # Connect the stacked widget with the selection combo box
        self.modelTab.layoutExtendMethodSelector.currentIndexChanged.connect(self.updateExtendSubtab)

        # Link the button to the apply function
        self.modelTab.layoutExtendApplyButton.clicked.connect(self.applyExtendOptionsToDataset)


        ### Connect the window page ###
        # Connect the list widget to the right panel to adjust the display
        self.modelTab.windowList.currentRowChanged.connect(self.updateWindowOptionsOnDataset)

        # Connect the plot widgets together with the plotting routines
        self.modelTab.periodStartWindow.dateChanged.connect(self.updateWindowPlot)
        self.modelTab.periodEndWindow.dateChanged.connect(self.updateWindowPlot)

        # Link the button to the clear function
        self.modelTab.layoutWindowClearButton.clicked.connect(self.applyWindowClearToDataset)

        # Link the button to the apply function
        self.modelTab.layoutWindowApplyButton.clicked.connect(self.applyWindowOptionsToDataset)


        ### Connect the summary page ###
        # Connect the clear button to its action function
        self.modelTab.summaryClearButton.clicked.connect(self.applySummaryClear)

        # Connect the start button to its action function
        self.modelTab.summaryStartButton.clicked.connect(self.applySummaryStart)


        return

    def updateModelSettings(self, defaultSettings):
        """
        This function is run when the user toggles the default model settings
        on the model settings sub-tab. 
        """

        print("DEF SETTINGS")

        return

    def changedTabsModelCreationPage(self, index):
        """
        Handles changing the stacked widget when a user clicks one of the hover 
        labels on the left side.
        """

        for i in range(4):
            if i != index:
                self.modelTab.buttons[i].onDeselect()

        return


    def plotTarget(self):
        """
        Waits for any changes to the forecast target specification
        and updates the plot accordingly. See the connectEvents function
        to figure out when this function is called.
        """

        # Make sure that the forecast target is an actual dataset
        if self.modelTab.targetSelect.currentIndex() < 0:
            return

        # Get the forecast target's internal ID and dataset
        dataset = self.modelTab.datasetList.item(self.modelTab.targetSelect.currentIndex()).data(QtCore.Qt.UserRole)
        datasetID = dataset.name

        # Get the period string
        start = self.modelTab.periodStart.date().toString("1900-MM-dd")
        start_dt = pd.to_datetime(start)
        end = self.modelTab.periodEnd.date().toString("1900-MM-dd")
        end_dt = pd.to_datetime(end)
        length = (end_dt - start_dt).days
        period = 'R/{0}/P{1}D/F12M'.format(start, length)

        # Get the forecast method. If the method is 'custom', get the custom method as well
        method = str(self.modelTab.methodCombo.currentData())
        methodText = str(self.modelTab.methodCombo.currentText()).split('(')[0]

        # Get the units
        units = 'KAF' if 'KAF' in method.upper() else dataset['DatasetUnits']

        if method == 'custom':

            # Get the custom function
            function = self.modelTab.customMethodSpecEdit.text()

            # Check if there is a unit
            if '|' in function:
                units = function.split('|')[1].strip()
                function = function.split('|')[0].strip()

            # Make sure the custom function can evaluate
            x = pd.DataFrame(
                np.random.random((10000,1)),
                index = pd.MultiIndex.from_arrays(
                    [pd.date_range(start=start_dt, periods=10000), 10000*[12013]],
                    names = ['Datetime', 'DatasetInternalID']
                ),
                columns = ['Value']
            )
            x = x.loc[(slice(None), 12013), 'Value']

            try:
                result = eval(function)

            except Exception as e:
                print(e)
                return
            if not isinstance(result, float) and not isinstance(result, int):
                print("result: ", result)
                loggingAndErrors.showErrorMessage(self, "Custom function must evaluate to a floating point number or NaN.")
                return
        else:
            function = None

        # Handle the actual plotting
        self.modelTab.dataPlot.plot.getAxis('left').setLabel(units)
        self.modelTab.dataPlot.displayDatasets(datasetID, period, method, function)

        # Set a title for the plot
        self.modelTab.dataPlot.plot.setTitle('<strong style="font-family: Open Sans, Arial;">{4} {0} - {1} {2} {3}</strong>'.format(start_dt.strftime("%b %d"), end_dt.strftime("%b %d"), methodText.title(), dataset['DatasetParameter'], dataset['DatasetName'] ))

        return


    def autoGeneratePredictors(self):
        """
        Generates default predictors based on the input to the
        previous sections.
        """

        # First verify that all the previous sections have been filled in correctly
        # PLACEHOLDERS
        target = None # DatasetID 
        targetPeriodStart = None # Month-Day combo, e.g.April 1st
        targetPeriodEnd = None # Month-Day combo e.g. July 31st
        forecastIssueDay = None # Month-day combo e.g. Feb 01
        
        # Set up a list to store the suggestions
        suggestedPredictors = []

        # Iterate over the datasetlist and add each predictors default resampling
        # method for the prior period
        for i, dataset in self.datasetTable.iterrows():

            # Pull the default resampling method
            method = dataset['DatasetDefaultResampling']

            # Check dataset parameter, we'll use this to generate the resample period
            if any(map(lambda x: x in dataset['DatasetParameter'].upper(), ['SWE', 'SNOW'])): 
                period = 'R/{0}/P1D/F1Y'.format(datetime.strftime(forecastIssueDay - timedelta(days=1), '%Y-%m-%d'))

            elif any(map(lambda x: x in dataset['DatasetParameter'].upper(), ['TEMP', 'INDEX'])):
                period = 'R/{0}/P28D/F1Y'.format(datetime.strftime(forecastIssueDay - timedelta(weeks=4), '%Y-%m-%d'))
            
            elif any(map(lambda x: x in dataset['DatasetParameter'].upper(), ['PRECIP'])):
                wyStart = datetime(forecastIssueDay.year if forecastIssueDay.month > 10 else forecastIssueDay.year - 1, 10, 1)
                period = 'R/{0}/P{1}D/F1Y'.format(datetime.strftime(wyStart, '%Y-%m-%d'), (forecastIssueDay - wyStart).days - 1)
            
            elif  any(map(lambda x: x in dataset['DatasetParameter'].upper(), ['FLOW'])): 
                wyStart = datetime(forecastIssueDay.year if forecastIssueDay.month > 10 else forecastIssueDay.year - 1, 10, 1)
                period = 'R/{0}/P1M/F1Y'.format(datetime.strftime(wyStart, '%Y-%m-%d'))

            suggestedPredictors.append((dataset.name, method, period)) 

        # Add the predictors to the GUI
        

        return

    def updateSimpleLayoutAggregationOptions(self):
        #todo: doc string

        if len(self.modelTab.layoutSimpleDoubleList.listOutput.selectedIndexes()) > 0:
            # Get the current datasest index
            currentIndex = self.modelTab.layoutSimpleDoubleList.listOutput.datasetTable.index[self.modelTab.layoutSimpleDoubleList.listOutput.currentIndex().row()]

            # Get the current dataset and operations settings
            datasetInfo = self.modelTab.fillList.datasetTable.loc[currentIndex]["DatasetName"] + " - " + \
                          self.modelTab.fillList.datasetTable.loc[currentIndex]["DatasetParameter"] + " " + \
                          str(self.modelTab.fillList.datasetTable.loc[currentIndex].name)
            accumMethod = str(self.datasetOperationsTable.loc[currentIndex]['AccumulationMethod'])
            accumPeriod = str(self.datasetOperationsTable.loc[currentIndex]['AccumulationPeriod'])
            predForcing = str(self.datasetOperationsTable.loc[currentIndex]['ForcingFlag'])

            # Update the dataset list with the single display option
            self.modelTab.layoutAggregationOptions.activeSelection.refreshDatasetListFromExtenal(self.modelTab.layoutSimpleDoubleList.listOutput.datasetTable.loc[currentIndex])

            self.modelTab.layoutAggregationOptions.aggLabel2.setText("     Accumulation Method: " + accumMethod)
            self.modelTab.layoutAggregationOptions.aggLabel3.setText("     Accumulation Period: " + accumPeriod)
            self.modelTab.layoutAggregationOptions.aggLabel4.setText("     Forced Flag: " + predForcing)

            # Set date selector range
            minT = parser.parse(str(np.sort(list(set(self.dataTable.loc[(slice(None),currentIndex[0]),'Value'].index.get_level_values(0).values)))[0]))
            maxT = parser.parse(str(np.sort(list(set(self.dataTable.loc[(slice(None),currentIndex[0]),'Value'].index.get_level_values(0).values)))[-1]))
            self.modelTab.layoutAggregationOptions.periodStart.minimumDate = minT
            self.modelTab.layoutAggregationOptions.periodStart.maximumDate = maxT
            self.modelTab.layoutAggregationOptions.periodStart.setDate(minT)

            # Set aggregation option on UI
            if accumMethod == 'None':
                self.modelTab.layoutAggregationOptions.aggLabel2.setStyleSheet("color : red")
                # Get default resampling method
                defResampling = self.datasetTable.loc[self.datasetOperationsTable.loc[currentIndex].name[0]]['DatasetDefaultResampling']
                defIdx = self.modelTab.layoutAggregationOptions.predictorAggregationOptions.index(defResampling)
                self.modelTab.layoutAggregationOptions.radioButtons.button(defIdx).setChecked(True)
            else: #set defined aggregation scheme
                self.modelTab.layoutAggregationOptions.aggLabel2.setStyleSheet("color : green")
                defIdx = self.modelTab.layoutAggregationOptions.predictorAggregationOptions.index(accumMethod)
                self.modelTab.layoutAggregationOptions.radioButtons.button(defIdx).setChecked(True)

            # Set aggregation period on UI
            if accumPeriod == 'None':
                self.modelTab.layoutAggregationOptions.aggLabel3.setStyleSheet("color : red")
            else: #set defined resampling period options
                self.modelTab.layoutAggregationOptions.aggLabel3.setStyleSheet("color : green")
                predPeriodItems = accumPeriod.split("/") #R/1978-03-01/P1M/F12M
                self.modelTab.layoutAggregationOptions.periodStart.setDate(parser.parse(predPeriodItems[1]))
                predPeriodPStep = str(predPeriodItems[2])[-1]
                a = self.modelTab.layoutAggregationOptions.predictorResamplingOptions.index(predPeriodPStep)
                self.modelTab.layoutAggregationOptions.tStepChar.setCurrentIndex(self.modelTab.layoutAggregationOptions.predictorResamplingOptions.index(predPeriodPStep))
                predPeriodPNum = ''.join(map(str,[int(s) for s in predPeriodItems[2] if s.isdigit()]))
                self.modelTab.layoutAggregationOptions.tStepInteger.setValue(int(predPeriodPNum))
                predPeriodFStep = str(predPeriodItems[3])[-1]
                self.modelTab.layoutAggregationOptions.freqChar.setCurrentIndex(self.modelTab.layoutAggregationOptions.predictorResamplingOptions.index(predPeriodFStep))
                predPeriodFNum = ''.join(map(str,[int(s) for s in predPeriodItems[3] if s.isdigit()]))
                self.modelTab.layoutAggregationOptions.freqInteger.setValue(int(predPeriodFNum))

            # Set forcing flag on UI
            if predForcing == 'None':
                self.modelTab.layoutAggregationOptions.aggLabel4.setStyleSheet("color : red")
            else: #set defined forcing flag
                self.modelTab.layoutAggregationOptions.aggLabel4.setStyleSheet("color : green")
                self.modelTab.layoutAggregationOptions.predForceCheckBox.setChecked(predForcing == 'True')
        else:
            self.modelTab.layoutAggregationOptions.activeSelection.refreshDatasetListFromExtenal(None)
            self.modelTab.layoutAggregationOptions.aggLabel2.setText("     Accumulation Method: NA")
            self.modelTab.layoutAggregationOptions.aggLabel3.setText("     Accumulation Period: NA")
            self.modelTab.layoutAggregationOptions.aggLabel4.setText("     Forced Flag: NA")

        self.modelTab.layoutAggregationOptions.resamplingUpdate()

    def applySimpleOptions(self):
        """
        Applies the attributes from the simple predictor page into the dataset operations table

        """
        # todo: write this function when the aggregation group is stable

        # Clear the button click
        self.modelTab.layoutSimpleApplyButton.setChecked(False)

        # Get the current datasest index
        rowIdx = self.modelTab.layoutSimpleDoubleList.listOutput.currentIndex().row()

        if rowIdx >= 0:

            currentIndex = self.modelTab.layoutSimpleDoubleList.listOutput.datasetTable.index[rowIdx]

            # Apply selected options
            self.datasetOperationsTable.loc[currentIndex]['AccumulationMethod'] = \
                self.modelTab.layoutAggregationOptions.selectedAggOption
            self.datasetOperationsTable.loc[currentIndex]['AccumulationDateStart'] = \
                self.modelTab.layoutAggregationOptions.periodStart.dateTime().toString("yyyy-MM-dd")
            self.datasetOperationsTable.loc[currentIndex]['AccumulationDateStop'] = \
                (parser.parse(str(np.sort(list(set(self.dataTable.loc[(slice(None),currentIndex[0]),'Value'].index.get_level_values(0).values)))[-1]))).strftime("%Y-%m-%d")
            self.datasetOperationsTable.loc[currentIndex]['AccumulationPeriod'] = \
                self.modelTab.layoutAggregationOptions.selectedAggPeriod
            self.datasetOperationsTable.loc[currentIndex]['ForcingFlag'] = \
                str(self.modelTab.layoutAggregationOptions.predForceCheckBox.checkState() == 2)

        self.updateSimpleLayoutAggregationOptions()

    def applySimpleClear(self):
        """
        Clears the fill attributes of a predictor

        """

        # Drop all rows in the dataset operations table
        self.datasetOperationsTable.drop(self.datasetOperationsTable.index, inplace=True)

        # Reset the output table
        self.modelTab.layoutSimpleDoubleList.resetOutputItems()

        # Clear the checkboxes
        self.modelTab.layoutSimpleExtend.updateToUnchecked()
        self.modelTab.layoutSimpleFill.updateToUnchecked()

        # Clear the aggregation options
        # todo: Add this functionality

        ### Reset the button state ###
        self.modelTab.layoutSimpleClearButton.setChecked(False)

    def updateFillSubtab(self):
        """
        Updates the state of the fill subtab methods pane based on the method selector

        """

        ### Update the widget pane ###
        # Switch the stacked widgets
        self.modelTab.stackedFillLayout.setCurrentIndex(self.layoutFillMethodSelector.currentIndex())

        # Update the gap limit visibility
        if self.modelTab.layoutFillMethodSelector.currentIndex() > 0:
            self.modelTab.layoutFillGapLimitLabel.setVisible(True)
            self.modelTab.layoutFillGapLimit.setVisible(True)
        else:
            self.modelTab.layoutFillGapLimitLabel.setVisible(False)
            self.modelTab.layoutFillGapLimit.setVisible(False)

        if self.modelTab.layoutFillMethodSelector.currentIndex() >= 5:
            self.modelTab.layoutFillOrderLabel.setVisible(True)
            self.modelTab.layoutFillOrder.setVisible(True)
        else:
            self.modelTab.layoutFillOrderLabel.setVisible(False)
            self.modelTab.layoutFillOrder.setVisible(False)

    def updateFillOptionsOnDataset(self):
        """
        Displays the correct information for the selected dataset in the fill pane

        """

        # Get the current datasest index
        currentIndex = self.modelTab.fillList.datasetTable.index[self.modelTab.fillList.currentIndex().row()]

        ### Update the widgets with dataset information ###
        # Get the options for the item
        fillMethod = self.datasetOperationsTable.loc[currentIndex]['FillMethod']
        fillGap = self.datasetOperationsTable.loc[currentIndex]['FillMaximumGap']
        fillOrder = self.datasetOperationsTable.loc[currentIndex]['FillOrder']
        # If needed, can extract more information based on the fill method here

        # Get the options for the selector and stack
        fillOptionsIndex = [x for x in range(self.modelTab.layoutFillMethodSelector.count())
                            if self.modelTab.layoutFillMethodSelector.itemText(x) == fillMethod]
        if fillOptionsIndex:
            fillOptionsIndex = fillOptionsIndex[0]
        else:
            fillOptionsIndex = 0

        # Get the fill order index
        fillOrderIndex = [x for x in range(self.modelTab.layoutFillOrder.count())
                          if self.modelTab.layoutFillOrder.itemText(x) == str(fillOrder)]
        if fillOrderIndex:
            fillOrderIndex = fillOrderIndex[0]
        else:
            fillOrderIndex = 0

        # Set the values into the widgets
        self.modelTab.stackedFillLayout.setCurrentIndex(fillOptionsIndex)
        self.modelTab.layoutFillMethodSelector.setCurrentIndex(fillOptionsIndex)
        self.modelTab.layoutFillOrder.setCurrentIndex(fillOrderIndex)

        # Set the values into the widgets
        # Correct this issue
        self.modelTab.layoutFillGapLimit.setText(str(fillGap))

        ### Update the plot with the dataset and interpolation ###
        self.updateFillPlot(currentIndex, fillMethod, fillGap, fillOrder)

    def applyFillOptionsToDataset(self):
        """
        Applies the fill attributes to a dataset

        """

        # Extract the fill limit
        try:
            fillLimit = int(self.modelTab.layoutFillGapLimit.text())
        except:
            fillLimit = None

        # Get the method to be utilized
        fillMethod = self.modelTab.layoutFillMethodSelector.currentText()

        # Get the order
        fillOrder = int(self.modelTab.layoutFillOrder.currentText())

        # Get the current dataset
        currentIndex = self.modelTab.fillList.datasetTable.index[self.fillList.currentIndex().row()]

        # Set the values
        self.datasetOperationsTable.loc[currentIndex]['FillMethod'] = fillMethod
        self.datasetOperationsTable.loc[currentIndex]['FillMaximumGap'] = fillLimit
        self.datasetOperationsTable.loc[currentIndex]['FillOrder'] = fillOrder

        # Clear the button click
        self.modelTab.modelTab.layoutFillApplyButton.setChecked(False)

        # Update the plot on the tab
        self.updateFillPlot(currentIndex, fillMethod, fillLimit, fillOrder)

    def applyFillClearToDataset(self):
        """
        Clears the fill attributes of a dataset

        """

        # Get the current dataset
        currentIndex = self.modelTab.fillList.datasetTable.index[self.modelTab.fillList.currentIndex().row()]

        # Set the values
        self.datasetOperationsTable.loc[currentIndex]['FillMethod'] = None
        self.datasetOperationsTable.loc[currentIndex]['FillMaximumGap'] = None
        self.datasetOperationsTable.loc[currentIndex]['FillOrder'] = None

        # Clear the button click
        self.modelTab.layoutFillClearButton.setChecked(False)

        # Switch the stacked widgets
        self.modelTab.layoutFillMethodSelector.setCurrentIndex(0)
        self.updateFillSubtab()

    def updateFillPlot(self, currentIndex, fillMethod, fillLimit, fillOrder):
        """
        Updates the plot on the fill subtab

        Parameters
        ----------
        currentIndex: pandas index
            Index which specifies the active dataset
        fillMethod: str
            Fill method specified to fill the gaps
        fillLimit: int
            Maximum size of gap to fill via interpolation
        fillOrder: int
            Order of the fill method, if applicable

        """

        ### Update the plot with the dataset and interpolation ###
        # Get the source and fill dataset. This copies it to avoid changing the source data
        sourceData = self.dataTable.loc[(slice(None), currentIndex), 'Value']
        sourceData = sourceData.droplevel('DatasetInternalID')
        sourceUnits = self.datasetTable.loc[currentIndex[0]]['DatasetUnits']

        if fillMethod is not None and fillMethod != 'None':
            # Fill the data with the applied operation
            filledData = fill_missing(sourceData, fillMethod.lower(), fillLimit, order=fillOrder)

            # Promote and set the status of the filled data
            fillData = pd.DataFrame(filledData)
            fillData['Status'] = 'Filled'
            fillData.set_index(['Status'], append=True, inplace=True)

            # Promote and set the status of the source data
            sourceData = pd.DataFrame(sourceData)
            sourceData['Status'] = 'Not Filled'
            sourceData.set_index(['Status'], append=True, inplace=True)

            # Stack it together with the existing data
            sourceData = pd.concat([fillData, sourceData]).sort_index()

        else:
            # No filled data is present. Promote back to a dataframe and add the plotting label
            sourceData = pd.DataFrame(sourceData)
            sourceData['Status'] = 'Not Filled'

            # Convert to a multiinstance table
            sourceData.set_index(['Status'], append=True, inplace=True)

        ## Plot the source dataset ##
        self.modelTab.layoutFillPlot.updateData(sourceData, 'Status', sourceUnits)
        self.modelTab.layoutFillPlot.displayDatasets()

    def updateExtendSubtab(self):
        """
        Updates the state of the extend subtab methods pane based on the method selector

        """

        ### Switch the stacked widgets ###
        self.modelTab.stackedExtendLayout.setCurrentIndex(self.layoutExtendMethodSelector.currentIndex())

        ### Set all options to false and reenable if active ###
        ## Linear widgets ##
        self.modelTab.layoutExtendLinearDurationLabel.setVisible(False)
        self.modelTab.layoutExtendLinearDurationLimit.setVisible(False)

        ## Fourier widgets ##
        self.modelTab.layoutExtendFourierDurationLabel.setVisible(False)
        self.modelTab.layoutExtendFourierDurationLimit.setVisible(False)
        self.modelTab.layoutExtendFourierFilterLabel.setVisible(False)
        self.modelTab.layoutExtendFourierFilter.setVisible(False)

        # Update the gap limit visibility
        if self.modelTab.layoutExtendMethodSelector.currentIndex() == 1:
            # Update visibility for the linear option
            self.modelTab.layoutExtendLinearDurationLabel.setVisible(True)
            self.modelTab.layoutExtendLinearDurationLimit.setVisible(True)

        elif self.modelTab.layoutExtendMethodSelector.currentIndex() == 2:
            # Update visibility for the fourier option
            self.modelTab.layoutExtendFourierDurationLabel.setVisible(True)
            self.modelTab.layoutExtendFourierDurationLimit.setVisible(True)
            self.modelTab.layoutExtendFourierFilterLabel.setVisible(True)
            self.modelTab.layoutExtendFourierFilter.setVisible(True)

    def updateExtendOptionsOnDataset(self):
        """
        Displays the correct information for the selected dataset in the fill pane

        """

        # Get the current datasest index
        currentIndex = self.modelTab.extendList.datasetTable.index[self.modelTab.extendList.currentIndex().row()]

        # Get the options for the item
        extendMethod = self.datasetOperationsTable.loc[currentIndex]['ExtendMethod']
        extendDuration = self.datasetOperationsTable.loc[currentIndex]['ExtendDuration']
        extendFilter = self.datasetOperationsTable.loc[currentIndex]['ExtendFilter']

        # Get the options for the selector and stack
        extendOptionsIndex = [x for x in range(self.layoutExtendMethodSelector.count()) if self.layoutExtendMethodSelector.itemText(x) == extendMethod]
        if extendOptionsIndex:
            extendOptionsIndex = extendOptionsIndex[0]
        else:
            extendOptionsIndex = 0

        # Toggle the stack to the correct display
        self.modelTab.stackedExtendLayout.setCurrentIndex(extendOptionsIndex)

        # Toggle the method selector to the correct display
        self.modelTab.layoutExtendMethodSelector.setCurrentIndex(extendOptionsIndex)

        # Set the options based on set option
        if extendOptionsIndex == 1:
            # Set the linear options
            self.modelTab.layoutExtendLinearDurationLimit.setText(str(extendDuration))

        elif extendOptionsIndex == 2:
            # Set the fourier options
            self.modelTab.layoutExtendFourierDurationLimit.setText(str(extendMethod))

            if extendFilter == 'Day':
                self.modelTab.layoutExtendFourierFilter.setCurrentIndex(0)
            if extendFilter == 'Week':
                self.modelTab.layoutExtendFourierFilter.setCurrentIndex(1)
            if extendFilter == 'Month':
                self.modelTab.layoutExtendFourierFilter.setCurrentIndex(2)
            if extendFilter == 'Year':
                self.modelTab.layoutExtendFourierFilter.setCurrentIndex(3)

        # Update the plot on the tab
        self.updateExtendPlot(currentIndex, extendMethod, extendDuration, extendFilter)

    def applyExtendOptionsToDataset(self):
        """
        Applies the fill attributes to a dataset

        """

        ### Extract the data from the GUI ###
        # Get the method to be utilized
        extendMethod = self.modelTab.layoutExtendMethodSelector.currentText()

        # Parse the output based on the method
        if extendMethod == 'Linear':
            # Extract the information from the linear stack
            extendLimit = int(self.modelTab.layoutExtendLinearDurationLimit.text())
            extendFilter = None

        elif extendMethod == 'Fourier':
            # Extract the information from the fourier stack
            extendLimit = int(self.modelTab.layoutExtendFourierDurationLimit.text())
            extendFilter = self.modelTab.layoutExtendFourierFilter.currentText()

        # Get the current dataset
        currentIndex = self.modelTab.extendList.datasetTable.index[self.extendList.currentIndex().row()]

        ### Determine if a fill has been added to the data ###
        if self.datasetOperationsTable.loc[currentIndex]['FillMethod'] is not None:
            # Set the values
            self.datasetOperationsTable.loc[currentIndex]['ExtendMethod'] = extendMethod
            self.datasetOperationsTable.loc[currentIndex]['ExtendDuration'] = extendLimit
            self.datasetOperationsTable.loc[currentIndex]['ExtendFilter'] = extendLimit

            # Update the plot on the tab
            self.updateExtendPlot(currentIndex, extendMethod, extendLimit, extendFilter)

        # Clear the button click
        self.modelTab.layoutExtendApplyButton.setChecked(False)

    def applyExtendClearToDataset(self):
        """
        Clears the fill attributes of a dataset

        """

        # Get the current dataset
        currentIndex = self.modelTab.extendList.datasetTable.index[self.modelTab.extendList.currentIndex().row()]

        # Set the values
        self.datasetOperationsTable.loc[currentIndex]['ExtendMethod'] = None
        self.datasetOperationsTable.loc[currentIndex]['ExtendDuration'] = None
        self.datasetOperationsTable.loc[currentIndex]['ExtendFilter'] = None

        # Clear the button click
        self.modelTab.layoutFillClearButton.setChecked(False)

        # # Switch the stacked widgets
        self.modelTab.layoutExtendMethodSelector.setCurrentIndex(0)
        self.updateExtendSubtab()

    def updateExtendPlot(self, currentIndex, extendMethod, extendLimit, extendFilter):
        """
        Updates the plot on the extend subtab

        Parameters
        ----------
        currentIndex: pandas index
            Index which specifies the active dataset
        extendMethod: str
            Fill method specified to extend the series
        extendLimit: int
            Extension period

        """

        ### Update the plot with the dataset and interpolation ###
        # Get the source and fill dataset. This copies it to avoid changing the source data
        sourceData = self.dataTable.loc[(slice(None), currentIndex), 'Value']
        sourceData = sourceData.droplevel('DatasetInternalID')
        sourceUnits = self.datasetTable.loc[currentIndex[0]]['DatasetUnits']

        ### Extract the data from the fill chart ###
        fillMethod = self.datasetOperationsTable.loc[currentIndex]['FillMethod']
        fillDuration = self.datasetOperationsTable.loc[currentIndex]['FillMaximumGap']
        fillOrder = self.datasetOperationsTable.loc[currentIndex]['FillOrder']

        if extendMethod is not None and extendMethod != 'None':
            # Fill the data with the applied operation
            extendedData, lostDensity = extend(sourceData, fillMethod.lower(), fillDuration, fillOrder,
                                               extendMethod.lower(), extendLimit, extendFilter)

            # Promote and set the status of the filled data
            extendedData = pd.DataFrame(extendedData)
            extendedData['Status'] = 'Extended'
            extendedData.set_index(['Status'], append=True, inplace=True)

            # Promote and set the status of the source data
            sourceData = pd.DataFrame(sourceData)
            sourceData['Status'] = 'Not Extended'
            sourceData.set_index(['Status'], append=True, inplace=True)

            # Stack it together with the existing data
            sourceData = pd.concat([extendedData, sourceData]).sort_index()

        else:
            # No filled data is present. Promote back to a dataframe and add the plotting label
            sourceData = pd.DataFrame(sourceData)
            sourceData['Status'] = 'Not Extended'

            # Convert to a multiinstance table
            sourceData.set_index(['Status'], append=True, inplace=True)

        ## Plot the source dataset ##
        self.modelTab.layoutExtendPlot.updateData(sourceData, 'Status', sourceUnits)
        self.modelTab.layoutExtendPlot.displayDatasets()

    def updateWindowOptionsOnDataset(self):
        """
        Displays the correct information for the selected dataset in the window pane

        """

        # Get the current datasest index
        currentIndex = self.modelTab.windowList.datasetTable.index[self.windowList.currentIndex().row()]

        # Get the current dataset and operations settings
        datasetInfo = self.modelTab.windowList.datasetTable.loc[currentIndex]["DatasetName"] + " - " + \
                      self.modelTab.windowList.datasetTable.loc[currentIndex]["DatasetParameter"] + " " + \
                      str(self.modelTab.windowList.datasetTable.loc[currentIndex].name)
        accumMethod = str(self.datasetOperationsTable.loc[currentIndex]['AccumulationMethod'])
        accumPeriod = str(self.datasetOperationsTable.loc[currentIndex]['AccumulationPeriod'])
        predForcing = str(self.datasetOperationsTable.loc[currentIndex]['ForcingFlag'])

        # Set date selector range
        minT = parser.parse(str(np.sort(list(set(self.dataTable.loc[(slice(None),currentIndex[0]),'Value'].index.get_level_values(0).values)))[0]))
        maxT = parser.parse(str(np.sort(list(set(self.dataTable.loc[(slice(None),currentIndex[0]),'Value'].index.get_level_values(0).values)))[-1]))
        self.modelTab.layoutWindowAggregationGroup.periodStart.minimumDate = minT
        self.modelTab.layoutWindowAggregationGroup.periodStart.maximumDate = maxT
        self.modelTab.layoutWindowAggregationGroup.periodStart.setDate(minT)

        # Set aggregation option on UI
        if accumMethod != 'None':
            defIdx = self.modelTab.layoutWindowAggregationGroup.predictorAggregationOptions.index(accumMethod)
            self.modelTab.layoutWindowAggregationGroup.radioButtons.button(defIdx).setChecked(True)

        # Set aggregation period on UI
        if accumPeriod != 'None':
            predPeriodItems = accumPeriod.split("/") #R/1978-03-01/P1M/F12M
            self.modelTab.layoutWindowAggregationGroup.periodStart.setDate(parser.parse(predPeriodItems[1]))
            predPeriodPStep = str(predPeriodItems[2])[-1]
            a = self.modelTab.layoutWindowAggregationGroup.predictorResamplingOptions.index(predPeriodPStep)
            self.modelTab.layoutWindowAggregationGroup.tStepChar.setCurrentIndex(self.layoutWindowAggregationGroup.predictorResamplingOptions.index(predPeriodPStep))
            predPeriodPNum = ''.join(map(str,[int(s) for s in predPeriodItems[2] if s.isdigit()]))
            self.modelTab.layoutWindowAggregationGroup.tStepInteger.setValue(int(predPeriodPNum))
            predPeriodFStep = str(predPeriodItems[3])[-1]
            self.modelTab.layoutWindowAggregationGroup.freqChar.setCurrentIndex(self.layoutWindowAggregationGroup.predictorResamplingOptions.index(predPeriodFStep))
            predPeriodFNum = ''.join(map(str,[int(s) for s in predPeriodItems[3] if s.isdigit()]))
            self.modelTab.layoutWindowAggregationGroup.freqInteger.setValue(int(predPeriodFNum))

        # Set forcing flag on UI
        if predForcing != 'None':
            self.modelTab.layoutWindowAggregationGroup.predForceCheckBox.setChecked(predForcing == 'True')

        self.modelTab.layoutWindowAggregationGroup.resamplingUpdate()

        # Update the plot
        self.updateWindowPlot()

    def applyWindowOptionsToDataset(self):
        """
        Applies the fill attributes to a dataset

        """

        # Get the current active index
        currentIndex = self.modelTab.windowList.datasetTable.index[self.modelTab.windowList.currentIndex().row()]

        # Apply the attributes into the data table
        self.datasetOperationsTable.loc[currentIndex]['AccumulationMethod'] = \
            self.modelTab.layoutWindowAggregationGroup.selectedAggOption
        self.datasetOperationsTable.loc[currentIndex]['AccumulationDateStart'] = \
            self.modelTab.layoutWindowAggregationGroup.periodStart.dateTime().toString("yyyy-MM-dd")
        self.datasetOperationsTable.loc[currentIndex]['AccumulationDateStop'] = \
            (parser.parse(str(np.sort(list(set(self.dataTable.loc[(slice(None), currentIndex[0]), 'Value'].index.get_level_values(0).values)))[-1]))).strftime("%Y-%m-%d")
        self.datasetOperationsTable.loc[currentIndex]['AccumulationPeriod'] = \
            self.modelTab.layoutWindowAggregationGroup.selectedAggPeriod
        self.datasetOperationsTable.loc[currentIndex]['ForcingFlag'] = \
            str(self.modelTab.layoutWindowAggregationGroup.predForceCheckBox.checkState() == 2)

        # Set the button to clear
        self.modelTab.layoutWindowApplyButton.setChecked(False)

    def applyWindowClearToDataset(self):
        """
        Clears the window attributes of a dataset

        """

        # Get the current dataset
        currentIndex = self.modelTab.windowList.datasetTable.index[self.modelTab.extendList.currentIndex().row()]

        # Set the values
        self.datasetOperationsTable.loc[currentIndex]['AccumulationMethod'] = None
        self.datasetOperationsTable.loc[currentIndex]['AccumulationDateStart'] = None
        self.datasetOperationsTable.loc[currentIndex]['AccumulationDateStop'] = None
        self.datasetOperationsTable.loc[currentIndex]['AccumulationPeriod'] = None
        self.datasetOperationsTable.loc[currentIndex]['ForcingFlag'] = None

        # Clear the button click
        self.modelTab.layouWindowClearButton.setChecked(False)

    def updateWindowPlot(self):
        """
        Updates the plot within the window subtab

        """

        ### Get the data from the widgets ###
        startDate = self.modelTab.periodStartWindow.dateTime().toPyDateTime()
        endDate = self.modelTab.periodEndWindow.dateTime().toPyDateTime()
        numberOfDays = (endDate - startDate).days + 1

        ### Push the number of days back into the widget ###
        self.modelTab.layoutWindowLagLimit.setText(str(numberOfDays))

        ### Update the plot with the dataset and interpolation ###
        # Get the source and fill dataset. This copies it to avoid changing the source data
        currentIndex = self.modelTab.windowList.datasetTable.index[self.modelTab.windowList.currentIndex().row()]
        sourceData = self.dataTable.loc[(slice(None), currentIndex), 'Value']
        sourceData = sourceData.droplevel('DatasetInternalID')
        sourceUnits = self.datasetTable.loc[currentIndex[0]]['DatasetUnits']

        # Extract the target dataset
        targetData = self.dataTable.loc[(slice(None), self.targetSelect.currentData().name), 'Value']
        targetData = targetData.droplevel('DatasetInternalID')
        targetUnits = self.datasetTable.loc[self.targetSelect.currentData().name]['DatasetUnits']

        # Window the data between the start and end dates
        sourceData = sourceData[startDate:endDate]
        targetData = targetData[startDate:endDate]

        # Calculate the correlation based on the lag
        if startDate <= endDate:
            # Start date is before the end date, so lag is positive. Calculate a nonzero correlation to display.
            # Cross correlation between the source and target datasets
            correlation = ccf(targetData.values, sourceData.values)

        else:
            # Start date is after the end date, so the lag is negative. Return a zero correlation
            correlation = np.zeros((numberOfDays, 2))
            correlation[:, 0] = np.arange(np.abs(numberOfDays))
            correlation[:, 1] = np.zeros(np.abs(numberOfDays))

        # Add some random data to test
        self.modelTab.layoutWindowPlot.clear()

        # Create the x axis labels
        categories = [str(x) for x in correlation[:, 0]]

        # Set the correlation into the plot as a bar series
        self.modelTab.layoutWindowPlot.createBarPlotItem('Correlation', correlation)

        # Add some random timeseries data
        self.modelTab.layoutWindowPlot.createLinePlotItem('Predictor', sourceData, categories)
        self.modelTab.layoutWindowPlot.createLinePlotItem('Target', targetData, categories)

        # Set the bar categories
        self.modelTab.layoutWindowPlot.setBarCategories(categories)

        # Plot the data
        self.modelTab.layoutWindowPlot.plot()

    def applySummaryClear(self):
        """
        Clear/reset all dataset and analysis options within the application

        """

        ### Reset the dataset operations table ###
        # Drop all rows in the tables
        self.modelRunsTable.drop(self.modelRunsTable.index, inplace=True)
        self.datasetOperationsTable.drop(self.datasetOperationsTable.index, inplace=True)

        # Update the table display elements
        self.modelTab.summaryListWidget.model().loadDataIntoModel(self.datasetTable, self.datasetOperationsTable)

        ### Reset all processing options ###
        # Reset the cross validation operations
        for x in self.modelTab.optionsCrossValidators:
            x.updateToUnchecked()

        # Reset the preprocessing operations
        for x in self.modelTab.optionsPreprocessor:
            x.updateToUnchecked()

        # Reset the regression options
        for x in self.modelTab.optionsRegression:
            x.updateToUnchecked()

        # Reset the selection options
        for x in self.modelTab.optionsSelection:
            x.updateToUnchecked()

        # Reset the scoring operations
        for x in self.modelTab.optionsScoring:
            x.updateToUnchecked()

        ### Reset the button state ###
        self.modelTab.summaryClearButton.setChecked(False)
        self.updateTabDependencies(3)

        ### Emit change to the doublelist object ###
        self.modelTab.layoutSimpleDoubleList.resetOutputItems()


    def applySummaryStart(self):
        """
        Start the regression analysis using the specified settings

        """

        ### Reset the button state ###
        self.modelTab.summaryStartButton.setChecked(False)
        errorString = 'Model Errors: '

        ### Check if a predictand has been selected
        if self.modelRunsTable.shape[0] < 1:
            errorString += 'Select and define a valid predictand from the Forecast Target tab. '

        ### Get predictors ###
        predPool = []
        predPeriods = []
        predMethods = []
        predForced = []

        for index, row in self.datasetOperationsTable.iterrows():
            predPool.append(row.name[0])
            predPeriods.append(str(row['AccumulationPeriod']))
            predMethods.append(str(row['AccumulationMethod']))
            predForced.append(str(row['ForcingFlag']))

        if len(predPool) < 1:
            errorString += 'Select at least 1 predictor from the Predictors tab. '

        if predPeriods.count('None') > 0 or predMethods.count('None') > 0 or predForced.count('None') > 0:
            errorString += 'Fully define aggregation options for selected predictors on the Predictors tab. '

        ### Get base model run definitions ###

        # Cross validators
        crossVals = []
        for crossVal in self.modelTab.optionsCrossValidators:
            if crossVal.isChecked():
                crossVals.append(crossVal.objectName())

        # Pre-processors
        preProcList = []
        for preProc in self.modelTab.optionsPreprocessor:
            if preProc.isChecked():
                preProcList.append(preProc.objectName())

        # Regression algorithms
        regAlgs = []
        for regAlg in self.modelTab.optionsRegression:
            if regAlg.isChecked():
                regAlgs.append(regAlg.objectName())

        # Feature selection algorithms
        selAlgs = []
        for selAlg in self.modelTab.optionsSelection:
            if selAlg.isChecked():
                selAlgs.append(selAlg.objectName())

        # Scoring parameters
        scoreParams = []
        for scoreParam in self.modelTab.optionsScoring:
            if scoreParam.isChecked():
                scoreParams.append(scoreParam.objectName())

        if len(crossVals) != 1:
            errorString += 'Select 1 Cross-Validation algorithm from the Options tab. '

        if len(preProcList) < 1 or len(regAlgs) < 1 or len(selAlgs) < 1 or len(scoreParams) < 1:
            errorString += 'Select at least 1 Preprocessor, Regressor, Feature Selector, and Model Scoring option from the Options tab. '


        ### Apply operations to datasets ###

        ### Final go no-go ###
        if len(errorString) > 20:
            self.modelTab.summaryLayoutErrorLabel.setText(errorString)
            self.modelTab.summaryLayoutErrorLabel.setStyleSheet("color : red")
            self.modelTab.summaryLayoutErrorLabel.setVisible(True)
        else:
            # Populate self.modelRunsTable with validated entries
            self.modelRunsTable.loc[0]['PredictorPool'] = predPool
            self.modelRunsTable.loc[0]['PredictorForceFlag'] = predForced
            self.modelRunsTable.loc[0]['PredictorPeriods'] = predPeriods
            self.modelRunsTable.loc[0]['PredictorMethods'] = predMethods
            self.modelRunsTable.loc[0]['CrossValidationType'] = crossVals[0]
            self.modelRunsTable.loc[0]['Preprocessors'] = preProcList
            self.modelRunsTable.loc[0]['RegressionTypes'] = regAlgs
            self.modelRunsTable.loc[0]['FeatureSelectionTypes'] = selAlgs
            self.modelRunsTable.loc[0]['ScoringParameters'] = scoreParams
            ### Kick off the analysis ###
            print('---- MODEL RUN TABLE ----')
            print(self.modelRunsTable.iloc[0])
            print('-------------------------')
            print('Beginning regression calculations...')
            self.rg = RegressionWorker.RegressionWorker(self.modelTab.parent, modelRunTableEntry=self.modelRunsTable.iloc[0])
            self.rg.setData()
            self.rg.run()
            a=1

            ### Populate self.forecastEquationsTable ###
            print('Populating forecast equations table...')
            self.forecastEquationsTable.drop(self.forecastEquationsTable.index, inplace=True)
            resultCounter = 0
            for result in self.rg.resultsList:
                self.forecastEquationsTable.loc[resultCounter] = [None] * self.forecastEquationsTable.columns.shape[0]
                resultPredictors = self.rg.resultsList[resultCounter]['Model']

                self.forecastEquationsTable.loc[resultCounter]['EquationSource'] = 'PyForecast'
                # self.parent.forecastEquationsTable.loc[resultCounter]['EquationComment'] = ''
                self.forecastEquationsTable.loc[resultCounter]['ModelTrainingPeriod'] = \
                self.modelRunsTable.loc[0]['ModelTrainingPeriod']
                self.forecastEquationsTable.loc[resultCounter]['EquationPredictand'] = \
                self.modelRunsTable.loc[0]['Predictand']
                self.forecastEquationsTable.loc[resultCounter]['PredictandPeriod'] = \
                self.modelRunsTable.loc[0]['PredictandPeriod']
                self.forecastEquationsTable.loc[resultCounter]['PredictandMethod'] = \
                self.modelRunsTable.loc[0]['PredictandMethod']
                self.forecastEquationsTable.loc[resultCounter]['EquationCreatedOn'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # self.forecastEquationsTable.loc[resultCounter]['EquationIssueDate'] = ''
                self.forecastEquationsTable.loc[resultCounter]['EquationMethod'] = \
                self.rg.resultsList[resultCounter]['Method']
                self.forecastEquationsTable.loc[resultCounter]['EquationSkill'] = \
                self.rg.resultsList[resultCounter]['Score']
                self.forecastEquationsTable.loc[resultCounter]['EquationPredictors'] = list(compress(predPool, resultPredictors))
                self.forecastEquationsTable.loc[resultCounter]['PredictorPeriods'] = list(compress(predPeriods, resultPredictors))
                self.forecastEquationsTable.loc[resultCounter]['PredictorMethods'] = list(compress(predMethods, resultPredictors))
                # self.forecastEquationsTable.loc[resultCounter]['DirectEquation'] = ''
                resultCounter += 1

            if len(self.rg.resultsList) >= 1:
                # bestModel = self.rg.resultsList[0]
                # print("\nA total of {0} models were assessed".format(len(self.rg.resultsList)))
                # print("\nThe best model found was: ")
                # print("\t-> Predictors: {0}".format(''.join(['1' if i else '0' for i in bestModel['Model']])))
                # print("\t-> Method:     {0}".format(bestModel["Method"]))
                # print("\t-> Scores:     {0}".format(bestModel['Score']))
                self.modelTab.summaryLayoutErrorLabel.setText('Success! ' + str(len(self.rg.resultsList)) + ' models were evaluated...')
                self.modelTab.summaryLayoutErrorLabel.setStyleSheet("color : green")
                self.modelTab.summaryLayoutErrorLabel.setVisible(True)


    def applyPredictandAggregationOption(self):
        # todo: doc string

        predictandData = self.modelTab.targetSelect.currentData()
        predID = predictandData.name
        # Get Min dataset date
        minT = parser.parse(str(np.sort(list(set(self.dataTable.loc[(slice(None),predID),'Value'].index.get_level_values(0).values)))[0]))
        maxT = parser.parse(str(np.sort(list(set(self.dataTable.loc[(slice(None),predID),'Value'].index.get_level_values(0).values)))[-1]))
        selT = parser.parse(self.modelTab.periodStart.dateTime().toString("yyyy-MM-ddThh:mm:ss.zzz"))
        if (parser.parse(str(minT.year) + '-'+str(selT.month)+ '-'+str(selT.day))<minT):
            startT = parser.parse(str(minT.year + 1) + '-' + str(selT.month) + '-' + str(selT.day))
        else:
            startT = parser.parse(str(minT.year) + '-' + str(selT.month) + '-' + str(selT.day))

        nDays = self.modelTab.periodEnd.date().toJulianDay() - self.modelTab.periodStart.date().toJulianDay() + 1 #dates inclusive
        periodString = "R/" + startT.strftime("%Y-%m-%d") + "/P" + str(nDays) + "D/F12M" #(e.g. R/1978-02-01/P1M/F1Y)
        #print("Predictand Entries for the self.modelRunsTable: ")
        #print("--Model Training Period: " + minT.strftime("%Y-%m-%d") + "/" + maxT.strftime("%Y-%m-%d"))
        #print("--Predictand ID: " + str(predID))
        #print("--Predictand Period: " + periodString)
        #print("--Predictand Method: " + self.methodCombo.currentData())
        if self.modelRunsTable.shape[0] < 1:
            self.modelRunsTable.loc[0] = [None] * self.modelRunsTable.columns.shape[0]

        #self.parent.modelRunsTable.loc[0]['ModelTrainingPeriod'] = minT.strftime("%Y-%m-%d") + "/" + maxT.strftime("%Y-%m-%d")
        self.modelRunsTable.loc[0]['ModelTrainingPeriod'] = minT.strftime("%Y") + "/" + maxT.strftime("%Y") + "/1900"
        self.modelRunsTable.loc[0]['Predictand'] = predID
        self.modelRunsTable.loc[0]['PredictandPeriod'] = periodString
        self.modelRunsTable.loc[0]['PredictandMethod'] = self.modelTab.methodCombo.currentData()


    def updateTabDependencies(self, tabIndex):
        # todo: doc string

        ### Get the current index the widget has been changed to ###
        # currentIndex = self.workflowWidget.currentIndex()
        ##print(tabIndex)


        if tabIndex == 3:
            # Update the summary boxes
            ##print('@@ debug statement')
            # Update predictand options
            self.modelTab.summaryLayoutErrorLabel.setVisible(False)
            if self.modelRunsTable.shape[0] < 1:
                self.modelTab.summaryLayoutLabel1.setText('     Period: None')
                self.modelTab.summaryLayoutLabel1.setStyleSheet("color : red")
                self.modelTab.summaryLayoutLabel2.setText('     Predictand: None')
                self.modelTab.summaryLayoutLabel2.setStyleSheet("color : red")
                self.modelTab.summaryLayoutLabel3.setText('     Predictand Period: None')
                self.modelTab.summaryLayoutLabel3.setStyleSheet("color : red")
                self.modelTab.summaryLayoutLabel4.setText('     Predictand Method: None')
                self.modelTab.summaryLayoutLabel4.setStyleSheet("color : red")
            else:
                selDataset = self.datasetTable.loc[self.modelRunsTable.loc[0]['Predictand']]
                selName = str(selDataset['DatasetName']) + ' (' + str(selDataset['DatasetAgency']) + ') ' + str(selDataset['DatasetParameter'])
                self.modelTab.summaryLayoutLabel1.setText('     Period: ' + str(self.modelRunsTable.loc[0]['ModelTrainingPeriod']))
                self.modelTab.summaryLayoutLabel1.setStyleSheet("color : green")
                self.modelTab.summaryLayoutLabel2.setText('     Predictand: ' + selName)
                self.modelTab.summaryLayoutLabel2.setStyleSheet("color : green")
                self.modelTab.summaryLayoutLabel3.setText('     Predictand Period: ' + str(self.modelRunsTable.loc[0]['PredictandPeriod']))
                self.modelTab.summaryLayoutLabel3.setStyleSheet("color : green")
                self.modelTab.summaryLayoutLabel4.setText('     Predictand Method: ' + str(self.modelRunsTable.loc[0]['PredictandMethod']))
                self.modelTab.summaryLayoutLabel4.setStyleSheet("color : green")

            # Load predictors table
            self.modelTab.summaryListWidget.model().loadDataIntoModel(self.datasetTable, self.datasetOperationsTable)

        if tabIndex == 4:
            a=1
