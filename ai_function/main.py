from pathilazh_ai import rag_implementation
reference_id = "" # Cron scheduler id

def handler(cron_details, context):
    rag_obj = rag_implementation.PathilazhImplementation()
    rag_obj.pathilazh_request_processing()

    context.close_with_success()


# Local machine running code
'''
if __name__ == "__main__":
    # Update the job id to the reference id

    # reference_id = "18680000000112265"

    # Trigger the pathilazh process implementation
    rag_obj = rag_implementation.PathilazhImplementation()
    rag_obj.pathilazh_request_processing()

    context.close_with_success() # conclude the function execution with a success response
'''
