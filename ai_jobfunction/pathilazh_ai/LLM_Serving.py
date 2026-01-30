import requests
import json
import os
import inspect
import logging
import re
from pathilazh_ai import common_util
from pathilazh_ai.common_util import org_id, project_name, workitem_name, format_time
import main


class LLMServing:
    """
    LLM Serving class to process questions using Catalyst's LLM and store responses in Stratus
    """
    
    def __init__(self):
        self.class_name = self.__class__.__name__
        self.file_name = os.path.basename(__file__)
        self.reference_id = main.reference_id
        self.bucket_name = 'pathilazh'
        
        # Get the access token from common_util class
        common_util.CommonActions()
        access_token = common_util.access_token
        
        # LLM API headers
        self.llm_header = {
            'Authorization': f'Zoho-oauthtoken {access_token}',
            'Content-Type': 'application/json',
            'catalyst-org': common_util.org_id,
            'x-catalyst-projectid': common_util.project_id,
            'x-catalyst-environment': 'Production'
        }
        
        # Stratus headers for file operations
        self.stratus_header = {
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type": "text/plain",
            "CATALYST-ORG": org_id,
            "Environment": "Development"
        }
        
        # ZCQL headers for database operations
        self.zcql_header = {
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type": "application/json",
            "CATALYST-ORG": org_id,
            "Environment": "Development"
        }
        
        # URLs
        self.stratus_base_url = f"https://{self.bucket_name}-development.zohostratus.in/"
        self.zcql_url = f"https://api.catalyst.zoho.in/baas/v1/project/{common_util.project_id}/query"
        
        # Catalyst LLM serving URL (Zia GenAI)
        self.llm_url = f"https://api.catalyst.zoho.in/baas/v1/project/{common_util.project_id}/genai/chat"
        
        # Response validation pattern for unknown answers
        self.unknown_pattern = r"(sorry|don't have|dont have|don't know|dont know|i'm not sure|im not sure|not sure what|cannot find|can't find|cant find|no information|unable to find|couldn't find|couldnt find|i do not have|i don't have)"

    def get_llm_response(self, question, context=""):
        """
        Get response from Catalyst LLM for a given question
        
        Args:
            question: The user's question
            context: Optional context for the LLM
            
        Returns:
            dict: Contains 'status' (KNOWN/UNKNOWN/ERROR) and 'response' (answer text)
        """
        function_name = inspect.currentframe().f_code.co_name
        
        try:
            # Prepare the prompt with context if available
            if context:
                prompt = f"Context: {context}\n\nQuestion: {question}\n\nPlease provide a helpful and accurate answer."
            else:
                prompt = f"Question: {question}\n\nPlease provide a helpful and accurate answer."
            
            # LLM request payload
            llm_payload = {
                "prompt": prompt,
                "model": "zia-gpt",  # Catalyst's default LLM model
                "max_tokens": 1024,
                "temperature": 0.7
            }
            
            llm_response = requests.post(
                url=self.llm_url,
                json=llm_payload,
                headers=self.llm_header
            )
            
            llm_status_code = llm_response.status_code
            
            if llm_status_code == 200:
                response_json = llm_response.json()
                answer = response_json.get("data", {}).get("response", "")
                
                # Validate if the response is a known answer or unknown
                if self.validate_response(answer):
                    return {"status": "KNOWN", "response": answer}
                else:
                    return {"status": "UNKNOWN", "response": answer}
            else:
                logging.warning({
                    "Service": "Catalyst", "Org id": org_id, "Project": project_name,
                    "Workitem Name": workitem_name,
                    "Path": f"{self.file_name}.{self.class_name}.{function_name}",
                    "Execution id": "", "Request Status": "", "Log Type": "SEVERE",
                    "Log Data": f"LLM API failed with status code {llm_status_code}",
                    "Response": str(llm_response.text),
                    "Reference": "While getting LLM response",
                    "Reference ID": self.reference_id, "Added Time": format_time
                })
                return {"status": "ERROR", "response": ""}
                
        except Exception as e:
            logging.warning({
                "Service": "Catalyst", "Org id": org_id, "Project": project_name,
                "Workitem Name": workitem_name,
                "Path": f"{self.file_name}.{self.class_name}.{function_name}",
                "Execution id": "", "Request Status": "", "Log Type": "SEVERE",
                "Log Data": f"Exception while getting LLM response: {str(e)}",
                "Response": "", "Reference": "While getting LLM response",
                "Reference ID": self.reference_id, "Added Time": format_time
            })
            return {"status": "ERROR", "response": ""}

    def validate_response(self, response):
        """
        Validate if the LLM response is a known answer or unknown
        
        Args:
            response: The LLM response text
            
        Returns:
            bool: True if known answer, False if unknown
        """
        if not response:
            return False
        
        # Check first 50 characters for unknown patterns
        response_lower = response.lower()[:50]
        
        if re.search(self.unknown_pattern, response_lower, re.IGNORECASE):
            return False
        
        return True

    def get_stratus_file(self, request_id):
        """
        Download file from Stratus bucket
        
        Args:
            request_id: The request ID (file name without extension)
            
        Returns:
            dict: File content as JSON or empty dict if failed
        """
        function_name = inspect.currentframe().f_code.co_name
        
        stratus_url = f"{self.stratus_base_url}{request_id}.json"
        stratus_response = requests.get(url=stratus_url, headers=self.stratus_header)
        stratus_response_code = stratus_response.status_code
        
        if stratus_response_code == 200:
            return stratus_response.json()
        else:
            logging.warning({
                "Service": "Catalyst", "Org id": org_id, "Project": project_name,
                "Workitem Name": workitem_name,
                "Path": f"{self.file_name}.{self.class_name}.{function_name}",
                "Execution id": request_id, "Request Status": "", "Log Type": "SEVERE",
                "Log Data": f"Failed to download file from Stratus. Status: {stratus_response_code}",
                "Response": str(stratus_response.text),
                "Reference": "While downloading file from Stratus",
                "Reference ID": self.reference_id, "Added Time": format_time
            })
            return {}

    def update_stratus_file(self, request_id, content):
        """
        Upload/Update file in Stratus bucket
        
        Args:
            request_id: The request ID (file name without extension)
            content: The content to upload (dict will be converted to JSON)
            
        Returns:
            bool: True if successful, False otherwise
        """
        function_name = inspect.currentframe().f_code.co_name
        
        stratus_url = f"{self.stratus_base_url}{request_id}.json"
        
        if isinstance(content, dict):
            content = json.dumps(content)
        
        content_bytes = content.encode("utf-8")
        stratus_response = requests.put(url=stratus_url, data=content_bytes, headers=self.stratus_header)
        stratus_response_code = stratus_response.status_code
        
        if stratus_response_code == 200:
            logging.info({
                "Service": "Catalyst", "Org id": org_id, "Project": project_name,
                "Workitem Name": workitem_name,
                "Path": f"{self.file_name}.{self.class_name}.{function_name}",
                "Execution id": request_id, "Request Status": "", "Log Type": "INFO",
                "Log Data": "File updated in Stratus successfully",
                "Response": "", "Reference": "While updating file in Stratus",
                "Reference ID": self.reference_id, "Added Time": format_time
            })
            return True
        else:
            logging.warning({
                "Service": "Catalyst", "Org id": org_id, "Project": project_name,
                "Workitem Name": workitem_name,
                "Path": f"{self.file_name}.{self.class_name}.{function_name}",
                "Execution id": request_id, "Request Status": "", "Log Type": "SEVERE",
                "Log Data": f"Failed to update file in Stratus. Status: {stratus_response_code}",
                "Response": str(stratus_response.text),
                "Reference": "While updating file in Stratus",
                "Reference ID": self.reference_id, "Added Time": format_time
            })
            return False

    def process_questions_with_llm(self, request_id):
        """
        Process all questions in a request using LLM and store answers in Stratus
        
        Args:
            request_id: The request ID to process
            
        Returns:
            dict: Summary of processing (total, answered, unanswered, etc.)
        """
        function_name = inspect.currentframe().f_code.co_name
        
        logging.info({
            "Service": "Catalyst", "Org id": org_id, "Project": project_name,
            "Workitem Name": workitem_name,
            "Path": f"{self.file_name}.{self.class_name}.{function_name}",
            "Execution id": request_id, "Request Status": "", "Log Type": "INFO",
            "Log Data": "Starting LLM processing for request",
            "Response": "", "Reference": "",
            "Reference ID": self.reference_id, "Added Time": format_time
        })
        
        # Initialize summary counters
        summary = {
            "total": 0,
            "answered": 0,
            "unanswered": 0,
            "invalid": 0,
            "error": 0,
            "skipped": 0
        }
        
        # Get request data from Stratus
        request_data = self.get_stratus_file(request_id)
        
        if not request_data:
            logging.warning({
                "Service": "Catalyst", "Org id": org_id, "Project": project_name,
                "Workitem Name": workitem_name,
                "Path": f"{self.file_name}.{self.class_name}.{function_name}",
                "Execution id": request_id, "Request Status": "", "Log Type": "SEVERE",
                "Log Data": "No request data found in Stratus",
                "Response": "", "Reference": "",
                "Reference ID": self.reference_id, "Added Time": format_time
            })
            return summary
        
        question_data = request_data.get("pathilazh_data", {})
        question_ids = list(question_data.keys())
        summary["total"] = len(question_ids)
        
        # Process each question
        for question_id in question_ids:
            curr_question_data = question_data.get(question_id, {})
            question = curr_question_data.get("question", "")
            question_status = curr_question_data.get("question_status", "VALID")
            
            # Skip invalid questions
            if question_status == "INVALID":
                summary["invalid"] += 1
                continue
            
            # Skip questions that already have answers
            if curr_question_data.get("rag_status") == "KNOWN":
                summary["skipped"] += 1
                continue
            
            # Get LLM response for the question
            llm_result = self.get_llm_response(question)
            
            # Update question data with LLM response
            curr_question_data["rag_status"] = llm_result["status"]
            curr_question_data["rag_content"] = llm_result["response"]
            
            # Update summary counters
            if llm_result["status"] == "KNOWN":
                summary["answered"] += 1
            elif llm_result["status"] == "UNKNOWN":
                summary["unanswered"] += 1
            else:
                summary["error"] += 1
            
            # Update question data in request
            question_data[question_id] = curr_question_data
        
        # Update request data with processed questions and summary
        request_data["pathilazh_data"] = question_data
        request_data["summary"] = summary
        
        # Save updated data back to Stratus
        self.update_stratus_file(request_id, request_data)
        
        logging.info({
            "Service": "Catalyst", "Org id": org_id, "Project": project_name,
            "Workitem Name": workitem_name,
            "Path": f"{self.file_name}.{self.class_name}.{function_name}",
            "Execution id": request_id, "Request Status": "", "Log Type": "INFO",
            "Log Data": f"LLM processing completed. Summary: {json.dumps(summary)}",
            "Response": "", "Reference": "",
            "Reference ID": self.reference_id, "Added Time": format_time
        })
        
        return summary

    def process_single_question(self, question, request_id=None):
        """
        Process a single question using LLM and optionally save to Stratus
        
        Args:
            question: The question to process
            request_id: Optional request ID to save the answer
            
        Returns:
            dict: Contains 'status' and 'response'
        """
        function_name = inspect.currentframe().f_code.co_name
        
        # Get LLM response
        llm_result = self.get_llm_response(question)
        
        # If request_id is provided, save to Stratus
        if request_id:
            answer_data = {
                "request_id": request_id,
                "question": question,
                "answer": llm_result["response"],
                "status": llm_result["status"]
            }
            self.update_stratus_file(f"{request_id}_answer", answer_data)
        
        return llm_result

    def get_pending_requests(self):
        """
        Get all pending requests from the database
        
        Returns:
            list: List of pending request data
        """
        function_name = inspect.currentframe().f_code.co_name
        
        query = "SELECT * FROM Pathilazh WHERE Pathilazh.REQUEST_STATUS = 'Pending';"
        zcql_param = {"query": query}
        
        zcql_response = requests.post(url=self.zcql_url, json=zcql_param, headers=self.zcql_header)
        zcql_response_code = zcql_response.status_code
        
        pending_requests = []
        
        if zcql_response_code == 200:
            zcql_data = zcql_response.json().get("data", [])
            for record in zcql_data:
                request_info = record.get("Pathilazh", {})
                pending_requests.append({
                    "request_id": request_info.get("ROWID"),
                    "requested_by": request_info.get("REQUESTED_BY"),
                    "query_type": request_info.get("QUERY_TYPE"),
                    "action_type": request_info.get("ACTION_TYPE")
                })
        else:
            logging.warning({
                "Service": "Catalyst", "Org id": org_id, "Project": project_name,
                "Workitem Name": workitem_name,
                "Path": f"{self.file_name}.{self.class_name}.{function_name}",
                "Execution id": "", "Request Status": "", "Log Type": "SEVERE",
                "Log Data": f"Failed to fetch pending requests. Status: {zcql_response_code}",
                "Response": str(zcql_response.text),
                "Reference": "While fetching pending requests",
                "Reference ID": self.reference_id, "Added Time": format_time
            })
        
        return pending_requests

    def update_request_status(self, request_id, status, start_time="", completion_time=""):
        """
        Update request status in the database
        
        Args:
            request_id: The request ID to update
            status: New status (e.g., 'Completed', 'Processing')
            start_time: Optional start time
            completion_time: Optional completion time
            
        Returns:
            bool: True if successful, False otherwise
        """
        function_name = inspect.currentframe().f_code.co_name
        
        if start_time and completion_time:
            query = f"UPDATE Pathilazh SET Pathilazh.REQUEST_STATUS = '{status}', Pathilazh.START_TIME = '{start_time}', Pathilazh.COMPLETION_TIME = '{completion_time}' WHERE Pathilazh.ROWID = '{request_id}';"
        else:
            query = f"UPDATE Pathilazh SET Pathilazh.REQUEST_STATUS = '{status}' WHERE Pathilazh.ROWID = '{request_id}';"
        
        zcql_param = {"query": query}
        zcql_response = requests.post(url=self.zcql_url, json=zcql_param, headers=self.zcql_header)
        
        if zcql_response.status_code == 200:
            return True
        else:
            logging.warning({
                "Service": "Catalyst", "Org id": org_id, "Project": project_name,
                "Workitem Name": workitem_name,
                "Path": f"{self.file_name}.{self.class_name}.{function_name}",
                "Execution id": request_id, "Request Status": "", "Log Type": "SEVERE",
                "Log Data": f"Failed to update request status. Status: {zcql_response.status_code}",
                "Response": str(zcql_response.text),
                "Reference": "While updating request status",
                "Reference ID": self.reference_id, "Added Time": format_time
            })
            return False
