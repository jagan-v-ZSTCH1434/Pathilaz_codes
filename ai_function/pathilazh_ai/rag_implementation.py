import requests
import json
import logging
import re
import os
import inspect
from flask import request
from pathilazh_ai import common_util, user_notification
from datetime import datetime, timedelta
from pathilazh_ai.common_util import org_id, format_time, workitem_name, project_name
import main


class PathilazhImplementation():
    '''
    Initialize the catalyst object, published bot id, bucket name and reference id
    Initialize the catalyst header
    '''
    def __init__(self):
        # Fetch the class name and file name
        self.class_name = self.__class__.__name__
        self.file_name = os.path.basename(__file__)

        # Initialize the catalyst object & bucket name
        self.bot_id = common_util.published_bot_id
        self.bucket_name = 'pathilazh'
        self.reference_id = main.reference_id

        # Get the access token from common_util class
        common_util.CommonActions()
        access_token = common_util.access_token
        self.rag_header = {
            'Authorization':f'Zoho-oauthtoken {access_token}',
            'catalyst-org':common_util.org_id,
            'x-catalyst-projectid':common_util.project_id,
            'x-catalyst-environment':'Production'
        }

        self.zcql_header = {
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type":"application/json",
            "CATALYST-ORG":org_id,
            "Environment":"Development"
        }

        self.stratus_header = {
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type":"text/plain",
            "CATALYST-ORG":org_id,
            "Environment":"Development"
        }

        self.zcql_url = f"https://api.catalyst.zoho.in/baas/v1/project/{common_util.project_id}/query"
        self.stratus_base_url = f"https://{self.bucket_name}-development.zohostratus.in/"
        
    '''
    Execute the ZCQL query and fetch the current request details
    '''
    def get_request_status(self):
        function_name = inspect.currentframe().f_code.co_name

        # Execute the ZCQL query and fetch the current request details
        # API codebase 
        query = f"SELECT * FROM Pathilazh WHERE Pathilazh.REQUEST_STATUS = 'Pending' AND Pathilazh.ACTION_TYPE = 'Cron';"
        zcql_param = {"query":query}
        zcql_response = requests.post(url=self.zcql_url,json=zcql_param,headers=self.zcql_header)
        zcql_response_code = zcql_response.status_code
        if(zcql_response_code == 200):
            zcql_response_json = zcql_response.json()
            zcql_data = zcql_response_json.get("data")
            if(len(zcql_data) >0):
                pending_requests = []
                for record in zcql_data:
                    request_data = record.get("Pathilazh")
                    request_id = request_data.get("ROWID")
                    requested_by = request_data.get("REQUESTED_BY")
                    query_type = request_data.get("QUERY_TYPE")
                    pending_requests.append({"request_id":request_id,"requested_by":requested_by,"query_type":query_type})
                return pending_requests
        else:
            logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":"","Request Status":"","Log Type":"SEVERE","Log Data":f"Exception occured while fetching pending records from table.","Response":str(zcql_response.json()),"Reference":"While fetching table rows.","Reference ID":self.reference_id,"Added Time":format_time})
        
        return []


        # SDK codebase
        '''
        zcql_service = self.catalyst_obj.zcql()
        query = f"SELECT * FROM Pathilazh_Requests WHERE Pathilazh_Requests.REQUEST_STATUS = 'Pending' AND Pathilazh_Requests.ROWID = '{job_name}';"
        zcql_response = zcql_service.execute_query(query)
        records_count = len(zcql_response)
        pending_requests = []
        if(records_count ==0):
            logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":job_name,"Request Status":"","Log Type":"SEVERE","Log Data":f"There is no records in the table.","Response":str(zcql_response),"Reference":"","Reference ID":self.reference_id,"Added Time":format_time})
            return pending_requests

        for request in zcql_response:
            request_data = request.get("Pathilazh_Requests")
            request_id = request_data.get("ROWID")
            requested_by = request_data.get("REQUESTED_BY")
            query_type = request_data.get("QUERY_TYPE")
            pending_requests.append({"request_id":request_id,"requested_by":requested_by,"query_type":query_type})
        return pending_requests
        '''
    
    '''
    Execute the ZCQL query and update the request status, start time and completion time
    '''
    def update_request_status(self, request_id, start_time, completion_time):
        function_name = inspect.currentframe().f_code.co_name

        # Execute the ZCQL query and update the request details
        # API codebase
        query = f"UPDATE Pathilazh SET Pathilazh.REQUEST_STATUS = 'Completed', Pathilazh.START_TIME = '{start_time}', Pathilazh.COMPLETION_TIME = '{completion_time}' WHERE Pathilazh.ROWID = '{request_id}';"
        zcql_param = {"query":query}
        zcql_response = requests.post(url=self.zcql_url,json=zcql_param,headers=self.zcql_header)
        zcql_response_code = zcql_response.status_code
        if(zcql_response_code == 200):
            zcql_response_json = zcql_response.json()
            zcql_data = zcql_response_json.get("data")
            if(len(zcql_data) == 0):
                logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"SEVERE","Log Data":f"There is no records matched with condition.","Response":str(zcql_response_json),"Reference":"While updating columns of the table rows.","Reference ID":self.reference_id,"Added Time":format_time})
        else:
            logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"SEVERE","Log Data":f"Exception occured while updating the columns of the table record.","Response":str(zcql_response.json()),"Reference":"While updating columns of the table rows.","Reference ID":self.reference_id,"Added Time":format_time})


        # SDK codebase
        '''
        zcql_service = self.catalyst_obj.zcql()
        query = f"UPDATE Pathilazh_Requests SET Pathilazh_Requests.REQUEST_STATUS = 'Completed', Pathilazh_Requests.START_TIME = '{start_time}', Pathilazh_Requests.COMPLETION_TIME = '{completion_time}' WHERE Pathilazh_Requests.ROWID = '{request_id}';"
        zcql_response = zcql_service.execute_query(query)
        records_count = len(zcql_response)
        if(records_count ==0):
            logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"SEVERE","Log Data":f"Exception occured while updating table record.","Response":str(zcql_response),"Reference":"","Reference ID":self.reference_id,"Added Time":format_time})
        '''

    '''
    Download the file from stratus bucket.
    Decode the byte data and return as json string
    '''
    def get_request_info(self,request_id):
        function_name = inspect.currentframe().f_code.co_name

        # Fetch the request information from stratus
        # API codebase
        stratus_url = f"{self.stratus_base_url}{request_id}.json"
        stratus_response = requests.get(url=stratus_url,headers=self.stratus_header)
        stratus_response_code = stratus_response.status_code
        if(stratus_response_code == 200):
            return stratus_response.json()
        elif(stratus_response_code == 404):
            logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"SEVERE","Log Data":f"There is no file with the key and status code is {stratus_response_code}.","Response":str(stratus_response.json()),"Reference":"While downloading file from stratus.","Reference ID":self.reference_id,"Added Time":format_time})
        else:
            logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"SEVERE","Log Data":f"Exception occured while fetching file from stratus and status code is {stratus_response_code}.","Response":str(stratus_response.json()),"Reference":"While downloading file from stratus.","Reference ID":self.reference_id,"Added Time":format_time})

        return {}

        # SDK codebase
        '''
        stratus_obj = self.catalyst_obj.stratus()
        bucket_obj = stratus_obj.bucket(self.bucket_name)
        file_obj = bucket_obj.get_object(f"{request_id}.json")
        logging.warning(f"file data is {file_obj}")
        file_obj_str = file_obj.decode("utf-8")
        file_obj_json = json.loads(file_obj_str)
        return file_obj_json
        '''


    '''
    Update the stratus file content for the request
    '''
    def update_request_info(self,request_id,request_content):
        function_name = inspect.currentframe().f_code.co_name

        # Update the request information in the stratus file
        # API codebase
        stratus_url = f"{self.stratus_base_url}{request_id}.json"
        request_content_byte = request_content.encode("utf-8")
        stratus_response = requests.put(url=stratus_url,data=request_content_byte,headers=self.stratus_header)
        stratus_response_code = stratus_response.status_code
        if(stratus_response_code == 404):
            logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"SEVERE","Log Data":f"There is no file with the key and status code is {stratus_response_code}.","Response":str(stratus_response.json()),"Reference":"While updating file content in stratus.","Reference ID":self.reference_id,"Added Time":format_time})
        elif(stratus_response_code != 200):
            logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"SEVERE","Log Data":f"Exception occured while updating file content and status code is {stratus_response_code}.","Response":str(stratus_response.json()),"Reference":"While updating file content in stratus.","Reference ID":self.reference_id,"Added Time":format_time})


        # SDK codebase
        '''
        stratus_obj = self.catalyst_obj.stratus()
        bucket_obj = stratus_obj.bucket(self.bucket_name)
        upload_response = bucket_obj.put_object(f"{request_id}.json",request_content,{"overwrite":"true"})
        if(upload_response != True):
            logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"SEVERE","Log Data":f"Exception occured while uploading stratus file.","Response":str(upload_response),"Reference":"","Reference ID":self.reference_id,"Added Time":format_time})
        '''


    def get_question_info(self,question):
        # Validate each question and return the status of the question
        temp_question = question
        
        temp_question_1 = re.sub(r'[^A-Za-z0-9]+', '', temp_question) # Alphanumeric only (removes ALL whitespace, tabs, newlines, and symbols)

        temp_question_2 = re.sub(r'[^0-9]+', '', temp_question) # Numbers only (removes everything except digits)

        temp_question_3 = re.sub(r'[A-Za-z0-9\s]+', '', temp_question) # Special characters only - removes letters, digits, and whitespace characters (space, tab (\t), newline (\n), etc):

        # Check whether the string contains at-least 15 characters
        if len(temp_question_1)<15:
            return {"status":"INVALID","reason":"The question should have at-least 15 Alpha-Numerical characters."}
        elif len(temp_question_2)>5:
            return {"status":"INVALID","reason":"The question should not contain more than 5 numbers."}
        elif len(temp_question_3) > 5:
            return {"status":"INVALID","reason":"The question should not contain more than 5 special characters."}
        return {"status":"VALID","reason":"valid question"}
            
    '''
    Fetch the current job's request data from the table.
    Validate each query and mark it's status (VALID/INVALID/SKIP), only if the query type is 'sheet'.
    Fetch RAG response for each query/ question
    Validate the response mark it's status (KNOWN/UNKNOWN/ERROR) using the response code and regex - response validation patten
    Update the request status in Table & Stratus(File)
    Notify the respective user using Cliq bot 
    '''
    def pathilazh_request_processing(self):
        function_name = inspect.currentframe().f_code.co_name

        logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":"","Request Status":"","Log Type":"INFO","Log Data":f"Pathilazh request processing started.","Response":"","Reference":"","Reference ID":self.reference_id,"Added Time":format_time})

        # Initialize the rag url and response validation pattern
        rag_response_url = f"https://api.catalyst.zoho.in/convokraft/api/v1/bots/{common_util.published_bot_id}/answer"
        # Updated pattern to catch more "unknown" type responses
        pattern = r"(sorry|don't have|dont have|don't know|dont know|i'm not sure|im not sure|not sure what|cannot find|can't find|cant find|no information|unable to find|couldn't find|couldnt find|i do not have|i don't have)"

        # Get the list of pending requests from the catalyst datastore and process each request
        pending_requests = self.get_request_status()

        for request in pending_requests:
            request_id = request.get("request_id")
            query_type = request.get("query_type")
            requested_by = request.get("requested_by")
            start_time = (datetime.now() + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")

            logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"INFO","Log Data":f"Pathilazh request processing has been started for request {request_id}.","Response":"","Reference":"","Reference ID":self.reference_id,"Added Time":format_time})
            
            # Get the request information from the stratus file
            request_info = self.get_request_info(request_id)
            if(len(request_info) == 0):
                continue
            question_data = request_info.get("pathilazh_data")

            # Validate each question and mark it's status(VALID/ INVALID/ SKIP) only if the query type is sheet
            if(query_type == "sheet"):
                # Fetch the unique exclude row ids from the input data (stratus data)
                exclude_rows_input = request_info.get("input_data").get("exclude_rows")
                exclude_rows = []
                for exclude_row in exclude_rows_input.split(","):
                    if('-' in exclude_row):
                        temp_exclude_row = exclude_row.split("-")
                        range1 = int(temp_exclude_row[0])
                        range2 = int(temp_exclude_row[1])
                        while range1<=range2:
                            exclude_rows.append(f"{range1}")
                            range1 = range1+1
                else:
                    exclude_rows.append(exclude_row)
                exclude_rows_set = set(exclude_rows)

                # Rewrite each question with it's status
                temp_question_data = {}
                question_ids = question_data.keys()
                for question_id in question_ids:
                    if(question_id not in exclude_rows_set):
                        question = question_data.get(question_id).get("question")
                        question_info = self.get_question_info(question)
                        question_status = question_info.get("status")
                        reason = question_info.get("reason")
                        temp_question_data[question_id] = {"question":question,"question_status":question_status,"reason":reason}
                    else:
                        temp_question_data[question_id] = {"question":question,"question_status":"SKIP","reason":"The row id is part of exclude rows list"}
                question_data = temp_question_data

                logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"INFO","Log Data":f"Each questions are mapped with status(VALID/INVALID/SKIP) query type {query_type}.","Response":"","Reference":"","Reference ID":self.reference_id,"Added Time":format_time})
            
            # Fetch the RAG response for each valid question and map it with RAG response
            question_ids = question_data.keys()
            invalid_count = answered_count = unanswered_count = issue_count = skipped_count = 0
            for question_id in question_ids:
                curr_question = question_data.get(question_id)
                question_status = curr_question.get("question_status")
                if(question_status == "VALID"):
                    question = curr_question.get("question")
                    # Get the RAG reponse from the RAG model
                    rag_param = {"transcript": {"message": question}}
                    rag_param = json.dumps(rag_param)
                    rag_response = requests.post(url=rag_response_url,headers=self.rag_header,data=rag_param)
                    rag_response_statuscode = rag_response.status_code
                    if(rag_response_statuscode == 200):
                        logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":"","Request Status":"","Log Type":"INFO","Log Data":f"RAG response retrieved for question {question}","Response":"","Reference":"","Reference ID":request_id,"Added Time":format_time})
                        rag_response = rag_response.json()
                        response_message = rag_response.get("transcript").get("message")
                        starting_string = response_message[:50]  # Increased from 20 to 50 to catch longer phrases
                        if re.search(pattern, starting_string, re.IGNORECASE):
                            unanswered_count = unanswered_count + 1
                            question_data[question_id]["rag_status"] = "UNKNOWN"
                        else:
                            answered_count = answered_count + 1
                            question_data[question_id]["rag_status"] = "KNOWN"
                        question_data[question_id]["rag_content"] = response_message
                    else:
                        logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"SEVERE","Log Data":f"There is some issue while fetching RAG response for question {question}","Response":str(rag_response.json()),"Reference":"This exception occured while fetching RAG response for question.","Reference ID":self.reference_id,"Added Time":format_time})
                        issue_count = issue_count + 1
                        question_data[question_id]["rag_status"] = "ERROR"
                        question_data[question_id]["rag_error_info"] = {"code":rag_response_statuscode,"response":str(rag_response.json())}
                elif(question_status == "INVALID"):
                    invalid_count = invalid_count + 1
                else:
                    skipped_count = skipped_count + 1


            # Summary of the request
            total = invalid_count+answered_count+unanswered_count+issue_count+skipped_count
            summary = {"total":total,"invalid":invalid_count,"answered":answered_count,"unanswered":unanswered_count,"error":issue_count,"skipped":skipped_count}
            request_info["pathilazh_data"] = question_data
            request_info["summary"] = summary

            logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"INFO","Log Data":f"The summary has been generated.","Response":"","Reference":"","Reference ID":self.reference_id,"Added Time":format_time})

            completion_time = (datetime.now() + timedelta(hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")

            # Update request completion actions in datastore and stratus
            self.update_request_status(request_id,start_time,completion_time)
            self.update_request_info(request_id, str(json.dumps(request_info)))

            logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"INFO","Log Data":f"Request Completed actions updated in datastore and stratus.","Response":"","Reference":"","Reference ID":self.reference_id,"Added Time":format_time})

            # Send RAG process completion acknowledgement to requester
            un_obj = user_notification.UserNotification()
            un_obj.cliq_notification(request_id, requested_by, query_type, request_info)

            logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"INFO","Log Data":f"User notification has been sent & completed.","Response":"","Reference":"","Reference ID":self.reference_id,"Added Time":format_time})

        logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":"","Request Status":"","Log Type":"INFO","Log Data":f"Pathilazh request process completed.","Response":"","Reference":"","Reference ID":self.reference_id,"Added Time":format_time})
