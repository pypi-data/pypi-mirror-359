import logging, jsonpickle
from oitoxesystem.reportsdatawarehouseapi.api import ReportsDataWarehouseApi
from fmconsult.utils.url import UrlUtil

class FuelSupllyRecord(ReportsDataWarehouseApi):

  def get_all(self, enterprise_id, start_date, end_date, vehicle_id, font):
    try:
      params = {
        'enterprise_id': enterprise_id,
        'start_date': start_date,
        'end_date': end_date,
        'font': font
      }
      
      if vehicle_id:
        params['vehicle_id'] = vehicle_id

      url = UrlUtil().make_url(self.base_url, ['warehouse', 'fuel-supply-records'])
      res = self.call_request('GET', url, params=params)
      return jsonpickle.decode(res)
    except:
      raise
    
  def get_by_fuel_fuel_supply_record(self, fuel_supply_record_ids):
    try:
      logging.info(f'get_by_fuel_fuel_supply_record records...')
      
      payload = {
        'fuel_supply_record_ids': fuel_supply_record_ids
      }
      
      url = UrlUtil().make_url(self.base_url, ['warehouse', 'fuel-supply-records', 'records'])
      res = self.call_request('POST', url, payload=payload)
      return jsonpickle.decode(res)
    except:
      raise