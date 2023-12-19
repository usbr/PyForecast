from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication
from uuid import uuid4
import pandas as pd
from Models.Datasets import Dataset
from Utilities.HydrologyDateTimes import convert_to_water_year
import pickle
import numpy as np
from numpy import nan
from inspect import signature

app = QApplication.instance()

def ordinaltg(n):
      return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(4 if 10 <= n % 100 < 20 else n % 10, "th")


class ResampledDataset:

  def __init__(self, **kwargs):
    self.dataset_guid = None
    self.forced = False
    self.mustBePositive = False
    self.period_start = pd.to_datetime('1900-07-01')
    self.period_end = pd.to_datetime('1900-08-01')
    self.agg_method = None
    self.unit = None
    self.preprocessing = None
    self.data = pd.Series([], index=pd.DatetimeIndex([]), dtype='float64')

    self.__dict__.update(**kwargs)

    # Validate datetimes
    
    if self.period_start.month >= 10:
      self.period_start = self.period_start.replace(year=1899)
    else:
      self.period_start = self.period_start.replace(year=1900)
    if self.period_end.month >= 10:
      self.period_end = self.period_end.replace(year=1899)
    else:
      self.period_end = self.period_end.replace(year=1900)

    if 'unit' not in kwargs:
      self.unit = self.dataset().display_unit
    
    if self.agg_method == 'ACCUMULATION (CMS to MCM)':
      self.unit = app.units.get_unit('mcm')
    if self.agg_method == 'ACCUMULATION (CFS to KAF)':
      self.unit = app.units.get_unit('kaf')
  
  def dataset(self):
    if self.dataset_guid != None:
      return app.datasets.get_dataset_by_guid(self.dataset_guid)
    else:
      return Dataset()
  
  def resample(self):
    
    if not self.dataset().data.empty:

      self.data = pd.Series([], index=pd.DatetimeIndex([]), dtype='float64')

      dataset = self.dataset()

      # reference to raw data for convienence
      #scale, offset = dataset.raw_unit.convert_to(dataset.display_unit)
      raw = dataset.data#*scale + offset

      # get the agg method
      a = app.agg_methods[self.agg_method]

      # Compute period duration
      days = (self.period_end - self.period_start).days

      # Create the periods
      start = self.period_start.replace(year=raw.index[0].year - 1)
      tracker = pd.Timestamp(start)
      periods = []
      while tracker <= raw.index[-1]:
        periods.append((tracker, tracker + pd.DateOffset(days=days)))
        tracker += pd.DateOffset(years=1)
      
      # Resample the data
      for idx in pd.IntervalIndex.from_tuples(periods):
        d = raw[idx.left:idx.right].dropna()
        if len(d>=1):
          self.data.loc[idx.left] = a(d)
        else:
          self.data.loc[idx.left] = nan

      # remove nans
      self.data = self.data.dropna()
      self.data.index = list(map(convert_to_water_year, self.data.index))

      # Convert to any new units
      if self.unit != dataset.display_unit:
        if self.agg_method not in ['ACCUMULATION (CFS to KAF)', 'ACCUMULATION (CMS to MCM)']:
          scale, offset = dataset.display_unit.convert_to(self.unit)
          self.data = self.data*scale + offset


      self.preprocess()
      if isinstance(self.data, pd.DataFrame):
        self.data = self.data.iloc[:,0]

      return
    else:
      print("did not resample")
    
  def preprocess(self):
    if not self.data.empty:
      
      method = app.preprocessing_methods[self.preprocessing]
      if len(signature(method).parameters) > 1:

        self.data, *self.params = self.data.apply(method)

      else:

        self.data = self.data.apply(method)
    
  def __list_form__(self):
    return f'{self.dataset().name} - {self.__period_str__()} - {self.agg_method} {self.dataset().parameter:25.25}'

  def __condensed_form__(self):
    return f'{self.dataset().external_id}: {self.dataset().name} - {self.dataset().parameter}'

  def __period_str__(self):
    return f'{self.period_start:%b-%d} to {self.period_end:%b-%d}'



