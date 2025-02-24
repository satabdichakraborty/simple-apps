import boto3
import json
import os
import logging
from typing import Dict, Any
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

def setup_bedrock_client():
    """Initialize Bedrock client"""
    try:
        return boto3.client('bedrock-runtime')
    except Exception as e:
        logger.error(f"Failed to initialize Bedrock client: {str(e)}")
        raise

def get_claude_response(bedrock_runtime, prompt: str) -> Dict[str, Any]:
    """Get response from Claude 3.5 Sonnet model"""
    try:
        # Call Bedrock with Claude 3.5 Sonnet
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps({
                "anthropic_version": "bedrock-2024-02-29",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2048,
                "temperature": 0.0,
                "system": "You are an AWS certification expert."
            })
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        response_text = response_body.get('content', [{}])[0].get('text', '')
        
        return {
            "statusCode": 200,
            "response": response_text
        }
        
    except Exception as e:
        logger.error(f"Error getting Claude response: {str(e)}")
        logger.error("Full error details: ", exc_info=True)
        return {
            "statusCode": 500,
            "error": str(e)
        }

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler"""
    logger.info("Starting Bedrock Call Lambda function")
    logger.info(f"Received event: {event}")
    
    try:
        # Validate input
        if 'prompt' not in event:
            raise ValueError("No prompt provided in event")
            
        prompt = event['prompt']
        
        # Initialize Bedrock client
        bedrock_runtime = setup_bedrock_client()
        
        # Get Claude's response
        result = get_claude_response(bedrock_runtime, prompt)
        
        # Prepare response
        response = {
            'statusCode': result.get('statusCode', 500),
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Successfully processed prompt',
                'response': result.get('response', ''),
                'error': result.get('error', None)
            }, indent=2)
        }
        
        return response
        
    except ValueError as ve:
        logger.error(f"Validation error: {str(ve)}")
        return {
            'statusCode': 400,
            'body': json.dumps({
                'message': 'Invalid input',
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