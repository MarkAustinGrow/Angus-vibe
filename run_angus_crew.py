#!/usr/bin/env python3
"""
Command-line interface for running Agent Angus with CrewAI.

This script provides a command-line interface for running different workflows
with Agent Angus using CrewAI.
"""
import argparse
import logging
from angus_crew import AngusCrew

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('angus_crew.log')
    ]
)
logger = logging.getLogger(__name__)

def main():
    """
    Main entry point for the command-line interface.
    """
    parser = argparse.ArgumentParser(description='Run Agent Angus with CrewAI')
    parser.add_argument('--task', type=str, 
                        choices=['analysis', 'upload', 'engagement', 'full'],
                        required=True, help='Task to perform')
    parser.add_argument('--limit', type=int, default=5,
                        help='Limit for number of items to process')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose output enabled")
    
    logger.info(f"Running task: {args.task} with limit: {args.limit}")
    
    try:
        crew = AngusCrew()
        
        if args.task == 'analysis':
            logger.info("Running analysis task")
            result = crew.run_analysis_only()
        elif args.task == 'upload':
            logger.info("Running upload task")
            result = crew.run_upload_only()
        elif args.task == 'engagement':
            logger.info("Running engagement task")
            result = crew.run_engagement_only()
        elif args.task == 'full':
            logger.info("Running full workflow")
            result = crew.run_full_workflow()
        
        logger.info("Task completed successfully")
        print("\nResult:")
        print(result)
        
    except Exception as e:
        logger.error(f"Error running task: {str(e)}", exc_info=True)
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
