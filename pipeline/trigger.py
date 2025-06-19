import json
import boto3
import os

stepfunctions = boto3.client('stepfunctions')

def lambda_handler(event, context):
    """Trigger the Step Functions pipeline"""
    
    try:
        # Parse the incoming request
        body = json.loads(event['body'])
        
        # Start the Step Functions execution
        response = stepfunctions.start_execution(
            stateMachineArn=os.environ['STATE_MACHINE_ARN'],
            input=json.dumps(body)
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'execution_arn': response['executionArn'],
                'message': 'Pipeline started successfully'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }