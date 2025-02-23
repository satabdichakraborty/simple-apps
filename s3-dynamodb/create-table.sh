#!/bin/bash

# Set your table name
DYNAMODB_TABLE_NAME="your-table-name"

# Create the table
aws dynamodb create-table \
    --table-name ${DYNAMODB_TABLE_NAME} \
    --attribute-definitions \
        AttributeName=QuestionId,AttributeType=S \
        AttributeName=CreatedDate,AttributeType=S \
    --key-schema \
        AttributeName=QuestionId,KeyType=HASH \
        AttributeName=CreatedDate,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST \
    --tags Key=Environment,Value=Production

# Wait for table to be created
aws dynamodb wait table-exists --table-name ${DYNAMODB_TABLE_NAME}

# Verify table creation
aws dynamodb describe-table --table-name ${DYNAMODB_TABLE_NAME} 