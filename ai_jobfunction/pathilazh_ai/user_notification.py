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

    def generate_summary(self, request_id, total, answered_count, unanswered_count, invalid_count, error_count, skipped_count):
        """
        Generate a formatted summary string for the request
        """
        summary = f"\nRequest ID : {request_id}\nTotal Questions : {total}\nAnswered Questions Count : {answered_count}\nUnanswered Questions Count : {unanswered_count+error_count}\nInvalid Questions Count : {invalid_count}\nSkipped Questions Count : {skipped_count}\n"
        return summary

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
                logging.info({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"INFO","Log Data":f"Response file shared to user.","Response":str(file_share_response.json()),"Reference":"","Reference ID":self.reference_id,"Added Time":format_time})
    

        summary_info = request_info.get("summary")
        total = summary_info.get("total")
        answered_count = summary_info.get("answered")
        unanswered_count = summary_info.get("unanswered")
        invalid_count = summary_info.get("invalid")
        error_count = summary_info.get("error")
        skipped_count = summary_info.get("skipped")
        
        # Use the new summary function
        summary = self.generate_summary(request_id, total, answered_count, unanswered_count, invalid_count, error_count, skipped_count)

        #For the user to send the summary record

        user_text = "Hello {@"+requested_by+"},"+f"your request ({request_id}) has been completed and the request summary below.\n{summary}"
        if query_type == "sheet":
          user_text += "\nIf you want to update the response into the sheet, kindly refer the help document."

        user_param = {"text": user_text}
        user_param = json.dumps(user_param)
        message_url1 = "https://cliq.zoho.in/api/v2/bots/democustomertool/message"
        user_response = requests.post(url=message_url1, data=user_param, headers=self.cliq_header)
        message_response_statuscode = user_response.status_code

        if message_response_statuscode != 200:
            logging.warning({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"SEVERE","Log Data":f"Exception occured while sending summary notification.","Response":str(user_response.json()),"Reference":"","Reference ID":self.reference_id,"Added Time":format_time})
        else:
            logging.info({"Service":"Catalyst","Org id":org_id,"Project":project_name,"Workitem Name":workitem_name,"Path":f"{self.file_name}.{self.class_name}.{function_name}","Execution id":request_id,"Request Status":"","Log Type":"INFO","Log Data":f"Summary has been sent to user.","Response":str(user_response.json()),"Reference":"","Reference ID":self.reference_id,"Added Time":format_time})

        # Send dev summary to personal bot
        self.send_dev_summary(request_id, requested_by, request_info)

    def send_dev_summary(self, request_id, requested_by, request_info):
        """
        Send summary with unanswered, invalid, and skipped questions to personal Cliq bot
        """
        function_name = inspect.currentframe().f_code.co_name
        
        # Get summary info
        summary_info = request_info.get("summary")
        total = summary_info.get("total")
        answered_count = summary_info.get("answered")
        unanswered_count = summary_info.get("unanswered")
        invalid_count = summary_info.get("invalid")
        error_count = summary_info.get("error")
        skipped_count = summary_info.get("skipped")

        # Parse question data for unanswered and invalid questions
        unanswered_rows = []
        invalid_rows = []
        
        question_data = request_info.get("pathilazh_data")
        if question_data:
            question_ids = question_data.keys()
            for question_id in question_ids:
                curr_question = question_data.get(question_id)
                question = curr_question.get("question")
                question_status = curr_question.get("question_status")
                reason = curr_question.get("reason", "")
                rag_status = curr_question.get("rag_status")

                if question_status == "VALID":
                    if rag_status == "UNKNOWN" or rag_status == "ERROR":
                        unanswered_rows.append([str(question_id), question])
                elif question_status == "INVALID":
                    invalid_rows.append([str(question_id), f"{question} (Reason: {reason})"])

        # Development notification with unanswered and invalid questions
        # Build simple text message instead of card for reliability
        dev_text = f"📋 *Development Review - Request {request_id}  -- {requested_by}*\n\n"
        dev_text += f"*Summary:*\n"
        dev_text += f"• Total: {total}\n"
        dev_text += f"• Answered: {answered_count}\n"
        dev_text += f"• Unanswered: {unanswered_count + error_count}\n"
        dev_text += f"• Invalid: {invalid_count}\n"
        dev_text += f"• Skipped: {skipped_count}\n\n"
        
        if unanswered_rows:
            dev_text += f"*Unanswered Questions:*\n"
            for row in unanswered_rows:
                dev_text += f"  {row[0]}. {row[1]}\n"
            dev_text += "\n"
        
        if invalid_rows:
            dev_text += f"*Invalid Questions:*\n"
            for row in invalid_rows:
                dev_text += f"  {row[0]}. {row[1]}\n"

        dev_param = json.dumps({"text": dev_text})

        dev_message_url = "https://cliq.zoho.in/api/v2/bots/mineuse/message"
        
        try:
            dev_response = requests.post(url=dev_message_url, data=dev_param, headers=self.cliq_header)

            if dev_response.status_code != 200:
                logging.warning({
                    "Service": "Catalyst", "Org id": org_id, "Project": project_name, "Workitem Name": workitem_name,
                    "Path": f"{self.file_name}.{self.class_name}.{function_name}", "Execution id": request_id,
                    "Log Type": "SEVERE", "Log Data": "Failed to send dev notification", "Response": str(dev_response.text),
                    "Reference": "", "Reference ID": self.reference_id, "Added Time": format_time
                })
            else:
                logging.info({
                    "Service": "Catalyst", "Org id": org_id, "Project": project_name, "Workitem Name": workitem_name,
                    "Path": f"{self.file_name}.{self.class_name}.{function_name}", "Execution id": request_id,
                    "Log Type": "INFO", "Log Data": "Dev notification sent successfully",
                    "Reference": "", "Reference ID": self.reference_id, "Added Time": format_time
                })
        except Exception as e:
            logging.warning({
                "Service": "Catalyst", "Org id": org_id, "Project": project_name, "Workitem Name": workitem_name,
                "Path": f"{self.file_name}.{self.class_name}.{function_name}", "Execution id": request_id,
                "Log Type": "SEVERE", "Log Data": f"Exception while sending dev notification: {str(e)}",
                "Reference": "", "Reference ID": self.reference_id, "Added Time": format_time
            })