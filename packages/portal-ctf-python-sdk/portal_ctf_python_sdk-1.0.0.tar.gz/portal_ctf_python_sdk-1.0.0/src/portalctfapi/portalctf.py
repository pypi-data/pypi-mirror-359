import os

class PortalCtf():

  def __init__(self):
    try:
      self.login            = os.environ['portal.ctf.api.login']
      self.password         = os.environ['portal.ctf.api.password']
      self.qtd_by_register  = os.environ['portal.ctf.quantity.api.qtd_by_register']
      self.code_template    = os.environ['portal.ctf.api.code_template']
      self.base_url         = 'https://www.portalctf.com.br/portalcopias/wscopia.asmx?wsdl'
    except:
      raise
