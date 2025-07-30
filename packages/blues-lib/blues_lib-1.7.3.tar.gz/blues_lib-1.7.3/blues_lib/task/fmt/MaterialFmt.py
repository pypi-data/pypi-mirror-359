import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from type.chain.AllMatchHandler import AllMatchHandler
from type.output.STDOut import STDOut

# brief chain
from material.chain.BriefFmt import BriefFmt
from material.chain.DetailFmt import DetailFmt

class MaterialFmt(AllMatchHandler):
  
  def resolve(self)->STDOut:
    chain = self._get_chain()
    return chain.handle()
  
  def _get_chain(self)->AllMatchHandler:
    brief_fmt = BriefFmt(self._request)
    detail_fmt = DetailFmt(self._request)

    brief_fmt.set_next(detail_fmt)
    return brief_fmt
