import json
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('YOUR_LOGS_TABLE_NAME')  # Replace with your table name

def lambda_handler(event, context):
    # Get last 24 hours of data
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
    
    try:
        # Query your DynamoDB table
        response = table.scan(
            FilterExpression=Key('timestamp').between(
                start_time.isoformat(),
                end_time.isoformat()
            )
        )
        
        items = response['Items']
        
        # Calculate analytics
        analytics = {
            'total_requests': len(items),
            'avg_processing_time': sum(float(item.get('processing_time_ms', 0)) for item in items) / max(len(items), 1),
            'success_rate': len([i for i in items if i.get('success', True)]) / max(len(items), 1) * 100,
            'hourly_data': calculate_hourly_metrics(items),
            'error_breakdown': calculate_errors(items)
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(analytics)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def calculate_hourly_metrics(items):
    hourly = {}
    for item in items:
        hour = item.get('hour', 'unknown')
        if hour not in hourly:
            hourly[hour] = {'count': 0, 'total_time': 0, 'errors': 0}
        
        hourly[hour]['count'] += 1
        hourly[hour]['total_time'] += float(item.get('processing_time_ms', 0))
        if not item.get('success', True):
            hourly[hour]['errors'] += 1
    
    return [
        {
            'hour': hour,
            'requests': data['count'],
            'avg_time': data['total_time'] / max(data['count'], 1),
            'error_rate': data['errors'] / max(data['count'], 1) * 100
        }
        for hour, data in sorted(hourly.items())
    ]

def calculate_errors(items):
    errors = {}
    for item in items:
        if not item.get('success', True):
            error_type = item.get('error_type', 'Unknown')
            errors[error_type] = errors.get(error_type, 0) + 1
    return errors