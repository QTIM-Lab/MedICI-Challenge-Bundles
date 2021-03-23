# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import azure
from azure.storage.blob import BlobServiceClient, BlobClient, ContentSettings

from azure.identity import ClientSecretCredential
from azure.identity import ManagedIdentityCredential

from email.utils import formatdate
import adal
import io
import os
from os import getenv
from shutil import copyfile
from pathlib import Path
import requests

import xml.etree.ElementTree as ET

CLIENT_SECRET_CRED_TYPE = "client_secret"
MANAGED_IDENTITY_CRED_TYPE = "managed_identity"

# There are 2 ways to use this class:
#   1. ClientSecretCredential - provide AZURE_TENANT_ID, aad_application_id, aad_application_secret
#   2. ManagedIdentityCredential - provide aad_application_id. Application must be a managed identity: https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview
class AadBlobHelper:
    def __init__(self):
        self.aad_tenant_id = getenv('AZURE_TENANT_ID')
        self.aad_application_id = getenv('AZURE_CLIENT_ID')
        self.aad_application_secret = getenv('AZURE_CLIENT_SECRET', None)
        self.aad_account_name = getenv('AZURE_ACCOUNT_NAME')

        self.account_url="https://{}.blob.core.windows.net".format(self.aad_account_name)

        if self.aad_application_secret is None:
            self.credential_type = MANAGED_IDENTITY_CRED_TYPE
        else:
            self.credential_type = CLIENT_SECRET_CRED_TYPE

    def _get_managed_identity_credential(self):
        try:
            cred = ManagedIdentityCredential(client_id=self.aad_application_id, logging_enable=True)
            return cred.get_token('https://storage.azure.com/.default').token
        except Exception as e:
            print('Exception in _get_managed_identity_credential:' + str(e))
            raise e

    def _get_client_secret_credential(self):
        try:    
            token_credential = ClientSecretCredential(
                self.aad_tenant_id,
                self.aad_application_id,
                self.aad_application_secret
            )
            return token_credential
        except Exception as e:
            print('Exception in _get_client_secret_credential:' + str(e))
            raise e

    def get_blob_service_client(self):
        if self.credential_type is MANAGED_IDENTITY_CRED_TYPE:
            cred = ManagedIdentityCredential(client_id=self.aad_application_id)
        else: # CLIENT_SECRET_CRED_TYPE
            cred = self._get_client_secret_credential()

        blob_service_client = BlobServiceClient(
            account_url="https://{}.blob.core.windows.net".format(self.aad_account_name),
            credential=cred
        )

        return blob_service_client

    def _download_managed_identity_blob(self, container, blob):
        token_credential = self._get_managed_identity_credential()
        
        blob_uri = self.get_blob_uri(container, blob)
        headers = { 'Authorization': "Bearer " + token_credential,
                    'x-ms-version': '2019-07-07',
                    'x-ms-date': formatdate(timeval=None, localtime=False, usegmt=True)}

        return requests.get(blob_uri, headers=headers, verify=False)

    def _get_blob(self, container, blob, encoding = None):
        file_type = ('w' if encoding else 'wb')

        if self.credential_type is MANAGED_IDENTITY_CRED_TYPE:
            get_response = self._download_managed_identity_blob(container, blob)
            data = (get_response.text if encoding else get_response.content)
            return data
        else: # CLIENT_SECRET_CRED_TYPE:
            blob_service_client = self.get_blob_service_client()
            blob_client = blob_service_client.get_blob_client(container, blob)
            download_stream = blob_client.download_blob()
            return download_stream

    def get_blob_to_bytes(self, container, blob):
        print("{} for {}/{}".format('get_blob_to_bytes', container, blob))
        if self.credential_type is MANAGED_IDENTITY_CRED_TYPE:
            data = self._get_blob(container, blob)
            return data
        elif self.credential_type is CLIENT_SECRET_CRED_TYPE:
            data = self._get_blob(container, blob)
            return data.content_as_bytes()

    def get_blob_to_text(self, container, blob):
        print("{} for {}/{}".format('get_blob_to_text', container, blob))
        if self.credential_type is MANAGED_IDENTITY_CRED_TYPE:
            data = self._get_blob(container, blob, encoding='UTF-8')
            return data
        elif self.credential_type is CLIENT_SECRET_CRED_TYPE:
            data = self._get_blob(container, blob, encoding='UTF-8')
            return data.readall()

    def list_blobs(self, container, path=''):
        if self.credential_type is MANAGED_IDENTITY_CRED_TYPE:
            token_credential = self._get_managed_identity_credential()
            
            container_uri = "{}/{}?restype=container&comp=list&prefix{}".format(self.account_url, container, path)

            headers = { 'Authorization': "Bearer " + token_credential,
                        'x-ms-version': '2019-07-07',
                        'x-ms-date': formatdate(timeval=None, localtime=False, usegmt=True)}

            blob_xml_list = requests.get(container_uri, headers=headers, verify=False).text

            root = ET.fromstring(blob_xml_list)

            blob_names = []

            for each in root.findall('.//Blob'):
                for blob in each.findall('.//Name'):
                    blob_names.append(blob.text)

            return blob_names
        elif self.credential_type is CLIENT_SECRET_CRED_TYPE:
            blob_service_client = self.get_blob_service_client()
            cc = blob_service_client.get_container_client(container)
            blob_list = cc.list_blobs(name_starts_with=path)

            blob_names = []
            for blob in blob_list:
                blob_names.append(blob.name)
            return blob_names

    def does_blob_exist(self, container, blob):
        if self.credential_type is MANAGED_IDENTITY_CRED_TYPE:
            token_credential = self._get_managed_identity_credential()
            
            container_uri = "{}/{}?restype=container&comp=list&prefix{}".format(self.account_url, container, blob)

            headers = { 'Authorization': "Bearer " + token_credential,
                        'x-ms-version': '2019-07-07',
                        'x-ms-date': formatdate(timeval=None, localtime=False, usegmt=True)}

            blobs = requests.get(container_uri, headers=headers, verify=False).json()
            if (len(blobs['Blobs']) > 0):
                return True
            else:
                return False
        elif self.credential_type is CLIENT_SECRET_CRED_TYPE:
            blob_service_client = self.get_blob_service_client()
            cc = blob_service_client.get_container_client(container)
            blob_list = cc.list_blobs(container, name_starts_with=blob)
            for b in blob_list:
                if b.name == blob:
                    return True
            return False

    def get_blob_uri(self, container, blob):
        return "{}/{}/{}".format(self.account_url, container, blob)

    def get_host_uri(self):
        return self.account_url