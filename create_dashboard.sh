#!/bin/bash

# Create CloudWatch Dashboard using AWS CLI
# This is an alternative to the Python script

echo "Creating AI Pipeline Dashboard..."

# First, get your Step Functions ARN
STATE_MACHINE_ARN=$(aws stepfunctions list-state-machines --query 'stateMachines[?name==`AIPipeline`].stateMachineArn' --output text)
echo "State Machine ARN: $STATE_MACHINE_ARN"

# Create the dashboard JSON
cat > dashboard.json << EOF
{
  "widgets": [
    {
      "type": "metric",
      "x": 0,
      "y": 0,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          ["AWS/StepFunctions", "ExecutionsSucceeded", "StateMachineArn", "$STATE_MACHINE_ARN"],
          [".", "ExecutionsFailed", ".", "."],
          [".", "ExecutionsAborted", ".", "."],
          [".", "ExecutionsTimedOut", ".", "."]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "us-east-2",
        "title": "Pipeline Execution Status",
        "period": 300,
        "stat": "Sum"
      }
    },
    {
      "type": "metric",
      "x": 12,
      "y": 0,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          ["AWS/StepFunctions", "ExecutionTime", "StateMachineArn", "$STATE_MACHINE_ARN"]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "us-east-2",
        "title": "Pipeline Execution Time",
        "period": 300,
        "stat": "Average"
      }
    },
    {
      "type": "metric",
      "x": 0,
      "y": 6,
      "width": 24,
      "height": 6,
      "properties": {
        "metrics": [
          ["AWS/Lambda", "Duration", "FunctionName", "ai-pipeline-InputAnalyzerFunction"],
          [".", ".", ".", "ai-pipeline-ResponseEnhancerFunction"],
          [".", ".", ".", "ai-pipeline-PipelineLoggerFunction"],
          [".", ".", ".", "ai-pipeline-PipelineFunction"]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "us-east-2",
        "title": "Lambda Function Performance",
        "period": 300,
        "stat": "Average"
      }
    }
  ]
}
EOF

# Create the dashboard
aws cloudwatch put-dashboard \
  --dashboard-name "AI Pipeline Dashboard" \
  --dashboard-body file://dashboard.json

# Clean up
rm dashboard.json

echo "Dashboard created successfully!"
echo "Dashboard URL: https://us-east-2.console.aws.amazon.com/cloudwatch/home?region=us-east-2#dashboards:name=AIPipelineDashboard"