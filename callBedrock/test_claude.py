import boto3
import json
import logging
from botocore.exceptions import ClientError
from typing import Dict, List, Any
import os

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
MODEL_ID = "anthropic.claude-3-haiku-20240307-v1:0"
REGION = "us-east-1"
TABLE_NAME = os.environ.get('TABLE_NAME')

def setup_aws_clients():
    """Initialize AWS clients"""
    try:
        dynamodb = boto3.resource('dynamodb')
        bedrock = boto3.client("bedrock-runtime", region_name=REGION)
        return dynamodb, bedrock
    except Exception as e:
        logger.error(f"Failed to initialize AWS clients: {str(e)}")
        raise

def get_questions_from_dynamodb(table) -> List[Dict[str, Any]]:
    """Read questions from DynamoDB"""
    try:
        response = table.scan()
        return response.get('Items', [])
    except Exception as e:
        logger.error(f"Error reading from DynamoDB: {str(e)}")
        raise

def validate_question(client, question: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a single question using Claude"""
    try:
        # Format the question and answers
        question_text = question.get('Question', '')
        answers = {
            'A': question.get('ResponseA', ''),
            'B': question.get('ResponseB', ''),
            'C': question.get('ResponseC', ''),
            'D': question.get('ResponseD', ''),
            'E': question.get('ResponseE', ''),
            'F': question.get('ResponseF', '')
        }
        
        # Filter out empty answers
        valid_answers = {k: v for k, v in answers.items() if v and v.strip() and v.lower() != 'nan'}
        
        # Create the prompt with stronger JSON formatting instruction
        answers_text = "\n".join([f"{k}) {v}" for k, v in valid_answers.items()])
        prompt = f"""As an AWS certification expert, analyze this question and provide the correct answer with explanation.

Question: {question_text}

Options:
{answers_text}

Respond ONLY with a JSON object in this exact format, no other text:
{{
    "correct_option": "<single letter A/B/C/D/E/F>",
    "explanation": "<your detailed explanation>",
    "confidence": "<HIGH/MEDIUM/LOW>"
}}

The response must be valid JSON. Do not include any text outside the JSON object."""

        # Format the request payload
        native_request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2048,
            "temperature": 0.0,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}],
                }
            ],
            "system": "You are an AWS certification expert. Always respond with valid JSON only."
        }
        
        # Invoke Claude
        response = client.invoke_model(
            modelId=MODEL_ID,
            body=json.dumps(native_request)
        )
        
        # Parse response
        model_response = json.loads(response["body"].read())
        response_text = model_response["content"][0]["text"]
        
        # Log the raw response for debugging
        logger.info(f"Raw Claude response: {response_text}")
        
        # Clean the response text - remove any non-JSON content
        response_text = response_text.strip()
        if response_text.startswith('```json'):
            response_text = response_text.split('```json')[1]
        if response_text.endswith('```'):
            response_text = response_text.split('```')[0]
        response_text = response_text.strip()
        
        try:
            # Parse the JSON response
            claude_answer = json.loads(response_text)
            
            # Validate JSON structure
            required_fields = ['correct_option', 'explanation', 'confidence']
            if not all(field in claude_answer for field in required_fields):
                raise ValueError("Missing required fields in response")
                
            return {
                "questionId": question.get('QuestionId', ''),
                "question": question_text,
                "validation": claude_answer,
                "status": "success"
            }
        except json.JSONDecodeError as je:
            logger.error(f"Failed to parse Claude's response as JSON: {response_text}")
            logger.error(f"JSON error: {str(je)}")
            return {
                "questionId": question.get('QuestionId', ''),
                "question": question_text,
                "validation": {
                    "correct_option": "ERROR",
                    "explanation": f"Failed to parse response: {str(je)}",
                    "confidence": "LOW"
                },
                "status": "error"
            }
            
    except Exception as e:
        logger.error(f"Error validating question: {str(e)}")
        return {
            "questionId": question.get('QuestionId', ''),
            "status": "error",
            "error": str(e)
        }

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler"""
    logger.info("Starting AWS Question Validator")
    
    try:
        # Validate environment variables
        if not TABLE_NAME:
            raise ValueError("TABLE_NAME environment variable is not set")
            
        # Initialize AWS clients
        dynamodb, bedrock = setup_aws_clients()
        table = dynamodb.Table(TABLE_NAME)
        
        # Get questions from DynamoDB
        questions = get_questions_from_dynamodb(table)
        logger.info(f"Found {len(questions)} questions to validate")
        
        # Validate each question
        validation_results = []
        for question in questions:
            result = validate_question(bedrock, question)
            validation_results.append(result)
            logger.info(f"Validated question {result['questionId']}: {result['status']}")
        
        # Prepare response
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Questions validated',
                'total_questions': len(questions),
                'results': validation_results
            }, indent=2)
        }
        
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