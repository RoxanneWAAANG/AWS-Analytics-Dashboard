import json
import time
from datetime import datetime

def lambda_handler(event, context):
    """Enhanced input analyzer with timing metrics"""
    
    # Capture start time for metrics
    start_time = time.time()
    
    # Input analysis logic
    message = event.get('message', '')
    
    # Analyze the input
    word_count = len(message.split())
    char_count = len(message)
    
    # Determine complexity
    if word_count > 20 or '?' in message:
        complexity = 'high'
    elif word_count > 10:
        complexity = 'medium'
    else:
        complexity = 'low'
    
    # Check for keywords (your existing logic)
    technical_keywords = ['algorithm', 'machine learning', 'AI', 'database', 'API']
    has_technical_terms = any(keyword.lower() in message.lower() for keyword in technical_keywords)
    
    # Calculate processing time
    processing_time_ms = (time.time() - start_time) * 1000
    
    # Create analysis result
    analysis = {
        'complexity': complexity,
        'word_count': word_count,
        'char_count': char_count,
        'has_technical_terms': has_technical_terms,
        'requires_detailed_response': complexity == 'high' or has_technical_terms,
        # Include processing time in analysis
        'analysis_processing_time_ms': processing_time_ms
    }
    
    # Include timing info in the response for the logger
    return {
        **event,
        'analysis': analysis,
        'stage_metrics': {
            'stage': 'input_analysis',
            'processing_time_ms': processing_time_ms,
            'input_length': char_count,
            'output_length': len(str(analysis)),
            'success': True,
            'timestamp': datetime.utcnow().isoformat()
        }
    }