#!/usr/bin/env python3
"""
Scheduled operations for Agent Angus with CrewAI.

This script provides a daemon mode for running scheduled tasks with Agent Angus using CrewAI.
"""
import schedule
import time
import logging
import argparse
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

# Global variable for simple tools flag
use_simple_tools = False

def run_daily_uploads():
    """
    Run the upload task daily.
    """
    logger.info("Running daily uploads")
    try:
        crew = AngusCrew(use_simple_tools=use_simple_tools)
        result = crew.run_upload_only()
        logger.info(f"Upload result: {result}")
    except Exception as e:
        logger.error(f"Error running daily uploads: {str(e)}", exc_info=True)

def run_hourly_engagement():
    """
    Run the engagement task hourly.
    """
    logger.info("Running hourly engagement")
    try:
        crew = AngusCrew(use_simple_tools=use_simple_tools)
        result = crew.run_engagement_only()
        logger.info(f"Engagement result: {result}")
    except Exception as e:
        logger.error(f"Error running hourly engagement: {str(e)}", exc_info=True)

def run_weekly_full_workflow():
    """
    Run the full workflow weekly.
    """
    logger.info("Running weekly full workflow")
    try:
        crew = AngusCrew(use_simple_tools=use_simple_tools)
        result = crew.run_full_workflow()
        logger.info(f"Full workflow result: {result}")
    except Exception as e:
        logger.error(f"Error running weekly full workflow: {str(e)}", exc_info=True)

def main():
    """
    Main entry point for scheduled operations.
    """
    global use_simple_tools
    
    parser = argparse.ArgumentParser(description='Run scheduled tasks for Agent Angus with CrewAI')
    parser.add_argument('--daily-time', type=str, default='10:00',
                        help='Time to run daily uploads (HH:MM format)')
    parser.add_argument('--weekly-day', type=str, default='monday',
                        choices=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'],
                        help='Day to run weekly full workflow')
    parser.add_argument('--weekly-time', type=str, default='08:00',
                        help='Time to run weekly full workflow (HH:MM format)')
    parser.add_argument('--disable-hourly', action='store_true',
                        help='Disable hourly engagement tasks')
    parser.add_argument('--disable-daily', action='store_true',
                        help='Disable daily upload tasks')
    parser.add_argument('--disable-weekly', action='store_true',
                        help='Disable weekly full workflow tasks')
    parser.add_argument('--simple-tools', action='store_true',
                        help='Use simple tools created with the @tool decorator')
    
    args = parser.parse_args()
    use_simple_tools = args.simple_tools
    
    logger.info("Starting scheduled operations")
    if use_simple_tools:
        logger.info("Using simple tools created with the @tool decorator")
    
    # Schedule tasks
    if not args.disable_daily:
        logger.info(f"Scheduling daily uploads at {args.daily_time}")
        schedule.every().day.at(args.daily_time).do(run_daily_uploads)
    
    if not args.disable_hourly:
        logger.info("Scheduling hourly engagement")
        schedule.every().hour.do(run_hourly_engagement)
    
    if not args.disable_weekly:
        logger.info(f"Scheduling weekly full workflow on {args.weekly_day} at {args.weekly_time}")
        if args.weekly_day == 'monday':
            schedule.every().monday.at(args.weekly_time).do(run_weekly_full_workflow)
        elif args.weekly_day == 'tuesday':
            schedule.every().tuesday.at(args.weekly_time).do(run_weekly_full_workflow)
        elif args.weekly_day == 'wednesday':
            schedule.every().wednesday.at(args.weekly_time).do(run_weekly_full_workflow)
        elif args.weekly_day == 'thursday':
            schedule.every().thursday.at(args.weekly_time).do(run_weekly_full_workflow)
        elif args.weekly_day == 'friday':
            schedule.every().friday.at(args.weekly_time).do(run_weekly_full_workflow)
        elif args.weekly_day == 'saturday':
            schedule.every().saturday.at(args.weekly_time).do(run_weekly_full_workflow)
        elif args.weekly_day == 'sunday':
            schedule.every().sunday.at(args.weekly_time).do(run_weekly_full_workflow)
    
    # Run continuously
    try:
        logger.info("Starting scheduler loop")
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Scheduled operations interrupted by user")
    except Exception as e:
        logger.error(f"Error in scheduler loop: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
