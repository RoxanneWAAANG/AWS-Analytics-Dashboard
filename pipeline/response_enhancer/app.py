import json
import time
import random
from typing import Dict, Any

def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    Enhances AI responses based on input analysis and user requirements
    """
    start_time = time.time()
    
    try:
        # Extract data from previous steps
        input_text = event.get('input', '')
        analysis = event.get('analysis', {})
        base_response = event.get('base_response', '')
        
        if not input_text or not analysis:
            raise ValueError("Missing required input or analysis data")
        
        print(f"Enhancing response for {analysis.get('complexity', 'unknown')} complexity input")
        
        # Perform enhancement
        enhanced_response = enhance_response(input_text, analysis, base_response)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        print(f"Enhancement complete in {processing_time:.2f}ms")
        print(f"Enhanced response length: {len(enhanced_response['content'])} characters")
        
        return {
            'statusCode': 200,
            'enhanced_response': enhanced_response,
            'processing_time_ms': round(processing_time, 2),
            'timestamp': time.time()
        }
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        error_msg = f"Response enhancement failed: {str(e)}"
        print(f"{error_msg}")
        
        return {
            'statusCode': 500,
            'error': error_msg,
            'enhanced_response': {
                'content': base_response or "I apologize, but I encountered an error while processing your request.",
                'enhancements': [],
                'quality_score': 0.1
            },
            'processing_time_ms': round(processing_time, 2),
            'timestamp': time.time()
        }

def enhance_response(input_text: str, analysis: Dict[str, Any], base_response: str) -> Dict[str, Any]:
    """
    Enhance the response based on input analysis
    """
    complexity = analysis.get('complexity', 'medium')
    category = analysis.get('category', 'general')
    features = analysis.get('features', {})
    
    # Start with base response or generate a mock response
    if not base_response:
        base_response = generate_mock_response(input_text, complexity, category)
    
    enhanced_content = base_response
    enhancements = []
    
    # Apply complexity-based enhancements
    if complexity == 'high':
        enhanced_content = add_detailed_explanations(enhanced_content)
        enhancements.append('detailed_explanations')
        
        enhanced_content = add_examples(enhanced_content, category)
        enhancements.append('examples')
        
        enhanced_content = add_structured_format(enhanced_content)
        enhancements.append('structured_format')
    
    elif complexity == 'medium':
        enhanced_content = add_moderate_detail(enhanced_content)
        enhancements.append('moderate_detail')
        
        if category in ['technical', 'research']:
            enhanced_content = add_examples(enhanced_content, category)
            enhancements.append('examples')
    
    # Apply category-specific enhancements
    if category == 'technical':
        enhanced_content = add_technical_formatting(enhanced_content)
        enhancements.append('technical_formatting')
    
    elif category == 'creative':
        enhanced_content = add_creative_elements(enhanced_content)
        enhancements.append('creative_elements')
    
    elif category == 'research':
        enhanced_content = add_research_structure(enhanced_content)
        enhancements.append('research_structure')
    
    # Apply feature-based enhancements
    if features.get('has_questions'):
        enhanced_content = add_qa_structure(enhanced_content)
        enhancements.append('qa_structure')
    
    if features.get('multi_part'):
        enhanced_content = add_section_headers(enhanced_content)
        enhancements.append('section_headers')
    
    # Calculate quality score
    quality_score = calculate_quality_score(enhanced_content, enhancements, complexity)
    
    # Add final polish
    enhanced_content = add_final_polish(enhanced_content, complexity)
    enhancements.append('final_polish')
    
    return {
        'content': enhanced_content,
        'enhancements': enhancements,
        'quality_score': quality_score,
        'original_length': len(base_response),
        'enhanced_length': len(enhanced_content),
        'improvement_factor': len(enhanced_content) / max(len(base_response), 1)
    }

def generate_mock_response(input_text: str, complexity: str, category: str) -> str:
    """Generate a base response for demonstration purposes"""
    responses = {
        'technical': f"Here's a technical response to your query about: {input_text[:50]}...",
        'creative': f"Let me help you with this creative request: {input_text[:50]}...",
        'research': f"Based on research and analysis of: {input_text[:50]}...",
        'general': f"Thank you for your question about: {input_text[:50]}..."
    }
    
    base = responses.get(category, responses['general'])
    
    if complexity == 'high':
        base += " This is a complex topic that requires detailed explanation."
    elif complexity == 'medium':
        base += " Let me provide you with a comprehensive answer."
    else:
        base += " Here's a straightforward response."
    
    return base

def add_detailed_explanations(content: str) -> str:
    """Add detailed explanations for high complexity responses"""
    return content + "\n\n**Detailed Explanation:**\nThis topic involves multiple interconnected concepts that build upon each other to form a comprehensive understanding."

def add_examples(content: str, category: str) -> str:
    """Add relevant examples based on category"""
    examples = {
        'technical': "\n\n**Example:**\n```python\n# Sample code implementation\ndef example_function():\n    return 'This demonstrates the concept'\n```",
        'research': "\n\n**Example Study:**\nFor instance, a 2023 study demonstrated similar findings when researchers analyzed comparable data sets.",
        'creative': "\n\n**Example:**\nImagine a scenario where the main character faces this exact challenge - how would they overcome it?",
        'general': "\n\n**Example:**\nTo illustrate this point, consider how this applies in everyday situations."
    }
    
    return content + examples.get(category, examples['general'])

def add_structured_format(content: str) -> str:
    """Add structured formatting with headers and bullets"""
    return f"## Overview\n{content}\n\n## Key Points\n• Main concept explained\n• Supporting details provided\n• Practical applications considered"

def add_moderate_detail(content: str) -> str:
    """Add moderate level of detail"""
    return content + "\n\nAdditional context: This builds on fundamental principles while addressing your specific needs."

def add_technical_formatting(content: str) -> str:
    """Add technical formatting elements"""
    return content + "\n\n**Technical Notes:**\n- Implementation considerations\n- Performance implications\n- Best practices"

def add_creative_elements(content: str) -> str:
    """Add creative elements and inspiration"""
    return content + "\n\n*Creative Inspiration:* Consider exploring different perspectives and let your imagination guide the development of ideas."

def add_research_structure(content: str) -> str:
    """Add research-oriented structure"""
    return content + "\n\n**Research Framework:**\n1. Problem definition\n2. Analysis methodology\n3. Findings and implications"

def add_qa_structure(content: str) -> str:
    """Add Q&A structure for responses with questions"""
    return content + "\n\n**Q&A Section:**\n**Q:** What are the key considerations?\n**A:** The main factors to consider include context, requirements, and desired outcomes."

def add_section_headers(content: str) -> str:
    """Add section headers for multi-part content"""
    return f"# Response Overview\n\n{content}\n\n## Additional Considerations\nFurther details and related topics are explored here."

def add_final_polish(content: str, complexity: str) -> str:
    """Add final polish and conclusion"""
    conclusions = {
        'high': "\n\n**Conclusion:**\nThis comprehensive analysis provides a thorough foundation for understanding and applying these concepts effectively.",
        'medium': "\n\n**Summary:**\nThese key points should help you move forward with confidence and clarity.",
        'low': "\n\nI hope this helps clarify things for you!"
    }
    
    return content + conclusions.get(complexity, conclusions['medium'])

def calculate_quality_score(content: str, enhancements: list, complexity: str) -> float:
    """Calculate quality score based on content and enhancements"""
    base_score = 0.5
    
    # Length bonus
    if len(content) > 500:
        base_score += 0.2
    elif len(content) > 200:
        base_score += 0.1
    
    # Enhancement bonus
    enhancement_score = min(len(enhancements) * 0.05, 0.3)
    base_score += enhancement_score
    
    # Complexity alignment bonus
    complexity_bonus = {
        'high': 0.1,
        'medium': 0.05,
        'low': 0.02
    }
    base_score += complexity_bonus.get(complexity, 0)
    
    return min(base_score, 1.0)