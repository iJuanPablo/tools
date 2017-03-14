"""
ip_reader
---------
Reads the Machine IP and emails if it has changed

Mac - Linux
    crontab

Windows:

Command line as follows:

schtasks /Create /SC HOURLY /TN PythonTask /TR "PATH_TO_PYTHON_EXE PATH_TO_PYTHON_SCRIPT"

That will create an hourly task called 'PythonTask'. You can replace HOURLY with DAILY, WEEKLY etc.
PATH_TO_PYTHON_EXE will be something like: C:\python25\python.exe.

Otherwise you can open the Task Scheduler and do it through the GUI. Hope this helps.

"""

import collections
import base64
import json

from httplib import HTTPSConnection
from urllib import urlencode
from urllib2 import urlopen


def encode_params(data):
    """Encode parameters in a piece of data.

    Will successfully encode parameters when passed as a dict or a list of
    2-tuples. Order is retained if data is a list of 2-tuples but arbitrary
    if parameters are supplied as a dict.
    """

    if isinstance(data, (str, bytes)):
        return data
    elif hasattr(data, 'read'):
        return data
    elif hasattr(data, '__iter__'):
        result = []
        for k, vs in to_key_val_list(data):
            if isinstance(vs, basestring) or not hasattr(vs, '__iter__'):
                vs = [vs]
            for v in vs:
                if v is not None:
                    result.append(
                        (k.encode('utf-8') if isinstance(k, str) else k,
                         v.encode('utf-8') if isinstance(v, str) else v))
        return urlencode(result, doseq=True)
    else:
        return data


def to_key_val_list(value):
    """Take an object and test to see if it can be represented as a
    dictionary. If it can be, return a list of tuples, e.g.,

    ::

        >>> to_key_val_list([('key', 'val')])
        [('key', 'val')]
        >>> to_key_val_list({'key': 'val'})
        [('key', 'val')]
        >>> to_key_val_list('string')
        ValueError: cannot encode objects that are not 2-tuples.

    :rtype: list
    """
    if value is None:
        return None

    if isinstance(value, (str, bytes, bool, int)):
        raise ValueError('cannot encode objects that are not 2-tuples')

    if isinstance(value, collections.Mapping):
        value = value.items()

    return list(value)


file_path = 'ip.txt'
my_ip = json.load(urlopen('https://api.ipify.org/?format=json'))['ip']

try:
    with open(file_path, 'r') as the_file:
        file_ip = the_file.read()
except:
    file_ip = u''

if my_ip != file_ip:

    http = 'http://'
    url = 'api.mailgun.net'
    request = '/v3/sandboxee586e52376a457d8b274c437718a56e.mailgun.org/messages'

    key = 'key-29caea072852af2816e0b02f6733b751'
    base64string = base64.encodestring('api:'+key).replace('\n', '')

    headers = {'Authorization': 'Basic %s' % base64string,
               'content-type': 'application/x-www-form-urlencoded'}
    payload = {"from": "PostMaster <postmaster@sandboxee586e52376a457d8b274c437718a56e.mailgun.org>",
               "to": "Juan Pablo <jp.urzua.t@gmail.com>",
               "subject": "La IP de la oficina ha cambiado!",
               "text": "La nueva IP es: " + my_ip}

    body = encode_params(payload)

    http_connection = HTTPSConnection(url)
    http_connection.request(method="POST", url=request, body=body, headers=headers)
    response = json.loads(http_connection.getresponse().read())
    print response

    if response['message'] == 'Queued. Thank you.':
        with open(file_path, 'w') as the_file:
            the_file.write(my_ip)
            print "Escrito"

else:
    print 'Same IP'


