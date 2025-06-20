import json
import boto3
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('PIPELINE_LOG_TABLE', 'PipelineLogs')


def lambda_handler(event, context):
    """
    Analytics API for AI Pipeline data with enhanced error handling
    """
    print(f"Analytics API called with table: {table_name}")
    print(f"Event: {json.dumps(event)}")
    
    # Initialize table
    table = dynamodb.Table(table_name)
    
    
    table_info = table.table_status
    print(f"Table status: {table_info}")
        
    # Extract query parameters
    query_params = event.get('queryStringParameters') or {}
    hours = int(query_params.get('hours', 24))
    
    print(f"Fetching data for last {hours} hours")
    
    # Calculate time window
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    # Query data
    analytics_data = get_analytics_data(table, start_time, end_time)
    
    print(f"Found {analytics_data['summary']['total_executions']} executions")
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET,OPTIONS'
        },
        'body': json.dumps(analytics_data, cls=DecimalEncoder)
    }


def get_analytics_data(table, start_time, end_time):
    """
    Fetch and analyze pipeline data with better error handling
    """
    # Try to scan the table (for now, since we might not have much data)
    response = table.scan()
    items = response.get('Items', [])
    
    print(f"Raw items found: {len(items)}")
    
    # If no items, return empty analytics
    if not items:
        return {
            'summary': {
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'success_rate': 0.0,
                'average_processing_time': 0.0
            },
            'complexity_breakdown': {},
            'category_breakdown': {},
            'recent_executions': [],
            'time_window': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'hours': (end_time - start_time).total_seconds() / 3600
            },
            'message': 'No pipeline executions found. Try running a pipeline first.'
        }
    
    # Filter items by time (if timestamp exists)
    filtered_items = []
    for item in items:
        if 'timestamp' in item:
            item_time = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
            if start_time <= item_time <= end_time:
                filtered_items.append(item)
        else:
            # Include items without timestamp for now
            filtered_items.append(item)
    
    print(f"Filtered items: {len(filtered_items)}")
    
    # Analyze data
    return analyze_pipeline_data(filtered_items, start_time, end_time)
    

def analyze_pipeline_data(items, start_time, end_time):
    """
    Analyze pipeline execution data
    """
    if not items:
        return {
            'summary': {
                'total_executions': 0,
                'successful_executions': 0,
                'failed_executions': 0,
                'success_rate': 0.0,
                'average_processing_time': 0.0
            },
            'message': 'No data in time window'
        }
    
    total_executions = len(items)
    successful_executions = sum(1 for item in items if item.get('success', True))
    failed_executions = total_executions - successful_executions
    success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
    
    # Calculate average processing time
    processing_times = [
        float(item.get('total_processing_time_ms', 0)) 
        for item in items 
        if item.get('total_processing_time_ms', 0) > 0
    ]
    avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
    
    # Complexity breakdown
    complexity_breakdown = {}
    for item in items:
        complexity = item.get('complexity', 'unknown')
        complexity_breakdown[complexity] = complexity_breakdown.get(complexity, 0) + 1
    
    # Category breakdown
    category_breakdown = {}
    for item in items:
        category = item.get('category', 'general')
        category_breakdown[category] = category_breakdown.get(category, 0) + 1
    
    # Recent executions (last 10)
    recent_executions = []
    for item in sorted(items, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]:
        recent_executions.append({
            'execution_id': item.get('execution_id', 'unknown'),
            'timestamp': item.get('timestamp', ''),
            'complexity': item.get('complexity', 'unknown'),
            'category': item.get('category', 'general'),
            'success': item.get('success', True),
            'processing_time_ms': float(item.get('total_processing_time_ms', 0)),
            'input_length': int(item.get('input_length', 0)),
            'output_length': int(item.get('output_length', 0))
        })
    
    return {
        'summary': {
            'total_executions': total_executions,
            'successful_executions': successful_executions,
            'failed_executions': failed_executions,
            'success_rate': round(success_rate, 2),
            'average_processing_time': round(avg_processing_time, 2)
        },
        'complexity_breakdown': complexity_breakdown,
        'category_breakdown': category_breakdown,
        'recent_executions': recent_executions,
        'time_window': {
            'start': start_time.isoformat(),
            'end': end_time.isoformat(),
            'hours': round((end_time - start_time).total_seconds() / 3600, 1)
        }
    }


def create_error_response(status_code, message):
    """
    Create standardized error response
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'GET,OPTIONS'
        },
        'body': json.dumps({
            'error': message,
            'timestamp': datetime.utcnow().isoformat()
        })
    }


class DecimalEncoder(json.JSONEncoder):
    """
    Helper class to handle Decimal objects in JSON serialization
    """
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)