class Regressor:

  def __init__(self, **kwargs):

    self.regression_model = None
    self.cross_validation = None
    self.feature_selection = None
    self.scoring_metric = None

    self.__dict__.update(**kwargs)
  
  def __str__(self):

    return f'{self.regression_model.NAME}/{self.cross_validation.NAME}'


class ModelConfiguration:

  def __init__(self, **kwargs):

    self.guid = str(uuid4())
    
    self.training_start_date = None
    self.training_end_date = None
    self.training_exclude_dates = []

    self.predictand = ResampledDataset()
    self.predictor_pool = PredictorPool()
    self.regressors = Regressors()

    self.comment = ''
    self.name = ''
    self.issue_date = None

    self._ok_to_pickle = [
      'training_start_date', 'training_end_date',
      'trianing_exclude_dates', 'comment', 'name', 'issue_date', 'guid'
    ]
    
    # Load in all args and kwargs into the dataset definition
    self.__dict__.update(**kwargs)

    return
  
  def define_new_predictor(self, **kwargs):
    p = ResampledDataset(**kwargs)
    self.predictor_pool.add_predictor(p)
  
  def define_new_predictand(self, **kwargs):
    p = ResampledDataset(**kwargs)
    self.predictand = p
  
  def define_new_regressor(self, **kwargs):
    r = Regressor(**kwargs)
    self.regressors.add_regressor(r)

  def __simple_target_string__(self):

    exclude = len(self.training_exclude_dates) > 0
    exclude_str = '(excluding ' + ','.join(list(map(str, self.training_exclude_dates))) + ')' if exclude else ''

    return  f'<span style="font-family:Consolas"><strong>{self.name}</strong> will create models for a <strong>{self.predictand.period_start:%b-%d} through {self.predictand.period_end:%b-%d}</strong> forecast ' + \
            f'targeting <strong>{self.predictand.dataset().__condensed_form__()} {self.predictand.agg_method}</strong> ' + \
            f'(to be issued on <strong>{self.issue_date:%b-%d}</strong>). This model will be trained on ' + \
            f'data from the period <strong>{self.training_start_date:%b-%Y} to {self.training_end_date:%b-%Y} {exclude_str}</strong></span>'

  def __str__(self):
    return f'<ModelConfiguration {self.guid}>'

  def __rich_text__(self):
    


    r = f"""
    <style>
            .small_title {{ 
                background-color: lightgray;
                font-weight: bold;
                color: black;
                border: 1px solid black;
            }}
            .title {{
              color: blue;
            }}
            .var {{
              font-weight: bold;
            }}
            .col1 {{
              width: 122px
            }}
            table,td, tr {{
                background-color: white;
                color: #0e0e0e;
                font-family: Arial;
                font-size: medium;
                border-collapse:"collapse";
                border: 1px solid black;
                padding:5px;
            }}
          </style>
          <table width="100%">
            <tr><td class="small_title col1">Configuration Name</td><td class="var title">{self.name}</td></tr>
            <tr><td class="small_title">Issue Date</td><td class="var">{self.issue_date:%B %d}</td></tr>
            <tr><td class="small_title">Forecast Target</td><td class="var">{self.predictand.dataset().external_id} | {self.predictand.agg_method} | {self.predictand.period_start:%m/%d} - {self.predictand.period_end:%m/%d}</td></tr>
          </table>
    """

    return r

