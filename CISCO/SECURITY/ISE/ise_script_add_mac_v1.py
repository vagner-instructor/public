import sys
import re
import getpass
from ise import ERS

# Checando se o parametro existe
if len(sys.argv) < 2:
    sys.exit('ERRO: Por favor inclua um parametro apos o script, exemplo * python ise_script_add_mac.py 11:22:33:44:55:66 *')

# Checando se o parametro fornecido é realmente o mac address
param_1 = sys.argv[1]
print('Checando o parametro fornecido: ' + param_1)
[]
if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", param_1.lower()):
    print('MacAddress ' + param_1 + ' está no padrão \n')
    mac_certo = 1

else:
    print('MacAddress ' + param_1 + ' Não está no padrão. Exemplo 11:22:33:44:55:66\n')
    mac_certo = 0
    exit()

# Se estiver certo entao continua
if (mac_certo == 1):
    ise_node = input("ISE - Por favor insira o IP do ISE:\n")
    ers_user = input("ISE - Por favor insira o usuario da API do ISE:\n")
    print('ISE - Por favor insira a senha do usuario da API do ISE:')
    ers_pass = getpass.getpass()
    endpoint_group = input("ISE - Por favor insira o nome do grupo de endpoint:\n")

ise = ERS(ise_node=ise_node, ers_user=ers_user, ers_pass=ers_pass, verify=False, disable_warnings=True)

# Declarando variaveis do ISE se não coletar acima, "use_csrf=True" para mais seguranca no ISE mas o disable_warnings abre brecha
#endpoint_group = 'MOBILE_ENDPOINT'
#ise = ERS(ise_node='198.18.133.27', ers_user='ers_admin', ers_pass='C1sco12345', verify=False, disable_warnings=True)

class InvalidMacAddress(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)



class ERS(object):
    def __init__(self, ise_node, ers_user, ers_pass, verify=False, disable_warnings=False, use_csrf=False, timeout=2,
                 protocol='https'):
        """
        Classe para interagir com o Cisco ISE via ERS API.
        
        
        :param ise_node: IP Address of the primary admin ISE node
        :param ers_user: ERS username
        :param ers_pass: ERS password
        :param verify: Verify SSL cert
        :param disable_warnings: Disable requests warnings
        :param timeout: Query timeout
        """
        self.ise_node = ise_node
        self.user_name = ers_user
        self.user_pass = ers_pass
        self.protocol = protocol

        self.url_base = '{0}://{1}:9060/ers'.format(self.protocol, self.ise_node)
        self.ise = requests.sessions.Session()
        self.ise.auth = (self.user_name, self.user_pass)
        # http://docs.python-requests.org/en/latest/user/advanced/#ssl-cert-verification
        self.ise.verify = verify
        self.disable_warnings = disable_warnings
        self.use_csrf = use_csrf
        self.csrf = None
        self.csrf_expires = None
        self.timeout = timeout
        self.ise.headers.update({'Connection': 'keep_alive'})

        if self.disable_warnings:
            requests.packages.urllib3.disable_warnings()

    def _request(self, url, method="get", data=None):
        if self.use_csrf:
            if not self.csrf_expires or not self.csrf or datetime.utcfromtimestamp(0) > self.csrf_expires:
                self.ise.headers.update({'ACCEPT': 'application/json', 'Content-Type': 'application/json',
                                         'X-CSRF-TOKEN': 'fetch'})

                resp = self.ise.get('{0}/config/deploymentinfo/versioninfo'.format(self.url_base))
                self.csrf = resp.headers["X-CSRF-Token"]
                self.csrf_expires = datetime.utcfromtimestamp(0) + timedelta(seconds=60)

            self.ise.headers.update({'ACCEPT': 'application/json', 'Content-Type': 'application/json',
                                     'X-CSRF-TOKEN': self.csrf})

            req = self.ise.request(method, url, data=data, timeout=self.timeout)
        else:
            req = self.ise.request(method, url, data=data, timeout=self.timeout)

        return req


    def get_endpoint_group(self, group):
        """
        Pegar detalhes do grupo de Endpoint.
        :param group: Name of the identity group
        :return: result dictionary
        """
        self.ise.headers.update(
            {'ACCEPT': 'application/json', 'Content-Type': 'application/json'})

        result = {
            'success': False,
            'response': '',
            'error': '',
        }

        resp = self.ise.get(
            '{0}/config/endpointgroup?filter=name.EQ.{1}'.format(self.url_base, group))
        found_group = resp.json()

        if found_group['SearchResult']['total'] == 1:
            result = self.get_object('{0}/config/endpointgroup/'.format(
                self.url_base), found_group['SearchResult']['resources'][0]['id'], 'IdentityGroup')
            return result
        elif found_group['SearchResult']['total'] == 0:
            result['response'] = '{0} not found'.format(group)
            result['error'] = 404
            return result

        else:
            result['response'] = '{0} not found'.format(group)
            result['error'] = resp.status_code
            return result

#
data_endpoint = ise.get_endpoint_group(group=endpoint_group)['response']

print('Dados do grupo que será adicionado: ')
print(data_endpoint)
print('\nID do Grupo: ' + data_endpoint['name'] + '/ é ' + data_endpoint['id'])

#Pega o retorno da função e adiciona o mac address dentro desse grupo
ise.add_endpoint(name='ENDPOINT_API_X', mac=param_1, group_id=(data_endpoint['id']), description=' via Endpoint Adicionado VIA_API')

print('\n### OK ### OK ### OK ### OK ### OK ### OK ###')
print('Mac Address ' + param_1 + ' foi adicionado no grupo ' + data_endpoint['id'])
print('### OK ### OK ### OK ### OK ### OK ### OK ###')