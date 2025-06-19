import json
import re
import time
from typing import Dict, Any

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Analyzes user input to determine complexity and processing requirements
    """
    start_time = time.time()

    # Extract input from event
    user_input = event.get('input', '')
    if not user_input:
        raise ValueError("No input provided")
    
    print(f"Analyzing input: {user_input[:100]}...")
    
    # Perform analysis
    analysis = analyze_input(user_input)
    
    # Calculate processing time
    processing_time = (time.time() - start_time) * 1000
    
    print(f"Analysis complete in {processing_time:.2f}ms")
    print(f"Complexity: {analysis['complexity']}")
    
    return {
        'statusCode': 200,
        'analysis': analysis,
        'input_length': len(user_input),
        'processing_time_ms': round(processing_time, 2),
        'timestamp': time.time()
    }
    

def analyze_input(user_input: str) -> Dict[str, Any]:
    """
    Analyze input text to determine complexity and requirements
    """
    # Basic metrics
    word_count = len(user_input.split())
    char_count = len(user_input)
    sentence_count = len(re.split(r'[.!?]+', user_input))
    
    # Complexity indicators
    complexity_score = 0
    category = "general"
    
    # Length-based complexity
    if char_count > 1000:
        complexity_score += 3
    elif char_count > 500:
        complexity_score += 2
    elif char_count > 100:
        complexity_score += 1
    
    # Content-based complexity
    technical_keywords = [
        'algorithm', 'machine learning', 'neural network', 'database', 
        'programming', 'code', 'function', 'api', 'architecture',
        'optimization', 'analysis', 'statistics', 'model', 'prediction'
    ]
    
    creative_keywords = [
        'story', 'poem', 'creative', 'narrative', 'character',
        'plot', 'write', 'imagine', 'fiction', 'essay'
    ]
    
    research_keywords = [
        'research', 'study', 'analysis', 'compare', 'evaluate',
        'investigate', 'examine', 'report', 'survey', 'data'
    ]
    
    # Categorize and score
    user_input_lower = user_input.lower()
    
    if any(keyword in user_input_lower for keyword in technical_keywords):
        category = "technical"
        complexity_score += 2
    elif any(keyword in user_input_lower for keyword in creative_keywords):
        category = "creative"
        complexity_score += 1
    elif any(keyword in user_input_lower for keyword in research_keywords):
        category = "research"
        complexity_score += 3
    
    # Question complexity
    if '?' in user_input:
        question_count = user_input.count('?')
        if question_count > 2:
            complexity_score += 2
        elif question_count > 1:
            complexity_score += 1
    
    # Multi-part requests
    if any(indicator in user_input_lower for indicator in ['and', 'also', 'additionally', 'furthermore', 'moreover']):
        complexity_score += 1
    
    # Determine final complexity level
    if complexity_score >= 6:
        complexity = "high"
        confidence = 0.9
    elif complexity_score >= 3:
        complexity = "medium"
        confidence = 0.8
    else:
        complexity = "low"
        confidence = 0.7
    
    # Processing requirements based on complexity
    processing_requirements = {
        "low": {"cpu": "low", "memory": "low", "estimated_time": 2000},
        "medium": {"cpu": "medium", "memory": "medium", "estimated_time": 5000},
        "high": {"cpu": "high", "memory": "high", "estimated_time": 10000}
    }
    
    return {
        'complexity': complexity,
        'category': category,
        'confidence': confidence,
        'metrics': {
            'word_count': word_count,
            'char_count': char_count,
            'sentence_count': sentence_count,
            'complexity_score': complexity_score
        },
        'processing_requirements': processing_requirements[complexity],
        'features': {
            'has_questions': '?' in user_input,
            'multi_part': any(indicator in user_input_lower for indicator in ['and', 'also', 'additionally']),
            'technical_content': any(keyword in user_input_lower for keyword in technical_keywords),
            'creative_content': any(keyword in user_input_lower for keyword in creative_keywords)
        }
    }