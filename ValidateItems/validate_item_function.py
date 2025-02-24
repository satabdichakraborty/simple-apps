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
BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"  # Claude 3.5 Sonnet model ID

def setup_aws_clients():
    """Initialize AWS service clients"""
    try:
        dynamodb = boto3.resource('dynamodb')
        bedrock_runtime = boto3.client('bedrock-runtime')
        return dynamodb, bedrock_runtime
    except Exception as e:
        logger.error(f"Failed to initialize AWS clients: {str(e)}")
        raise

def get_claude_response(bedrock_runtime, question: str, options: Dict[str, str]) -> Dict[str, Any]:
    """Get answer from Claude 3.5 Sonnet model"""
    try:
        # Format the prompt
        options_text = "\n".join([f"{key}) {value}" for key, value in options.items()])
        prompt = f"""You are an AWS expert. Please analyze this multiple choice question and provide the correct answer with explanation.

Question: {question}

Options:
{options_text}

Please provide your response in this JSON format:
{{
    "correct_option": "A/B/C/D/E/F",
    "explanation": "Your detailed explanation here"
}}

Be very specific about why the chosen answer is correct and why others are incorrect.
"""

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
                "system": "You are an AWS certification expert. Always respond in valid JSON format."
            })
        )
        
        # Parse response for Claude 3.5
        response_body = json.loads(response['body'].read())
        response_text = response_body.get('content', [{}])[0].get('text', '{}')
        
        # Add error handling for JSON parsing
        try:
            claude_response = json.loads(response_text)
            if not isinstance(claude_response, dict):
                raise ValueError("Response is not a dictionary")
            if 'correct_option' not in claude_response or 'explanation' not in claude_response:
                raise ValueError("Response missing required fields")
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON response: {response_text}")
            return {
                "correct_option": "Error",
                "explanation": "Failed to parse Claude's response as JSON"
            }
        
        return claude_response
        
    except Exception as e:
        logger.error(f"Error getting Claude response: {str(e)}")
        logger.error(f"Full error details: ", exc_info=True)
        return {
            "correct_option": "Error",
            "explanation": f"Failed to get answer: {str(e)}"
        }

def format_question(item: Dict[str, Any], bedrock_runtime) -> Dict[str, Any]:
    """Format a question with its non-empty answers and get Claude's response"""
    try:
        # Get all possible responses and handle 'nan' values
        responses = {
            'A': str(item.get('ResponseA', '')),
            'B': str(item.get('ResponseB', '')),
            'C': str(item.get('ResponseC', '')),
            'D': str(item.get('ResponseD', '')),
            'E': str(item.get('ResponseE', '')),
            'F': str(item.get('ResponseF', ''))
        }
        
        # Filter out empty responses and 'nan'
        non_empty_responses = {
            key: value for key, value in responses.items() 
            if value and value.strip() and value.lower() != 'nan'
        }
        
        # Format the question text with answers
        question_text = item.get('Question', '')
        formatted_text = f"Question: {question_text}\n\n"
        for key, value in non_empty_responses.items():
            formatted_text += f"{key}) {value}\n"
            
        # Get Claude's response
        claude_answer = get_claude_response(bedrock_runtime, question_text, non_empty_responses)
        
        return {
            'QuestionId': str(item.get('QuestionId', '')),
            'FormattedText': formatted_text,
            'Type': str(item.get('Type', '')),
            'Status': str(item.get('Status', '')),
            'Key': str(item.get('Key', '')),
            'Topic': str(item.get('Topic', '')),
            'ResponseCount': len(non_empty_responses),
            'ClaudeResponse': {
                'CorrectOption': claude_answer.get('correct_option', 'Unknown'),
                'Explanation': claude_answer.get('explanation', 'No explanation provided')
            }
        }
    except Exception as e:
        logger.error(f"Error formatting question: {str(e)}")
        logger.error(f"Problematic item: {item}")
        raise

def get_formatted_questions(table, bedrock_runtime) -> List[Dict[str, Any]]:
    """Read and format questions from DynamoDB table"""
    try:
        response = table.scan()
        items = response.get('Items', [])
        
        # Format each question
        formatted_questions = []
        for item in items:
            formatted_question = format_question(item, bedrock_runtime)
            formatted_questions.append(formatted_question)
            
            # Log each formatted question with Claude's response
            logger.info(f"\nQuestion ID: {formatted_question['QuestionId']}")
            logger.info(formatted_question['FormattedText'])
            logger.info(f"Response Count: {formatted_question['ResponseCount']}")
            logger.info(f"Claude's Answer: {formatted_question['ClaudeResponse']['CorrectOption']}")
            logger.info(f"Explanation: {formatted_question['ClaudeResponse']['Explanation']}\n")
            
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
            
        # Initialize AWS clients
        dynamodb, bedrock_runtime = setup_aws_clients()
        table = dynamodb.Table(TABLE_NAME)
        
        # Get and format questions
        formatted_questions = get_formatted_questions(table, bedrock_runtime)
        
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