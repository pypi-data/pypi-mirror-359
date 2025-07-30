import logging, jsonpickle
from oitoxesystem.reportsdatawarehouseapi.api import ReportsDataWarehouseApi
from fmconsult.utils.url import UrlUtil

class WorkingDay(ReportsDataWarehouseApi):

  def get_all(self, enterprise_id, start_date, end_date, driver_id=None):
    try:
      logging.info(f'get all working days records...')
      params = {
        'enterprise_id': enterprise_id,
        'start_date': start_date,
        'end_date': end_date,
      }
      if driver_id:
        params['driver_id'] = driver_id
      
      
      url = UrlUtil().make_url(self.base_url, ['warehouse', 'working-days'])
      res = self.call_request('GET', url, params=params)
      
      return jsonpickle.decode(res)
    except:
      raise

  def update(self, data, working_day_id):
    
    try: 
      logging.info(f'update working day record...')
      url = UrlUtil().make_url(self.base_url, ['warehouse', 'working-day', working_day_id])
      res = self.call_request('PUT', url, payload=data)
      return jsonpickle.decode(res)
    except:
      raise