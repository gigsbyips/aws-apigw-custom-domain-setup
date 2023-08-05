import json

def lambda_handler(event, context):
    # Retrieve the HTTP method from the event object
    http_method = event['httpMethod']
    api_id = event['requestContext']['apiId']
    stage = event['requestContext']['stage']
    #resource_path = event['requestContext']['resourcePath']
    
    if http_method == 'GET':
        # Handle GET request
        response_body = {'message': f'Mock GET response from {api_id} in stage {stage}'}
        status_code = 200
    elif http_method == 'PUT':
        # Handle PUT request
        response_body = {'message': f'Mock PUT response from {api_id} in stage {stage}'}
        status_code = 200
    elif http_method == 'DELETE':
        # Handle DELETE request
        response_body = {'message': f'Mock DELETE response from {api_id} in stage {stage}'}
        status_code = 200
    else:
        # Return an error for unsupported methods
        response_body = {'error': f'Unsupported HTTP method from {api_id} in stage {stage}'}
        status_code = 400
    
    # Construct the API response
    response = {
        'statusCode': status_code,
        'body': json.dumps(response_body)
    }
    
    return response
