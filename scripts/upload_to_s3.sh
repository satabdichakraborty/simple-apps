#!/bin/bash

# Set variables
BUCKET_NAME="your-s3-bucket-name"
LOCAL_FILE_PATH="path/to/your/local/questions.csv"
S3_PATH="questions.csv"  # Destination path in S3
REGION="us-east-1"

echo "Uploading file to S3..."
echo "Source: $LOCAL_FILE_PATH"
echo "Destination: s3://$BUCKET_NAME/$S3_PATH"

# Upload file to S3
aws s3 cp $LOCAL_FILE_PATH "s3://$BUCKET_NAME/$S3_PATH" \
    --region $REGION

# Verify upload
echo "Verifying upload..."
aws s3 ls "s3://$BUCKET_NAME/$S3_PATH"

echo "Upload complete!" 