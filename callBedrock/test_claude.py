import boto3
import json
import logging
from typing import Dict, Any

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

def ask_claude() -> Dict[str, Any]:
    """Ask Claude a simple question"""
    try:
        # Initialize Bedrock client
        bedrock_runtime = setup_bedrock_client()
        
        # Call Bedrock with Claude 3.5 Sonnet
        response = bedrock_runtime.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps({
                "anthropic_version": "bedrock-2024-02-29",
                "messages": [
                    {
                        "role": "user",
                        "content": "How are you?"
                    }
                ],
                "max_tokens": 2048,
                "temperature": 0.0
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
    logger.info("Starting Simple Claude Test")
    
    try:
        # Get Claude's response
        result = ask_claude()
        
        # Prepare response
        response = {
            'statusCode': result.get('statusCode', 500),
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Claude response received',
                'response': result.get('response', ''),
                'error': result.get('error', None)
            }, indent=2)
        }
        
        logger.info(f"Claude's response: {result.get('response', '')}")
        return response
        
    except Exception as e:
        logger.error(f"Critical error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Internal server error',
                'error': str(e)
            })
        } 