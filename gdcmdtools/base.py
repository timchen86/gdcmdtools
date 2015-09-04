#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from apiclient.discovery import build

import httplib2
import pprint

import logging 
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BASE_INFO = {
        "app":"gdcmdtools",
        "description":'Google Drive command line tools',
        "version":'0.96'}

GDAPI_VER = 'v2'
FTAPI_VER = 'v1'
DISCOVERY_URL = "https://www.googleapis.com/discovery/v1/apis/{api}/{apiVersion}/rest"

DEBUG_LEVEL = ('debug', 'info', 'warning', 'error', 'critical')

class GDBase(object):
    def __init__(self):
        self.drive_service = None
        self.ft_service = None
        self.http = None
        self.root_folder = None

    def get_root(self):
        if self.root_folder == None:
            if self.drive_service == None:
                self.get_drive_service()
            about = self.drive_service.about().get().execute()
       
        self.root_folder = about['rootFolderId']
        logger.debug("root_folder=%s" % self.root_folder)
        return self.root_folder

    def get_drive_service(self, http):
        self.drive_service = build('drive', GDAPI_VER, 
                discoveryServiceUrl=DISCOVERY_URL, http=http)

        return self.drive_service

    def get_ft_service(self, http):
        self.ft_service = build('fusiontables', FTAPI_VER, 
                discoveryServiceUrl=DISCOVERY_URL, http=http)

        return self.ft_service


