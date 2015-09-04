#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run_flow
from apiclient.discovery import build

from gdcmdtools.base import BASE_INFO

import httplib2
import pprint

import shutil

import logging 
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DICT_OF_REDIRECT_URI = {
    "oob":"(default) means \"urn:ietf:wg:oauth:2.0:oob\"",
    "local":"means \"http://localhost\""
    }

SCOPE = [
    # if using /drive.file instead of /drive,
    # then the fusion table is not seen by drive.files.list()
    # also, drive.parents.insert() fails.
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/fusiontables',
    'https://www.googleapis.com/auth/drive.scripts',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email'
]

class GDAuth(object):
    def __init__(self, secret_file=None, if_oob=True):
        default_secret_file = os.path.expanduser('~/.%s.secrets' % BASE_INFO["app"])

        if secret_file == None:
            self.secret_file = default_secret_file
        else:
            # should reissue the credencials
            storage_file = os.path.expanduser('~/.%s.creds' % BASE_INFO["app"])
            if os.path.isfile(storage_file):
                os.remove(storage_file)

            try:
               shutil.copyfile(secret_file, default_secret_file)
            except:
                logger.error('failed to copy secret file')

            self.secret_file = default_secret_file
            
        os.chmod(self.secret_file, 0600)

        self.if_oob = if_oob 

    def run(self):
        credentials = self.get_credentials()
        return credentials


    def get_credentials(self):
        #home_path = os.getenv("HOME")
        #storage_file = os.path.abspath(
        #        '%s/.%s.creds' % (home_path,BASE_INFO["app"]))
        storage_file = os.path.expanduser('~/.%s.creds' % BASE_INFO["app"])
        logger.debug('storage_file=%s' % storage_file)

        try:
            with open(storage_file): pass
        except IOError:
            logger.error('storage_file: %s not exists' % storage_file)
            #return None

        storage = Storage(storage_file)
        credentials = storage.get()

        # FIXME: if secret_file is given, should clean creds
        if credentials is None or credentials.invalid == True:
            #credentials_file = os.path.abspath(
            #        '%s/.%s.secrets' % (home_path,BASE_INFO["app"]))
            credentials_file = self.secret_file

            #logger.debug('credentials_file=%s' % credentials_file)

            if self.if_oob:
                redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            else:
                redirect_uri = None


            try: 
                flow = flow_from_clientsecrets(
                    credentials_file,
                    scope=SCOPE,
                    redirect_uri=redirect_uri)
            except:
                logger.error("failed on flow_from_clientsecrets()")
                return None


                        
            if self.if_oob:
                auth_uri = flow.step1_get_authorize_url()
                logger.info('Please visit the URL in your browser: %s' % auth_uri)
                code = raw_input('Insert the given code: ')

                try:
                    credentials = flow.step2_exchange(code)
                except:
                    logger.error("failed on flow.step2_exchange()")
                    return None

                storage.put(credentials)
                credentials.set_store(storage)

            else:
                try:
                    credentials = run_flow(flow, storage)
                except:
                    logger.error("failed on oauth2client.tools.run_flow()")
                    return None

        self.credentials = credentials
       
        return self.credentials


    def get_authorized_http(self):
        self.http =  httplib2.Http()
        self.credentials.authorize(self.http)
        #wrapped_request = self.http.request

        # FIXME
        def _Wrapper(uri, method="GET", body=None, headers=None, **kw):
            logger.debug('Req: %s %s' % (uri, method))
            logger.debug('Req headers:\n%s' % pprint.pformat(headers))
            logger.debug('Req body:\n%s' % pprint.pformat(body))
            resp, content = wrapped_request(uri, method, body, headers, **kw)
            logger.debug('Rsp headers:\n%s' % pprint.pformat(resp))
            logger.debug('Rsp body:\n%s' % pprint.pformat(content))
            return resp, content

        #self.http.request = _Wrapper
        return self.http


