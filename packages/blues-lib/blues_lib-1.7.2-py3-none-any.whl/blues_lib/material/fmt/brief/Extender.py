import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.chain.AllMatchHandler import AllMatchHandler
from type.output.STDOut import STDOut
from util.BluesAlgorithm import BluesAlgorithm 

class Extender(AllMatchHandler):
  def resolve(self)->STDOut:
    
    try:
      entities = self._request.get('entities')
      for entity in entities:
        self._set(entity)
      return STDOut(200,'ok',entities)
    except Exception as e:
      return STDOut(500,'SystemField resolve failed %s' % e,None)
      
  def _set(self,entity):
    config = self._request.get('model').config
    entity['material_type'] = config.get('mode') # article gallery shortvideo qa
    entity['material_site'] = config.get('site') # ifeng bbc
    entity['material_lang'] = config.get('lang') # cn en
    id = config.get('site')+'_'+BluesAlgorithm.md5(entity['material_url'])
    entity['material_id'] = id