class Regressors(QAbstractTableModel):

  def __init__(self):

    QAbstractTableModel.__init__(self)
    self.regressors = []

  def headerData(self, section, orientation, role):
    if section>=0:
      if orientation == Qt.Horizontal and role==Qt.DisplayRole: 
        if section == 0:
          return "Regression Algorithm"
        if section == 1:
          return "Scoring Metrics"
  def data(self, index, role):
    if role == Qt.DisplayRole:
      row=index.row()
      column=index.column()
      if row >= 0 and column >= 0:
        r = self.regressors[row]
        if column == 0:
          return r.regression_model
        if column == 1:
          return r.scoring_metric
    return QVariant()

  def rowCount(self, parent=QModelIndex()):
    return len(self)
  
  def columnCount(self, parent=QModelIndex()):
    return 2


  def add_regressor(self, regressor):
    self.regressors.append(regressor)
    self.insertRow(self.rowCount())
    self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount(), self.columnCount()))

  def delete_regressor(self, idx):
    _ = self.regressors.pop(idx)
    self.removeRow(idx)
    self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount(), self.columnCount()))

  def insertRows(self, position, rows, parent=QModelIndex()):
    self.beginInsertRows(parent, position, position+rows-1)
    self.endInsertRows()
    return True
  
  def removeRows(self, position, rows, parent=QModelIndex()):
    self.beginRemoveRows(parent, position, position+rows-1)
    self.endRemoveRows()
    return True

  def __setitem__(self, idx, regressor):
    self.regressors[idx] = regressor
    self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount(), self.columnCount()))

  def __getitem__(self, idx):
    return self.regressors[idx]

  def __len__(self):
    return len(self.regressors)
        
class PredictorPool(QAbstractTableModel):

  def __init__(self):

    QAbstractTableModel.__init__(self)
    self.predictors = []

  def headerData(self, section, orientation, role):
    if section>=0:
      if orientation == Qt.Horizontal and role==Qt.DisplayRole: 
        if section == 0:
          return "Name"
        if section == 1:
          return "Period"
        if section == 2:
          return "Agg. Method"
        if section == 3:
          return "Unit"
        if section == 4:
          return "Preprocessing"
        if section == 5:
          return "Forced?"
    return QAbstractTableModel.headerData(self, section, orientation, role)


  def data(self, index, role=Qt.DisplayRole):

    row = index.row()
    col = index.column()
    
    if row < 0 or col < 0:
      return QVariant()

    predictor = self.predictors[row]

    if role == Qt.DisplayRole:
      if col == 0:
        return predictor.dataset().__condensed_form__()
      if col == 1:
        return predictor.__period_str__()
      if col == 2:
        return predictor.agg_method
      if col == 3:
        return predictor.unit.id
      if col == 4:
        return predictor.preprocessing
      if col == 5:
        return '✓' if predictor.forced else 'NO'
    
  def add_predictor(self, predictor = None):
    self.predictors.append(predictor)
    self.insertRow(self.rowCount())
    self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount(), self.columnCount()))
  
  def define_new_predictor(self, **kwargs):
    p = ResampledDataset(**kwargs)
    self.add_predictor(p)

  def delete_predictor(self, idx):
    _ = self.predictors.pop(idx)
    self.removeRow(idx)
    self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount(), self.columnCount()))

  def rowCount(self, parent=QModelIndex()):
    if parent.isValid():
      return 0
    return len(self.predictors)

  def columnCount(self, parent=QModelIndex()):
    return 6

  def insertRows(self, position, rows, parent=QModelIndex()):
    self.beginInsertRows(parent, position, position+rows-1)
    self.endInsertRows()
    return True
  
  def removeRows(self, position, rows, parent=QModelIndex()):
    self.beginRemoveRows(parent, position, position+rows-1)
    self.endRemoveRows()
    return True

  def __setitem__(self, idx, predictor):
    self.predictors[idx] = predictor
    self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount(), self.columnCount()))

  def __getitem__(self, idx):
    return self.predictors[idx]

  def __iter__(self):
    return iter(self.predictors)

  def __len__(self):
    return len(self.predictors)


