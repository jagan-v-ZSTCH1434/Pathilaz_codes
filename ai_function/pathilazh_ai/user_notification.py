import requests
import json
import os
import inspect
import logging
from pathilazh_ai import common_util
from io import BytesIO
from pathilazh_ai.common_util import org_id, project_name, workitem_name, format_time
import main

class UserNotification():
    def __init__(self):
        self.class_name = self.__class__.__name__
        self.file_name = os.path.basename(__file__)
        self.reference_id = main.reference_id
        access_token = common_util.access_token
        self.cliq_header = {
            'Authorization':f'Zoho-oauthtoken {access_token}'
        }

    '''
    Sent the Q/A response as file, only if the query type is 'text'
    Sent the summary of the request to the requester
    '''
    def cliq_notification(self, request_id, requested_by, query_type, request_info):
        function_name = inspect.currentframe().f_code.co_name
        if(query_type == "text"):
            answered = unanswered = invalid = ""
            question_data = request_info.get("pathilazh_data")
            question_ids = question_data.keys()
            for question_id in question_ids:
                curr_question = question_data.get(question_id)
                question = curr_question.get("question")
                question_status = curr_question.get("question_status")
                reason = curr_question.get("reason")
                rag_status = curr_question.get("rag_status")
                rag_content = curr_question.get("rag_content")

                if(question_status == "VALID"):
                    if(rag_status == "KNOWN"):
                        answered = answered + f"{question_id}. {question}\n\nResponse: {rag_content}\n\n"
                    elif(rag_status == "UNKNOWN" or rag_status == "ERROR"):
                        unanswered = unanswered + f"{question_id}. {question}\n\n"
                elif(question_status == "INVALID"):
                    invalid = invalid + f"{question_id}. {question}\n\nReason: {reason}\n\n"

            file_content = ""
            file_content = file_content + f"Answered Questions:\n{answered}\n" if answered != "" else file_content
            file_content = file_content + f"Unanswered Questions:\n{unanswered}\n" if unanswered != "" else file_content
            file_content = file_content + f"Invalid Questions:\n{invalid}\n" if invalid != "" else file_content

            # Share file to the user
            file_obj = BytesIO(file_content.encode('utf-8'))
            file_obj.name = f"{request_id}.txt"
            files = {"file": (file_obj.name, file_obj, "text/plain")}
            files_list = []
            files_list.append(files)
        
            file_share_url = "https://cliq.zoho.in/api/v2/bots/democustomertool/files"
            data = {"user_id":requested_by}
            file_share_response = requests.post(url= file_share_url, headers=self.cliq_header,data=data,files=files)
            file_share_responsecode = file_share_response.status_code
            if file_share_responsecode != 200:
                logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"SEVERE","Log Data":f"Exception occured while sharing QA file with requester.","Response":str(file_share_response.json()),"Reference":"","Reference ID":self.reference_id,"Added Time":format_time})
            else:
                logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"INFO","Log Data":f"Response file shared to user.","Response":str(file_share_response.json()),"Reference":"","Reference ID":self.reference_id,"Added Time":format_time})
        
        
        # Share the summary to the requester
        summary_info = request_info.get("summary")
        total = summary_info.get("total")
        answered_count = summary_info.get("answered")
        unanswered_count = summary_info.get("unanswered")
        invalid_count = summary_info.get("invalid")
        error_count = summary_info.get("error")
        skipped_count = summary_info.get("skipped")
        summary = f"\nRequest ID : {request_id}\nTotal Questions : {total}\nAnswered Questions Count : {answered_count}\nUnanswered Questions Count : {unanswered_count+error_count}\nInvalid Questions Count : {invalid_count}\nSkipped Questions Count : {skipped_count}\n"

        text_message = "Hello {@"+requested_by+"},"+f"your request ({request_id}) has been completed and the request summary below."
        if(query_type == "sheet"):
            text_message = text_message + " If you want to update the response into the sheet, kindly refer the help document and follow the process mentioned."
        text_message = f"{text_message}\n{summary}" 
        
        param = {"text": text_message}
        param = json.dumps(param)
        message_url = "https://cliq.zoho.in/api/v2/bots/mineuse/message"
        message_response = requests.post(url=message_url,data=param,headers=self.cliq_header)
        message_response_statuscode = message_response.status_code

        if message_response_statuscode != 200:
            logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"SEVERE","Log Data":f"Exception occured while sending summary notification.","Response":str(message_response.json()),"Reference":"","Reference ID":self.reference_id,"Added Time":format_time})
        else:
            logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"INFO","Log Data":f"Summary has been sent to user.","Response":str(message_response.json()),"Reference":"","Reference ID":self.reference_id,"Added Time":format_time})


        
