import json
import boto3
import time
import os
from datetime import datetime
from decimal import Decimal

# Initialize AWS services
dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')

# Get table name from environment variable
table_name = os.environ.get('PIPELINE_LOG_TABLE', 'PipelineLogs')
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    """
    Logs pipeline execution data to DynamoDB and CloudWatch
    """
    print(f"Logging to table: {table_name}")
    
    # Extract execution data from Step Functions event
    execution_data = extract_execution_data(event)
    
    # Log to DynamoDB
    log_to_dynamodb(execution_data)
    
    # Send metrics to CloudWatch
    send_cloudwatch_metrics(execution_data)
    
    print(f"Successfully logged execution: {execution_data['execution_id']}")
    
    return {
        'statusCode': 200,
        'message': 'Logging completed successfully',
        'execution_id': execution_data['execution_id']
    }
        

def extract_execution_data(event):
    """
    Extract and normalize execution data from Step Functions event
    """
    timestamp = datetime.utcnow()
    execution_id = f"exec_{int(timestamp.timestamp())}"
    
    # Default values
    execution_data = {
        'execution_id': execution_id,
        'timestamp': timestamp.isoformat(),
        'date': timestamp.strftime('%Y-%m-%d'),
        'hour': timestamp.strftime('%Y-%m-%dT%H'),
        'input': '',
        'input_length': 0,
        'output': '',
        'output_length': 0,
        'success': True,
        'total_processing_time_ms': 0,
        'input_analysis_time_ms': 0,
        'response_enhancement_time_ms': 0,
        'complexity': 'unknown',
        'category': 'general',
        'quality_score': 0.0,
        'error_type': None,
        'error_message': None
    }
    
    # Extract input data
    if 'input' in event:
        execution_data['input'] = str(event['input'])
        execution_data['input_length'] = len(execution_data['input'])
    
    # Extract analysis data
    if 'analysis' in event:
        analysis = event['analysis']
        execution_data['complexity'] = analysis.get('complexity', 'unknown')
        execution_data['category'] = analysis.get('category', 'general')
        execution_data['input_analysis_time_ms'] = analysis.get('processing_time_ms', 0)
    
    # Extract enhancement data
    if 'enhanced_response' in event:
        enhanced = event['enhanced_response']
        execution_data['output'] = enhanced.get('content', '')
        execution_data['output_length'] = len(execution_data['output'])
        execution_data['quality_score'] = enhanced.get('quality_score', 0.0)
        execution_data['response_enhancement_time_ms'] = enhanced.get('processing_time_ms', 0)
    
    # Calculate total processing time
    execution_data['total_processing_time_ms'] = (
        execution_data['input_analysis_time_ms'] + 
        execution_data['response_enhancement_time_ms']
    )
    
    # Check for errors
    if 'error' in event or event.get('statusCode', 200) >= 400:
        execution_data['success'] = False
        execution_data['error_message'] = event.get('error', 'Unknown error')
        execution_data['error_type'] = classify_error(execution_data['error_message'])
    
    print(f"Extracted execution data for {execution_id}")
    print(f"• Input length: {execution_data['input_length']}")
    print(f"• Complexity: {execution_data['complexity']}")
    print(f"• Success: {execution_data['success']}")
    print(f"• Total time: {execution_data['total_processing_time_ms']}ms")
    
    return execution_data

def log_to_dynamodb(execution_data):
    """
    Store execution data in DynamoDB
    """
    # Convert float values to Decimal for DynamoDB
    item = {}
    for key, value in execution_data.items():
        if isinstance(value, float):
            item[key] = Decimal(str(value))
        else:
            item[key] = value
    
    # Write to DynamoDB
    table.put_item(Item=item)
    print(f"Logged to DynamoDB: {execution_data['execution_id']}")


def send_cloudwatch_metrics(execution_data):
    """
    Send custom metrics to CloudWatch
    """
    metrics = []
    
    # Basic metrics
    metrics.extend([
        {
            'MetricName': 'ExecutionCount',
            'Value': 1,
            'Unit': 'Count',
            'Dimensions': [
                {'Name': 'Complexity', 'Value': execution_data['complexity']},
                {'Name': 'Category', 'Value': execution_data['category']}
            ]
        },
        {
            'MetricName': 'ProcessingTime',
            'Value': execution_data['total_processing_time_ms'],
            'Unit': 'Milliseconds',
            'Dimensions': [
                {'Name': 'Complexity', 'Value': execution_data['complexity']}
            ]
        },
        {
            'MetricName': 'InputLength',
            'Value': execution_data['input_length'],
            'Unit': 'Count',
            'Dimensions': [
                {'Name': 'Category', 'Value': execution_data['category']}
            ]
        },
        {
            'MetricName': 'OutputLength',
            'Value': execution_data['output_length'],
            'Unit': 'Count'
        }
    ])
    
    # Success/Error metrics
    if execution_data['success']:
        metrics.append({
            'MetricName': 'SuccessfulExecutions',
            'Value': 1,
            'Unit': 'Count'
        })
        
        if execution_data['quality_score'] > 0:
            metrics.append({
                'MetricName': 'QualityScore',
                'Value': float(execution_data['quality_score']),
                'Unit': 'None'
            })
    else:
        metrics.extend([
            {
                'MetricName': 'FailedExecutions',
                'Value': 1,
                'Unit': 'Count'
            },
            {
                'MetricName': 'ErrorsByType',
                'Value': 1,
                'Unit': 'Count',
                'Dimensions': [
                    {'Name': 'ErrorType', 'Value': execution_data.get('error_type', 'unknown')}
                ]
            }
        ])
    
    # Stage-specific metrics
    if execution_data['input_analysis_time_ms'] > 0:
        metrics.append({
            'MetricName': 'InputAnalysisTime',
            'Value': execution_data['input_analysis_time_ms'],
            'Unit': 'Milliseconds'
        })
    
    if execution_data['response_enhancement_time_ms'] > 0:
        metrics.append({
            'MetricName': 'ResponseEnhancementTime',
            'Value': execution_data['response_enhancement_time_ms'],
            'Unit': 'Milliseconds'
        })
    
    # Send metrics to CloudWatch
    cloudwatch.put_metric_data(
        Namespace='AIPipeline',
        MetricData=metrics
    )
    
    print(f"Sent {len(metrics)} metrics to CloudWatch")


def classify_error(error_message):
    """
    Classify error type based on error message
    """
    error_message_lower = error_message.lower()
    
    if 'timeout' in error_message_lower:
        return 'timeout'
    elif 'memory' in error_message_lower or 'out of memory' in error_message_lower:
        return 'memory'
    elif 'permission' in error_message_lower or 'access denied' in error_message_lower:
        return 'permission'
    elif 'validation' in error_message_lower or 'invalid' in error_message_lower:
        return 'validation'
    elif 'network' in error_message_lower or 'connection' in error_message_lower:
        return 'network'
    elif 'rate limit' in error_message_lower or 'throttling' in error_message_lower:
        return 'rate_limit'
    else:
        return 'unknown'