#!/bin/bash

# Set variables
TABLE_NAME="LLM_item_validation_results"
REGION="us-east-1"

echo "Creating DynamoDB table: $TABLE_NAME"

# Create the table
aws dynamodb create-table \
    --table-name $TABLE_NAME \
    --attribute-definitions \
        AttributeName=QuestionId,AttributeType=S \
    --key-schema \
        AttributeName=QuestionId,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION \
    --tags Key=Environment,Value=Production

# Wait for table to be created
echo "Waiting for table to be created..."
aws dynamodb wait table-exists \
    --table-name $TABLE_NAME \
    --region $REGION

# Verify table creation
echo "Verifying table creation..."
aws dynamodb describe-table \
    --table-name $TABLE_NAME \
    --region $REGION

echo "Table creation complete!" 