import logging, jsonpickle
from oitoxesystem.reportsdatawarehouseapi.api import ReportsDataWarehouseApi
from fmconsult.utils.url import UrlUtil

class KilometerTracker(ReportsDataWarehouseApi):

  def get_all(self, enterprise_id, start_date, end_date, driver_id=None, vehicle_id=None, page=None, limit=None, subenterprise_id=None):
    try:
      logging.info(f'get all working days records...')
      params = {
        'enterprise_id': enterprise_id,
        'start_date': start_date,
        'end_date': end_date,
      }
      
      if driver_id:
        params['driver_id'] = driver_id
        
      if subenterprise_id:
        params['subenterprise_id'] = subenterprise_id
        
      if vehicle_id:
        params['vehicle_id'] = vehicle_id
        
      if page:
        params['page'] = page
        
      if limit:
        params['limit'] = limit        
        
      url = UrlUtil().make_url(self.base_url, ['warehouse', 'kilometer-tracker'])
      res = self.call_request('GET', url, params=params)
      return jsonpickle.decode(res)
    except:
      raise 