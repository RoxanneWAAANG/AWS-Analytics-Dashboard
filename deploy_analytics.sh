#!/bin/bash

echo "Deploying Analytics Dashboard..."

# Deploy SAM template
sam build
sam deploy --guided

# Upload dashboard to S3
aws s3 cp dashboard/index.html s3://YOUR-STACK-NAME-dashboard/ --acl public-read

# Get the analytics API endpoint
API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name ai-pipeline \
  --query 'Stacks[0].Outputs[?OutputKey==`AnalyticsApiEndpoint`].OutputValue' \
  --output text)

echo "Dashboard URL: http://YOUR-STACK-NAME-dashboard.s3-website-YOUR-REGION.amazonaws.com"
echo "Analytics API: $API_ENDPOINT"
echo "Update the API_ENDPOINT in your index.html file"