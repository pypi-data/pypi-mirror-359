import xmltodict
import logging
from zeep.exceptions import Fault
from zeep import Client
from portalctfapi.portalctf import PortalCtf
logging.getLogger('zeep').setLevel(logging.ERROR)

class WsCopia(PortalCtf):
    def recuperar_copia(self, last_pointer):
        try:
            url = self.base_url
            
            client = Client(url)

            header = {
                'login': self.login,
                'senha': self.password
            }

            soap_login = client.get_element('ns0:SoapLogin')
            header = soap_login(login=header['login'], senha=header['senha'])

            client.set_default_soapheaders([header])

            response = client.service.RecuperarCopia(
                parametroCopia={
                    'Ponteiro': last_pointer,
                    'CodTemplate': self.code_template,
                    'QtdRegistro': self.qtd_by_register
                }
            )
            xml_dict = xmltodict.parse(response)
            return xml_dict
        except Fault as e:
            print(f"Error when calling the service: {str(e)}")
            raise
        
    def listar_templates(self):
        try:
            url = url = self.base_url
            client = Client(url)

            header = {
                'login': self.login,
                'senha': self.password
            }
            soap_login = client.get_element('ns0:SoapLogin')
            header = soap_login(login=header['login'], senha=header['senha'])

            client.set_default_soapheaders([header])

            response = client.service.ListarTemplatesDisponiveis()
            
            xml_dict = xmltodict.parse(response)
            return xml_dict 
        except Fault as e:
            print(f"Error when calling the service: {str(e)}")
            raise
