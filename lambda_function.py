import boto3
import pandas as pd
import io
import logging
import time
import os
from typing import Dict, Any
from datetime import datetime
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get environment variables
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
DYNAMODB_TABLE_NAME = os.environ.get('DYNAMODB_TABLE_NAME')

if not S3_BUCKET_NAME:
    raise ValueError("S3_BUCKET_NAME environment variable is not set")
if not DYNAMODB_TABLE_NAME:
    raise ValueError("DYNAMODB_TABLE_NAME environment variable is not set")

def setup_aws_clients():
    """Initialize AWS service clients"""
    try:
        s3_client = boto3.client('s3')
        dynamodb = boto3.resource('dynamodb')
        return s3_client, dynamodb
    except Exception as e:
        logger.error(f"Failed to initialize AWS clients: {str(e)}")
        raise

def read_csv_from_s3(s3_client, bucket: str, key: str) -> pd.DataFrame:
    """Read CSV file from S3 and return DataFrame"""
    try:
        logger.info(f"Reading file {key} from bucket {bucket}")
        response = s3_client.get_object(Bucket=bucket, Key=key)
        csv_data = response['Body'].read().decode('utf-8')
        return pd.read_csv(io.StringIO(csv_data))
    except ClientError as e:
        logger.error(f"S3 operation failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Failed to process CSV file: {str(e)}")
        raise

def insert_to_dynamodb(table, items: list) -> Dict[str, int]:
    """Batch insert items to DynamoDB with error tracking"""
    success_count = 0
    error_count = 0
    
    for item in items:
        try:
            table.put_item(Item=item)
            success_count += 1
        except Exception as e:
            error_count += 1
            logger.error(f"Failed to insert item: {str(e)}\nItem: {item}")
    
    return {'success': success_count, 'errors': error_count}

def process_csv_row(row) -> Dict[str, str]:
    """Convert DataFrame row to DynamoDB item"""
    return {
        'QuestionId': str(row['QuestionId']),
        'Type': str(row['Type']),
        'Status': str(row['Status']),
        'Question': str(row['Question']),
        'Key': str(row['Key']),
        'Notes': str(row['Notes']),
        'Rationale': str(row['Rationale']),
        'CreatedDate': str(row['Created Date']),
        'CreatedBy': str(row['Created By']),
        'ResponseA': str(row['Response A']),
        'ResponseB': str(row['Response B']),
        'ResponseC': str(row['Response C']),
        'ResponseD': str(row['Response D']),
        'ResponseE': str(row['Response E']),
        'ResponseF': str(row['Response F']),
        'RationaleA': str(row['Rationale A']),
        'RationaleB': str(row['Rationale B']),
        'RationaleC': str(row['Rationale C']),
        'RationaleD': str(row['Rationale D']),
        'RationaleE': str(row['Rationale E']),
        'RationaleF': str(row['Rationale F']),
        'Topic': str(row['Topic']),
        'Knowledge': str(row['CLF-002-Knowledge-Skills']),
        'Tag': str(row['CLF-002-Tagging System']),
        'ProcessedAt': datetime.now().isoformat()
    }

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    start_time = time.time()
    logger.info("Starting CSV processing Lambda function")
    
    try:
        # Initialize AWS clients
        s3_client, dynamodb = setup_aws_clients()
        table = dynamodb.Table(DYNAMODB_TABLE_NAME)
        
        # Get S3 event details
        file_key = event['Records'][0]['s3']['object']['key']
        logger.info(f"Processing file: {file_key} from bucket: {S3_BUCKET_NAME}")
        
        # Read and process CSV file
        df = read_csv_from_s3(s3_client, S3_BUCKET_NAME, file_key)
        logger.info(f"Successfully read CSV file with {len(df)} rows")
        
        # Process rows and prepare items for DynamoDB
        items = [process_csv_row(row) for _, row in df.iterrows()]
        
        # Insert to DynamoDB
        results = insert_to_dynamodb(table, items)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Prepare response
        response = {
            'statusCode': 200,
            'body': {
                'message': 'File processing completed',
                'total_rows': len(df),
                'successful_inserts': results['success'],
                'failed_inserts': results['errors'],
                'processing_time_seconds': round(processing_time, 2)
            }
        }
        
        logger.info(f"Processing completed: {response}")
        return response
        
    except Exception as e:
        logger.error(f"Critical error during execution: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': {
                'message': 'Error processing file',
                'error': str(e),
                'processing_time_seconds': round(time.time() - start_time, 2)
            }
        } 