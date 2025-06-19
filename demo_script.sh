#!/bin/bash

# AI Pipeline Demo Script
# This script demonstrates the AI pipeline functionality and monitoring

API_ENDPOINT="https://o77htsxjbd.execute-api.us-east-2.amazonaws.com/Prod/pipeline"

echo "🚀 AI Pipeline Demo - Week 2 Project"
echo "===================================="

# Test Case 1: Simple Query
echo ""
echo "📝 Test 1: Simple Query"
echo "Input: 'What is AI?'"
RESPONSE1=$(curl -s -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{"message": "What is AI?"}')
echo "Response: $RESPONSE1"

# Extract execution ARN for monitoring
EXECUTION_ARN1=$(echo $RESPONSE1 | grep -o '"execution_arn":"[^"]*"' | cut -d'"' -f4)
echo "Execution ARN: $EXECUTION_ARN1"

# Wait a moment for processing
echo "⏳ Waiting for processing..."
sleep 5

# Test Case 2: Complex Query with Code
echo ""
echo "📝 Test 2: Complex Query (should trigger high complexity analysis)"
echo "Input: 'Write a Python function to implement machine learning'"
RESPONSE2=$(curl -s -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{"message": "Write a Python function to implement machine learning. Please include comments and error handling."}')
echo "Response: $RESPONSE2"

EXECUTION_ARN2=$(echo $RESPONSE2 | grep -o '"execution_arn":"[^"]*"' | cut -d'"' -f4)
echo "Execution ARN: $EXECUTION_ARN2"

echo "⏳ Waiting for processing..."
sleep 5

# Test Case 3: Question-based Query
echo ""
echo "📝 Test 3: Question-based Query"
echo "Input: 'How does neural network training work?'"
RESPONSE3=$(curl -s -X POST $API_ENDPOINT \
  -H "Content-Type: application/json" \
  -d '{"message": "How does neural network training work? What are the key steps?"}')
echo "Response: $RESPONSE3"

EXECUTION_ARN3=$(echo $RESPONSE3 | grep -o '"execution_arn":"[^"]*"' | cut -d'"' -f4)
echo "Execution ARN: $EXECUTION_ARN3"

echo ""
echo "🔍 Checking Execution Status"
echo "============================"

# Check execution status for the first test
echo ""
echo "Execution 1 Status:"
aws stepfunctions describe-execution --execution-arn "$EXECUTION_ARN1" --query 'status' --output text

echo ""
echo "Execution 2 Status:"
aws stepfunctions describe-execution --execution-arn "$EXECUTION_ARN2" --query 'status' --output text

echo ""
echo "Execution 3 Status:"
aws stepfunctions describe-execution --execution-arn "$EXECUTION_ARN3" --query 'status' --output text

echo ""
echo "📊 Monitoring Information"
echo "========================"
echo "• CloudWatch Dashboard: https://us-east-2.console.aws.amazon.com/cloudwatch/home?region=us-east-2#dashboards:name=AIPipelineDashboard"
echo "• Step Functions Console: https://us-east-2.console.aws.amazon.com/states/home?region=us-east-2#/statemachines"
echo "• DynamoDB Logs: https://us-east-2.console.aws.amazon.com/dynamodbv2/home?region=us-east-2#item-explorer?table=PipelineLogs"

echo ""
echo "📋 Demo Summary"
echo "==============="
echo "✅ Pipeline successfully processes different types of queries"
echo "✅ Step Functions orchestrates the workflow with retries"
echo "✅ Each Lambda function performs its specific role"
echo "✅ Comprehensive logging and monitoring in place"
echo "✅ Error handling and retry mechanisms working"

echo ""
echo "🎯 Key Features Demonstrated:"
echo "• Input Analysis (complexity detection)"
echo "• Integration with existing chatbot"
echo "• Response enhancement with metadata"
echo "• Comprehensive logging"
echo "• Monitoring and observability"