from PyQt5.QtWidgets import *
from Views import DatasetViewDialog

# Get the global application
app = QApplication.instance()

class DatasetModelView:
  """DatasetModelView is an object that contains functions for connecting GUI
  events from the Dataset's Tab to the Dataset Model. 
  """

  def __init__(self):

    self.dt = app.gui.DatasetsTab

    # Load the web_map
    with open(app.base_dir + '/Resources/WebMap/map_data.geojson', 'r') as r:
      geojson = r.read()

    # connect javascript console messages from the web map to the application
    self.dt.dataset_map.page.loadFinished.connect(lambda x: self.dt.dataset_map.page.runJavaScript(f"loadDatasetCatalog({geojson})"))
    self.dt.dataset_map.page.java_msg_signal.connect(self.add_dataset_from_map)

    # List view context menu actions
    self.dt.dataset_list.view_action.triggered.connect(self.view_dataset)
    self.dt.dataset_list.remove_action.triggered.connect(self.remove_dataset)
    self.dt.dataset_list.add_action.triggered.connect(self.add_blank_dataset)
    self.dt.dataset_list.action1.triggered.connect(lambda c: self.add_climate_dataset(self.dt.dataset_list.action1.data()))
    self.dt.dataset_list.action2.triggered.connect(lambda c: self.add_climate_dataset(self.dt.dataset_list.action2.data()))
    
    # Double click event
    self.dt.dataset_list.doubleClicked.connect(self.view_dataset)
    
    # Connect Models to Views
    self.dt.dataset_list.setModel(app.datasets)

    return

  def add_climate_dataset(self, idx):

    if idx == 1:
      dataset = app.datasets.add_dataset(
        external_id = 'MENSO',
        name = 'Multivariate El Nino Southern Oscillation',
        agency = 'NOAA',
        parameter = 'Climate Index',
        raw_unit = app.units.get_unit('-'),
        display_unit = app.units.get_unit('-'),
        dataloader = app.dataloaders.get_loader_by_name('NOAA-CPC')['CLASS']()
      )
      
      
    if idx == 2:
      dataset = app.datasets.add_dataset(
        external_id = 'PNA',
        name = 'Pacific North American Index',
        agency = 'NOAA',
        parameter = 'Climate Index',
        raw_unit = app.units.get_unit('-'),
        display_unit = app.units.get_unit('-'),
        dataloader = app.dataloaders.get_loader_by_name('NOAA-CPC')['CLASS']()
      )
    if not dataset:
      ret = QMessageBox.information(self.dt, 'Dataset duplicate', 'Dataset is already in dataset list.')
    self.dt.dataset_list.scrollToBottom()
      

  def add_dataset_from_map(self, msg):

    msg=msg.strip()

    if msg[:3] != 'ID:':
      return
    
    msg = msg.replace('ID:', '')

    id_, name, agency, dloader, param, pcode, units  = msg.split('~~')
    dataset = app.datasets.add_dataset(
      external_id = id_,
      agency = agency,
      name=name,
      parameter=param,
      param_code=pcode,
      raw_unit=app.units.get_unit(units),
      display_unit = app.units.get_unit(units),
      dataloader = app.dataloaders.get_loader_by_name(dloader)['CLASS']()
    ) 
    if not dataset:
      ret = QMessageBox.information(self.dt, 'Dataset duplicate', 'Dataset is already in dataset list.')
    self.dt.dataset_list.scrollToBottom()

  def view_dataset(self, checked):
    
    if len(self.dt.dataset_list.selectedIndexes()) > 1:
      m = QMessageBox("Please select only one dataset to view")
      m.exec()
      return
    
    idx = self.dt.dataset_list.selectedIndexes()[0]
    dataset = app.datasets[idx.row()]
    dv = DatasetViewDialog.DatasetViewer(app, dataset.guid)
    
    return

  def remove_dataset(self, checked):

    for i,idx in enumerate(self.dt.dataset_list.selectedIndexes()):
      dataset = app.datasets[idx.row()-i]
      app.datasets.remove_dataset(dataset)

    return

  def add_blank_dataset(self, checked):
    
    new_dataset = app.datasets.add_dataset()
    dv = DatasetViewDialog.DatasetViewer(app, new_dataset.guid, new=True)

    return