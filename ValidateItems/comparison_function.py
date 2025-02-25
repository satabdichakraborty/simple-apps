import boto3
import json
import logging
from typing import Dict, List, Any
import os
from botocore.exceptions import ClientError
import csv
from io import StringIO
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get environment variables
SOURCE_TABLE = os.environ.get('SOURCE_TABLE')  # Table with 'key' field
RESULTS_TABLE = os.environ.get('RESULTS_TABLE')  # Table with 'correctoption' field
OUTPUT_BUCKET = os.environ.get('OUTPUT_BUCKET')

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
        # Handle reserved word 'Key' with expression attributes
        expression_names = {}
        projection = []
        
        for attr in attributes:
            if attr == 'Key':  # Match exact capitalization
                expression_names['#k'] = 'Key'
                projection.append('#k')
            else:
                projection.append(attr)
        
        # Build the projection expression
        projection_expression = ', '.join(projection)
        
        # Scan with expression attribute names if needed
        if expression_names:
            response = table.scan(
                ProjectionExpression=projection_expression,
                ExpressionAttributeNames=expression_names
            )
        else:
            response = table.scan(
                ProjectionExpression=projection_expression
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
        source_items = get_table_items(source_table, ['QuestionId', 'Key'])
        results_items = get_table_items(results_table, ['QuestionId', 'CorrectOption'])
        
        # Create dictionaries for easier lookup
        source_dict = {item['QuestionId']: item.get('Key', '').strip() for item in source_items}
        
        # Handle comma-separated values in results table and store all options
        results_dict = {}
        all_options_dict = {}  # Store complete CorrectOption string
        for item in results_items:
            qid = item['QuestionId']
            correct_options = item.get('CorrectOption', '').split(',')
            results_dict[qid] = correct_options[0].strip() if correct_options else ''
            all_options_dict[qid] = item.get('CorrectOption', '')  # Store complete string
        
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
                # Clean and compare values
                source_key = source_key.strip().upper()
                result_key = result_key.strip().upper()
                
                matches_flag = source_key == result_key
                if matches_flag:
                    matches += 1
                else:
                    mismatches.append(question_id)
                
                comparison_details.append({
                    "questionid": question_id,
                    "matches": matches_flag,
                    "table1_key": source_key,
                    "table2_correctoption": result_key,
                    "table2_all_options": all_options_dict.get(question_id, '') if not matches_flag else ''  # Use stored options
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

def save_to_s3(comparison_results: Dict[str, Any]) -> str:
    """Save comparison results to CSV in S3"""
    try:
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow([
            'QuestionId',
            'Matches',
            'Table1_Key',
            'Table2_CorrectOption',
            'Table2_All_Options',
            'Status'
        ])
        
        # Write comparison details
        for detail in comparison_results['comparison_details']:
            writer.writerow([
                detail['questionid'],
                detail['matches'],
                detail['table1_key'],
                detail['table2_correctoption'],
                detail.get('table2_all_options', ''),
                'Match' if detail['matches'] else 'Mismatch'
            ])
        
        # Write missing items
        for question_id in comparison_results['missing_from_table1']:
            writer.writerow([
                question_id,
                'N/A',
                'MISSING',
                'EXISTS',
                'Missing from Table 1'
            ])
            
        for question_id in comparison_results['missing_from_table2']:
            writer.writerow([
                question_id,
                'N/A',
                'EXISTS',
                'MISSING',
                'Missing from Table 2'
            ])
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'comparison_results_{timestamp}.csv'
        
        # Upload to S3
        s3_client = boto3.client('s3')
        s3_client.put_object(
            Bucket=OUTPUT_BUCKET,
            Key=filename,
            Body=output.getvalue(),
            ContentType='text/csv'
        )
        
        logger.info(f"Saved comparison results to s3://{OUTPUT_BUCKET}/{filename}")
        return filename
        
    except Exception as e:
        logger.error(f"Error saving to S3: {str(e)}")
        raise

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Main Lambda handler"""
    logger.info("Starting DynamoDB Table Comparison")
    
    try:
        # Validate environment variables
        if not all([SOURCE_TABLE, RESULTS_TABLE, OUTPUT_BUCKET]):
            raise ValueError("Required environment variables are not set")
        
        # Perform comparison
        comparison_results = compare_tables()
        
        # Save results to S3
        output_file = save_to_s3(comparison_results)
        
        # Prepare response
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Comparison completed successfully',
                'results': comparison_results,
                'output_file': f"s3://{OUTPUT_BUCKET}/{output_file}"
            }, indent=2)
        }
        
        # Log summary
        logger.info(f"Comparison Summary:")
        logger.info(f"Matches: {comparison_results['matches']}")
        logger.info(f"Mismatches: {comparison_results['mismatches']}")
        logger.info(f"Missing from Table 1: {len(comparison_results['missing_from_table1'])}")
        logger.info(f"Missing from Table 2: {len(comparison_results['missing_from_table2'])}")
        logger.info(f"Results saved to: {output_file}")
        
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
