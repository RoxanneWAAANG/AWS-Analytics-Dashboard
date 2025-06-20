# Project3 -- AWS Analytics Dashboard

A serverless AI pipeline analytics system built with AWS SAM that processes, enhances, and analyzes user inputs through a multi-stage workflow.

## Architecture

- **API Gateway**: REST endpoints for triggering pipelines and accessing analytics
- **Step Functions**: Orchestrates the AI pipeline workflow
- **Lambda Functions**: Input analysis, response enhancement, logging, and analytics
- **DynamoDB**: Stores execution logs and metrics
- **CloudWatch**: Monitoring, alarms, and dashboards

## Prerequisites

- AWS CLI configured with appropriate permissions
- AWS SAM CLI installed
- Python 3.9+

## Deployment

1. Clone the repository:
```bash
git clone https://github.com/RoxanneWAAANG/AWS-Analytics-Dashboard.git
cd AWS-Analytics-Dashboard
```

2. Build the application:
```bash
sam build --template pipeline-template.yaml
```

3. Deploy to AWS:
```bash
sam deploy --guided
```

4. Note the API Gateway URLs from the deployment output.

## API Endpoints

### Trigger Pipeline
**POST** `/trigger`

Starts an AI pipeline execution.

**Request Body:**
```json
{
  "input": "Your text input here"
}
```

**Response:**
```json
{
  "message": "Pipeline execution started successfully",
  "execution_arn": "arn:aws:states:...",
  "request_id": "...",
  "status": "RUNNING"
}
```

### Analytics
**GET** `/analytics`

Retrieves pipeline execution analytics and metrics.

**Query Parameters:**
- `hours` (optional): Time window in hours (default: 24)

**Response:**
```json
{
  "summary": {
    "total_executions": 10,
    "successful_executions": 9,
    "failed_executions": 1,
    "success_rate": 90.0,
    "average_processing_time": 2500.5
  },
  "complexity_breakdown": {
    "high": 3,
    "medium": 5,
    "low": 2
  },
  "category_breakdown": {
    "technical": 4,
    "creative": 3,
    "general": 3
  },
  "recent_executions": [...],
  "time_window": {
    "start": "2025-06-19T10:00:00",
    "end": "2025-06-20T10:00:00",
    "hours": 24.0
  }
}
```

## Usage Examples

### Trigger a Pipeline
```bash
curl -X POST https://nb5nia3lf0.execute-api.us-east-2.amazonaws.com/Prod/trigger \
  -H "Content-Type: application/json" \
  -d '{"input": "Explain machine learning concepts"}'
```

### Get Analytics
```bash
# Get last 24 hours
curl https://nb5nia3lf0.execute-api.us-east-2.amazonaws.com/Prod/analytics

# Get last 6 hours
curl https://nb5nia3lf0.execute-api.us-east-2.amazonaws.com/Prod/analytics?hours=6
```

## Project Structure

```
├── pipeline/
│   ├── input_analyzer/
│   │   └── app.py           # Analyzes input complexity
│   ├── response_enhancer/
│   │   └── app.py           # Enhances responses based on analysis
│   ├── pipeline_logger/
│   │   └── app.py           # Logs execution data to DynamoDB
│   └── trigger.py           # Triggers Step Functions workflow
├── analytics/
│   └── app.py               # Analytics API endpoint
├── pipeline-template.yaml   # SAM template
└── README.md
```

## Pipeline Workflow

1. **Input Analysis**: Analyzes text complexity, category, and processing requirements
2. **Response Enhancement**: Enhances responses based on complexity and content type
3. **Logging**: Records execution metrics, performance data, and results in DynamoDB

## Monitoring

The deployment includes:

- **CloudWatch Dashboard**: Real-time metrics visualization
- **CloudWatch Alarms**: Alerts for high error rates and long execution times
- **SNS Topic**: Notification system for alerts

Access the dashboard through the AWS Console or use the dashboard URL provided in deployment outputs.

## Data Storage

Execution logs are stored in DynamoDB with the following key metrics:
- Execution ID and timestamp
- Input/output lengths and processing times
- Success/failure status and error details
- Complexity and category classifications
- Quality scores and performance metrics

## Troubleshooting

### Analytics API Returns "Internal Server Error"
1. Check CloudWatch logs:
```bash
aws logs filter-log-events \
  --log-group-name "/aws/lambda/analytics-dashboard-analytics-api" \
  --start-time <timestamp>
```

2. Verify DynamoDB table access:
```bash
aws dynamodb scan --table-name analytics-dashboard-PipelineLogs --max-items 3
```

### Pipeline Execution Fails
1. Check Step Functions execution status:
```bash
aws stepfunctions describe-execution --execution-arn <execution-arn>
```

2. Review individual Lambda function logs in CloudWatch.

### No Data in Analytics
- Wait for pipeline executions to complete
- Verify Step Functions are successfully writing to DynamoDB
- Check that the analytics time window includes recent executions

## Cost Optimization

The system uses:
- DynamoDB on-demand pricing
- Lambda with pay-per-use
- API Gateway with request-based pricing
- Step Functions standard workflows

## Security

- All Lambda functions use least-privilege IAM roles
- API Gateway endpoints include CORS configuration
- DynamoDB table includes point-in-time recovery
- No authentication required (suitable for development/testing)

## Contributing

1. Make changes to the appropriate Lambda function
2. Test locally using `sam local invoke`
3. Deploy changes using `sam deploy`
4. Verify functionality through API endpoints