class ModelConfigurations(QAbstractListModel):

  # Define model roles
  id_role = Qt.UserRole + 1 # Returns the configuration GUID
  obj_role = Qt.UserRole + 2 # Returns the configuration object
  rich_text_role = Qt.UserRole + 3
  simple_str_role = Qt.UserRole + 4

  def __init__(self):

    QAbstractListModel.__init__(self)
    self.configurations = []

    return
  
  def data(self, index, role=Qt.DisplayRole):

    row = index.row()
    configuration = self.configurations[row]
    if role == self.obj_role:
      return configuration

    if role == self.rich_text_role:
      return configuration.__rich_text__()

    if role == self.simple_str_role:
      return configuration.__simple_target_string__()
    
    return

  def rowCount(self, parent=QModelIndex()):
    return len(self.configurations)

  def roleNames(self):
    return {
      self.id_role : b'id',
      self.obj_role: b'object',
      self.rich_text_role : b'rich_text'
    }

  def add_configuration(self, **kwargs):

    configuration = ModelConfiguration(**kwargs)
    self.configurations.append(configuration)
    self.insertRow(self.rowCount())
    self.dataChanged.emit(self.index(0), self.index(self.rowCount()))  

    return 

  def remove_configuration(self, configuration):
    
    idx = self.configurations.index(configuration)
    _ = self.configurations.pop(idx)
    self.beginRemoveRows(QModelIndex(), idx, idx)
    self.removeRow(idx) 
    self.endRemoveRows()
    self.dataChanged.emit(self.index(0), self.index(self.rowCount()))  
    
    
    return
  
  def clear_all(self):
    j=0
    for i in range(len(self.configurations)):
      config = self.configurations[i-j]
      self.remove_configuration(config)
      j+=1
  
  def get_by_id(self, id):
    for config in self.configurations:
      if config.guid == id:
        return config

  def load_from_file(self, f):
    num_configurations = pickle.load(f)

    for i in range(num_configurations):
      config_dict = pickle.load(f)
      predictand = pickle.load(f)
      if not hasattr(predictand.dataset, 'raw_unit'):
          predictand.dataset.raw_unit = predictand.dataset.unit
          predictand.dataset.display_unit = predictand.dataset.unit
      predictand.dataset_guid = predictand.dataset.guid
      del predictand.dataset
      num_predictors = pickle.load(f)
      predictor_pool = PredictorPool()
      for i in range(num_predictors):
        predictor = pickle.load(f)
        if not hasattr(predictor.dataset, 'raw_unit'):
          predictor.dataset.raw_unit = predictor.dataset.unit
          predictor.dataset.display_unit = predictor.dataset.unit
        predictor.dataset_guid = predictor.dataset.guid
        del predictor.dataset
        predictor_pool.add_predictor(
          predictor
        )
      num_regressors = pickle.load(f)
      regressors = Regressors()
      for i in range(num_regressors):
        regressor = pickle.load(f)
        regressors.add_regressor(
          regressor
        )
      self.add_configuration(
        **ModelConfiguration(
          **config_dict,
          predictand=predictand,
          predictor_pool = predictor_pool,
          regressors = regressors
        ).__dict__
      )
    self.dataChanged.emit(self.index(0), self.index(self.rowCount()))

  def save_to_file(self, f):
    pickle.dump(len(self.configurations), f, 4) # Dump the number of configurations
    for config in self.configurations:
      config_dict = {}
      for (key, value) in config.__dict__.items():
        if key in config._ok_to_pickle:
          config_dict[key] = value
      pickle.dump(config_dict, f, 4)

      pickle.dump(config.predictand, f, 4)
      
      pickle.dump(len(config.predictor_pool), f, 4)
      for dataset in config.predictor_pool:
        pickle.dump(dataset, f, 4)
      
      pickle.dump(len(config.regressors), f, 4)
      for regressor in config.regressors:
        pickle.dump(regressor, f, 4)



  def __getitem__(self, index):
    return self.configurations[index]

  def __setitem__(self, index, config):
    self.configurations[index] = config
    self.dataChanged.emit(self.index(0), self.index(self.rowCount())) 

  def __len__(self):
    return len(self.configurations)