import boto3
import json
import logging
from typing import Dict, List, Any
import os
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get environment variables
SOURCE_TABLE = os.environ.get('SOURCE_TABLE')  # Table with 'key' field
RESULTS_TABLE = os.environ.get('RESULTS_TABLE')  # Table with 'correctoption' field

def setup_dynamodb():
    """Initialize DynamoDB resource"""
    try:
        return boto3.resource('dynamodb')
    except Exception as e:
        logger.error(f"Failed to initialize DynamoDB: {str(e)}")
        raise

def get_table_items(table, attributes: List[str]) -> List[Dict[str, Any]]:
    """Get items from DynamoDB table with specified attributes"""
    try:
        projection = ', '.join(attributes)
        response = table.scan(
            ProjectionExpression=projection
        )
        return response.get('Items', [])
    except ClientError as e:
        logger.error(f"DynamoDB operation failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error reading from table: {str(e)}")
        raise

def compare_tables() -> Dict[str, Any]:
    """Compare records between two DynamoDB tables"""
    try:
        dynamodb = setup_dynamodb()
        source_table = dynamodb.Table(SOURCE_TABLE)
        results_table = dynamodb.Table(RESULTS_TABLE)
        
        # Get items from both tables
        source_items = get_table_items(source_table, ['QuestionId', '#key'])
        results_items = get_table_items(results_table, ['QuestionId', 'CorrectOption'])
        
        # Create dictionaries for easier lookup
        source_dict = {item['QuestionId']: item.get('#key', '') for item in source_items}
        results_dict = {item['QuestionId']: item.get('CorrectOption', '') for item in results_items}
        
        # Initialize comparison results
        matches = 0
        mismatches = []
        missing_from_source = []
        missing_from_results = []
        comparison_details = []
        
        # Compare all QuestionIds from both tables
        all_question_ids = set(list(source_dict.keys()) + list(results_dict.keys()))
        
        for question_id in all_question_ids:
            source_key = source_dict.get(question_id)
            result_key = results_dict.get(question_id)
            
            # Case 1: Question exists in both tables
            if source_key is not None and result_key is not None:
                matches_flag = source_key.upper() == result_key.upper()
                if matches_flag:
                    matches += 1
                else:
                    mismatches.append(question_id)
                
                comparison_details.append({
                    "questionid": question_id,
                    "matches": matches_flag,
                    "table1_key": source_key,
                    "table2_correctoption": result_key
                })
            
            # Case 2: Question missing from source table
            elif source_key is None:
                missing_from_source.append(question_id)
            
            # Case 3: Question missing from results table
            else:
                missing_from_results.append(question_id)
        
        return {
            "matches": matches,
            "mismatches": len(mismatches),
            "mismatched_ids": mismatches,
            "missing_from_table1": missing_from_source,
            "missing_from_table2": missing_from_results,
            "comparison_details": comparison_details
        }
        
    except Exception as e:
        logger.error(f"Error during comparison: {str(e)}")
        raise

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler"""
    logger.info("Starting DynamoDB Table Comparison")
    
    try:
        # Validate environment variables
        if not SOURCE_TABLE or not RESULTS_TABLE:
            raise ValueError("Required environment variables are not set")
        
        # Perform comparison
        comparison_results = compare_tables()
        
        # Prepare response
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Comparison completed successfully',
                'results': comparison_results
            }, indent=2)
        }
        
        # Log summary
        logger.info(f"Comparison Summary:")
        logger.info(f"Matches: {comparison_results['matches']}")
        logger.info(f"Mismatches: {comparison_results['mismatches']}")
        logger.info(f"Missing from Table 1: {len(comparison_results['missing_from_table1'])}")
        logger.info(f"Missing from Table 2: {len(comparison_results['missing_from_table2'])}")
        
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
