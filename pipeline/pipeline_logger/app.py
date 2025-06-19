import json
import boto3
import time
from datetime import datetime
from decimal import Decimal

# Initialize AWS services
dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')
table = dynamodb.Table('YOUR_LOGS_TABLE_NAME')

def lambda_handler(event, context):
    """Enhanced pipeline logger that captures timing metrics from all stages"""
    # Extract timing data from each stage
    input_metrics = event.get('stage_metrics', {})
    enhancement_metrics = event.get('enhanced_response', {}).get('metadata', {})
    
    # Calculate total pipeline processing time
    total_processing_time = 0
    stage_times = {}
    
    # Get timing from input analyzer
    if 'analysis' in event and 'analysis_processing_time_ms' in event['analysis']:
        input_time = event['analysis']['analysis_processing_time_ms']
        stage_times['input_analysis'] = input_time
        total_processing_time += input_time
    
    # Get timing from response enhancer
    if 'enhancement_processing_time_ms' in enhancement_metrics:
        enhancement_time = enhancement_metrics['enhancement_processing_time_ms']
        stage_times['response_enhancement'] = enhancement_time
        total_processing_time += enhancement_time
    
    # Create comprehensive log entry
    log_entry = {
        'execution_id': context.aws_request_id,
        'timestamp': datetime.utcnow().isoformat(),
        'date': datetime.utcnow().strftime('%Y-%m-%d'),
        'hour': datetime.utcnow().strftime('%Y-%m-%d-%H'),
        
        # Input metrics
        'input_message': event.get('message', ''),
        'input_length': len(event.get('message', '')),
        
        # Output metrics  
        'output_message': event.get('enhanced_response', {}).get('reply', ''),
        'output_length': len(event.get('enhanced_response', {}).get('reply', '')),
        
        # Performance metrics
        'total_processing_time_ms': Decimal(str(round(total_processing_time, 2))),
        'input_analysis_time_ms': Decimal(str(round(stage_times.get('input_analysis', 0), 2))),
        'response_enhancement_time_ms': Decimal(str(round(stage_times.get('response_enhancement', 0), 2))),
        
        # Analysis results
        'complexity': event.get('analysis', {}).get('complexity', 'unknown'),
        'has_technical_terms': event.get('analysis', {}).get('has_technical_terms', False),
        
        # Success/Error tracking
        'success': True,
        'error_type': None,
        'error_message': None
    }
    
    # Store in DynamoDB
    table.put_item(Item=log_entry)
    
    # Send metrics to CloudWatch
    send_cloudwatch_metrics(log_entry)
    
    print(f"Successfully logged execution: {context.aws_request_id}")
    print(f"Total processing time: {total_processing_time:.2f}ms")
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Logged successfully',
            'execution_id': context.aws_request_id,
            'processing_time_ms': total_processing_time
        })
    }


def send_cloudwatch_metrics(log_entry):
    """Send custom metrics to CloudWatch for monitoring"""
    metrics_data = [
        {
            'MetricName': 'TotalProcessingTime',
            'Value': float(log_entry['total_processing_time_ms']),
            'Unit': 'Milliseconds',
            'Dimensions': [
                {'Name': 'Complexity', 'Value': log_entry['complexity']}
            ]
        },
        {
            'MetricName': 'InputAnalysisTime', 
            'Value': float(log_entry['input_analysis_time_ms']),
            'Unit': 'Milliseconds'
        },
        {
            'MetricName': 'ResponseEnhancementTime',
            'Value': float(log_entry['response_enhancement_time_ms']), 
            'Unit': 'Milliseconds'
        },
        {
            'MetricName': 'RequestCount',
            'Value': 1,
            'Unit': 'Count',
            'Dimensions': [
                {'Name': 'Success', 'Value': str(log_entry['success'])}
            ]
        },
        {
            'MetricName': 'InputLength',
            'Value': log_entry['input_length'],
            'Unit': 'Count'
        },
        {
            'MetricName': 'OutputLength', 
            'Value': log_entry['output_length'],
            'Unit': 'Count'
        }
    ]
    
    # Send metrics in batches (CloudWatch has a 20 metric limit per call)
    cloudwatch.put_metric_data(
        Namespace='AI-Pipeline/Analytics',
        MetricData=metrics_data
    )
    
    print("CloudWatch metrics sent successfully")
