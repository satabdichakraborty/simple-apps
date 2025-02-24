import boto3
import json
import logging
from botocore.exceptions import ClientError
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
REGION = "us-east-1"

def setup_bedrock_client():
    """Initialize Bedrock client"""
    try:
        return boto3.client("bedrock-runtime", region_name=REGION)
    except Exception as e:
        logger.error(f"Failed to initialize Bedrock client: {str(e)}")
        raise

def ask_claude() -> Dict[str, Any]:
    """Ask Claude a simple question"""
    try:
        # Initialize Bedrock client
        client = setup_bedrock_client()
        
        # Define the prompt
        prompt = "How are you?"
        
        # Format the request payload
        native_request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 512,
            "temperature": 0.5,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ],
        }
        
        # Convert request to JSON
        request = json.dumps(native_request)
        
        # Invoke the model
        response = client.invoke_model(modelId=MODEL_ID, body=request)
        
        # Decode the response
        model_response = json.loads(response["body"].read())
        response_text = model_response["content"][0]["text"]
        
        logger.info(f"Raw response: {model_response}")
        
        return {
            "statusCode": 200,
            "response": response_text
        }
        
    except ClientError as e:
        logger.error(f"ClientError in Claude response: {str(e)}")
        return {
            "statusCode": 500,
            "error": f"Bedrock ClientError: {str(e)}"
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