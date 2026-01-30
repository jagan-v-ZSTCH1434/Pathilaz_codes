import zcatalyst_sdk
import logging
import os
import inspect
from flask import request
from datetime import datetime, timedelta
import main
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64

# Initialize the Catalyst Org, project details and current time details
org_id = "60051487989"
project_id = "23382000000044772"
published_bot_id = "78848000000003011"

workitem_name = "functions.cron.pathilazh_ai"
project_name = "AI"
access_token = ""

now = datetime.now() + timedelta(hours=5, minutes=30)
format_time = now.strftime("%d-%b-%Y %H:%M:%S")

# Fetch environment variable
key = os.getenv("key")

class CommonActions:
    def __init__(self):
        self.class_name = self.__class__.__name__
        self.file_name = os.path.basename(__file__)
        self.reference_id = main.reference_id
        function_name = inspect.currentframe().f_code.co_name
        global access_token
        if access_token == "":
            catalyst_object = zcatalyst_sdk.initialize(req=request)
            cache_service = catalyst_object.cache()
            segment_service = cache_service.segment("Personal_Token")
            cache_response = segment_service.get("Auth_Token")
            cache_value = cache_response.get("cache_value")
            if cache_value:
                # Decrypt the cache value 

                key_byte = bytes.fromhex(key) # Convert the key (str) to key (byte)
                aes_key = AESGCM(key_byte)
                raw = base64.b64decode(cache_value) # Decode the encrypted cache value

                # Extract Nonce & ciphertext from the raw data
                nonce = raw[:12]
                ciphertext = raw[12:]

                plaintext = aes_key.decrypt(nonce=nonce,data=ciphertext,associated_data=None) # Decrypt the ciphertext
                access_token = plaintext.decode()
            else:
                logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":"","Request Status":"","Log Type":"SEVERE","Log Data":f"The auth token is empty or null.","Response":str(cache_response),"Reference":"The auth token is empty or null.","Reference ID":self.reference_id,"Added Time":format_time})     
