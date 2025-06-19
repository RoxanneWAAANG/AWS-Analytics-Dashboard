import boto3

def create_enhanced_alarms():
    cloudwatch = boto3.client('cloudwatch')
    
    # High error rate alarm
    cloudwatch.put_metric_alarm(
        AlarmName='AI-Pipeline-High-Error-Rate',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=2,
        MetricName='ErrorRate',
        Namespace='AI-Pipeline/Analytics',
        Period=300,  # 5 minutes
        Statistic='Average',
        Threshold=5.0,  # 5% error rate
        ActionsEnabled=True,
        AlarmActions=[
            'arn:aws:sns:YOUR_REGION:YOUR_ACCOUNT:pipeline-alerts'  # Replace with your SNS topic
        ],
        AlarmDescription='Alert when error rate exceeds 5%'
    )
    
    # High latency alarm  
    cloudwatch.put_metric_alarm(
        AlarmName='AI-Pipeline-High-Latency',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=3,
        MetricName='ProcessingTime',
        Namespace='AI-Pipeline/Analytics',
        Period=300,
        Statistic='Average',
        Threshold=5000,  # 5 seconds
        ActionsEnabled=True,
        AlarmActions=[
            'arn:aws:sns:YOUR_REGION:YOUR_ACCOUNT:pipeline-alerts'
        ],
        AlarmDescription='Alert when average processing time exceeds 5 seconds'
    )

if __name__ == '__main__':
    create_enhanced_alarms()