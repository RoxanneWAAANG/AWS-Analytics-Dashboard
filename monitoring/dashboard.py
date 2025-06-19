import boto3
import json

cloudwatch = boto3.client('cloudwatch')

dashboard_body = {
    "widgets": [
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/StepFunctions", "ExecutionsSucceeded", "StateMachineArn", "YOUR_STATE_MACHINE_ARN"],
                    [".", "ExecutionsFailed", ".", "."],
                    [".", "ExecutionTime", ".", "."]
                ],
                "period": 300,
                "stat": "Sum",
                "region": "us-east-2",
                "title": "Pipeline Execution Metrics"
            }
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/Lambda", "Duration", "FunctionName", "InputAnalyzerFunction"],
                    [".", ".", ".", "ResponseEnhancerFunction"],
                    [".", ".", ".", "PipelineLoggerFunction"]
                ],
                "period": 300,
                "stat": "Average",
                "region": "us-east-2",
                "title": "Lambda Performance"
            }
        }
    ]
}

cloudwatch.put_dashboard(
    DashboardName='AIPipelineDashboard',
    DashboardBody=json.dumps(dashboard_body)
)