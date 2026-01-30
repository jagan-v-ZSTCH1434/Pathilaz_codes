from pathilazh_ai import rag_implementation

reference_id = "23382000000044823" # execution job scheduler id

'''
Update the job scheduler id to reference id and mark the variable as global variable
Trigger the pathilazh process implementation
'''
def handler(job_request, context):
    global reference_id
    job_data = job_request.get_job_meta_details()
    job_name = job_data.get("job_name") # Job name
    reference_id = job_data.get("id") # Job id

    rag_obj = rag_implementation.PathilazhImplementation()
    rag_obj.pathilazh_request_processing(job_name)

    context.close_with_success() # conclude the function execution with a success response


# Local machine running code
'''
if __name__ == "__main__":
    # Update the job id to the reference id

    # job_name = "18680000000112297"
    # reference_id = "18680000000112265"

    # Trigger the pathilazh process implementation
    rag_obj = rag_implementation.PathilazhImplementation()
    rag_obj.pathilazh_request_processing(job_name)

    context.close_with_success() # conclude the function execution with a success response
'''
