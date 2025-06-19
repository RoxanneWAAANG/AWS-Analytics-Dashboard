import json
import boto3
import time
import os
from typing import Dict, Any

# Initialize AWS services
stepfunctions = boto3.client('stepfunctions')

# Get Step Functions ARN from environment
STATE_MACHINE_ARN = os.environ.get('STATE_MACHINE_ARN')

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Triggers the AI Pipeline Step Functions workflow
    """
    print("AI Pipeline trigger activated")
    
    # Extract input from event
    user_input = extract_user_input(event)
    
    if not user_input:
        return create_error_response(400, "No input provided")
    
    print(f"Processing input: {user_input[:100]}...")
    
    # Prepare execution input
    execution_input = {
        'input': user_input,
        'timestamp': time.time(),
        'request_id': context.aws_request_id if context else f"req_{int(time.time())}"
    }
    
    # Start Step Functions execution
    execution_response = start_pipeline_execution(execution_input)
    
    print(f"Pipeline started: {execution_response['executionArn']}")
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        },
        'body': json.dumps({
            'message': 'Pipeline execution started successfully',
            'execution_arn': execution_response['executionArn'],
            'request_id': execution_input['request_id'],
            'status': 'RUNNING'
        })
    }
        

def extract_user_input(event: Dict[str, Any]) -> str:
    """
    Extract user input from various event sources
    """
    # API Gateway event
    if 'body' in event:
        body = event['body']
        if isinstance(body, str):
            body = json.loads(body)
        
        if isinstance(body, dict):
            return body.get('input') or body.get('text') or body.get('message', '')
        return str(body)
    
    # Direct invocation
    if 'input' in event:
        return str(event['input'])
    
    # Query parameters
    if 'queryStringParameters' in event and event['queryStringParameters']:
        return event['queryStringParameters'].get('input', '')
    
    # Path parameters
    if 'pathParameters' in event and event['pathParameters']:
        return event['pathParameters'].get('input', '')
    
    # Direct string
    if isinstance(event, str):
        return event
    
    return ''
    

def start_pipeline_execution(execution_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Start Step Functions execution
    """
    if not STATE_MACHINE_ARN:
        raise ValueError("STATE_MACHINE_ARN environment variable not set")
    
    execution_name = f"pipeline-{int(time.time())}-{execution_input['request_id'][-8:]}"
    
    response = stepfunctions.start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        name=execution_name,
        input=json.dumps(execution_input)
    )
    
    return response


def create_error_response(status_code: int, message: str) -> Dict[str, Any]:
    """
    Create standardized error response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        },
        'body': json.dumps({
            'error': message,
            'timestamp': time.time()
        })
    }

# Additional utility functions for different trigger scenarios

def handle_scheduled_execution(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle scheduled/automated pipeline executions
    """
    # For future use with CloudWatch Events or other schedulers
    default_inputs = [
        "Test pipeline functionality",
        "Generate performance metrics",
        "Health check execution"
    ]
    
    import random
    test_input = random.choice(default_inputs)
    
    return {
        'input': test_input,
        'timestamp': time.time(),
        'request_id': f"scheduled_{int(time.time())}",
        'execution_type': 'scheduled'
    }

def handle_batch_execution(inputs: list) -> list:
    """
    Handle multiple inputs in batch (for future batch processing)
    """
    executions = []
    
    for i, user_input in enumerate(inputs):
        execution_input = {
            'input': user_input,
            'timestamp': time.time(),
            'request_id': f"batch_{int(time.time())}_{i}",
            'execution_type': 'batch'
        }
        
        try:
            execution_response = start_pipeline_execution(execution_input)
            executions.append({
                'status': 'started',
                'execution_arn': execution_response['executionArn'],
                'input_preview': user_input[:50] + '...' if len(user_input) > 50 else user_input
            })
        except Exception as e:
            executions.append({
                'status': 'failed',
                'error': str(e),
                'input_preview': user_input[:50] + '...' if len(user_input) > 50 else user_input
            })
    
    return executions

# Health check function
def health_check() -> Dict[str, Any]:
    """
    Perform health check of pipeline components
    """
    health_status = {
        'trigger_function': 'healthy',
        'step_functions': 'unknown',
        'timestamp': time.time()
    }
    
    try:
        # Check if Step Functions is accessible
        if STATE_MACHINE_ARN:
            stepfunctions.describe_state_machine(stateMachineArn=STATE_MACHINE_ARN)
            health_status['step_functions'] = 'healthy'
        else:
            health_status['step_functions'] = 'configuration_error'
    except Exception as e:
        health_status['step_functions'] = f'error: {str(e)}'
    
    return health_status