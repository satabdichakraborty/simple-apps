import boto3
import json
import os
import logging
from typing import Dict, List, Any
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get environment variables
TABLE_NAME = os.environ.get('TABLE_NAME')

def setup_dynamodb():
    """Initialize DynamoDB resource"""
    try:
        return boto3.resource('dynamodb')
    except Exception as e:
        logger.error(f"Failed to initialize DynamoDB: {str(e)}")
        raise

def format_question(item: Dict[str, Any]) -> Dict[str, Any]:
    """Format a question with its non-empty answers"""
    # Get all possible responses
    responses = {
        'A': item.get('ResponseA', ''),
        'B': item.get('ResponseB', ''),
        'C': item.get('ResponseC', ''),
        'D': item.get('ResponseD', ''),
        'E': item.get('ResponseE', ''),
        'F': item.get('ResponseF', '')
    }
    
    # Filter out empty responses
    non_empty_responses = {
        key: value for key, value in responses.items() 
        if value and value.strip()
    }
    
    # Format the question text with answers
    formatted_text = f"Question: {item.get('Question', '')}\n\n"
    for key, value in non_empty_responses.items():
        formatted_text += f"{key}) {value}\n"
    
    return {
        'QuestionId': item.get('QuestionId', ''),
        'FormattedText': formatted_text,
        'Type': item.get('Type', ''),
        'Status': item.get('Status', ''),
        'Key': item.get('Key', ''),
        'Topic': item.get('Topic', ''),
        'ResponseCount': len(non_empty_responses)
    }

def get_formatted_questions(table) -> List[Dict[str, Any]]:
    """Read and format questions from DynamoDB table"""
    try:
        response = table.scan()
        items = response.get('Items', [])
        
        # Format each question
        formatted_questions = []
        for item in items:
            formatted_question = format_question(item)
            formatted_questions.append(formatted_question)
            
            # Log each formatted question
            logger.info(f"\nQuestion ID: {formatted_question['QuestionId']}")
            logger.info(formatted_question['FormattedText'])
            logger.info(f"Response Count: {formatted_question['ResponseCount']}\n")
            
        return formatted_questions
        
    except ClientError as e:
        logger.error(f"DynamoDB operation failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error reading questions: {str(e)}")
        raise

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler"""
    logger.info("Starting Question Validator Lambda function")
    logger.info(f"Received event: {event}")
    
    try:
        # Validate environment variables
        if not TABLE_NAME:
            raise ValueError("TABLE_NAME environment variable is not set")
            
        # Initialize DynamoDB
        dynamodb = setup_dynamodb()
        table = dynamodb.Table(TABLE_NAME)
        
        # Get and format questions
        formatted_questions = get_formatted_questions(table)
        
        # Prepare response
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Questions validated successfully',
                'count': len(formatted_questions),
                'questions': formatted_questions
            }, indent=2)
        }
        
        logger.info(f"Successfully validated {len(formatted_questions)} questions")
        return response
        
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Configuration error',
                'error': str(ve)
            })
        }
    except Exception as e:
        logger.error(f"Critical error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Internal server error',
                'error': str(e)
            })
        } 