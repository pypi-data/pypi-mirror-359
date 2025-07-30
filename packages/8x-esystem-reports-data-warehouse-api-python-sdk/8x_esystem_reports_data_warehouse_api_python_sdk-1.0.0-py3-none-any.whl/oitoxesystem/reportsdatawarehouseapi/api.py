import logging, jsonpickle, requests, os
from fmconsult.http.api import ApiBase

class ReportsDataWarehouseApi(ApiBase):

  def __init__(self):
    try:
      self.api_environment = os.environ['reports.data.warehouse.api.environment'] 
      self.api_token = os.environ['reports.data.warehouse.api.token']
      
      api_sandbox_base_url = 'http://localhost:3002'
      api_live_base_url = 'https://api.data-warehouse.reports.8x-esystem.com.br'

      get_base_url = lambda env: api_live_base_url if env == 'live' else api_sandbox_base_url

      self.base_url = get_base_url(self.api_environment)
      super().__init__()
    except:
      raise
