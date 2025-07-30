#!/usr/bin/env python3
"""
CLI entry point for Reddit DM automation using Popsy API
"""

import argparse
import json
import logging
import os

from popsy_cli.api import (
    PopsyAPIClient,
    parse_threads_response,
    process_threads_for_dm,
    process_threads_for_comment,
    setup_logging,
    show_configuration
)

# Import browser automation functionality
try:
    from popsy_cli.dm_automation import BrowserDMSender, create_browser_dm_callback
    BROWSER_AVAILABLE = True
except ImportError as e:
    BROWSER_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"Browser automation not available: {e}")

logger = logging.getLogger(__name__)


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description='Reddit DM Automation CLI using Popsy API')

    parser.add_argument('--token', type=str, help='API authentication token')
    parser.add_argument('--base-url', type=str, default='https://app.popsy.ai',
                       help='Base URL of the API (default: https://app.popsy.ai)')
    parser.add_argument('--min-relevancy', type=int, default=90,
                       help='Minimum relevancy score (0-100, default: 90)')
    parser.add_argument('--subreddit-id', type=int,
                       help='Filter by specific subreddit ID')
    parser.add_argument('--page-size', type=int, default=50,
                       help='Number of threads to fetch per page (default: 50)')
    parser.add_argument('--max-threads', type=int, default=100,
                       help='Maximum number of threads to process (default: 100)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Run without actually sending DMs or marking threads')
    parser.add_argument('--show-closed', action='store_true',
                       help='Include closed threads')
    parser.add_argument('--show-deleted', action='store_true',
                       help='Include deleted threads')
    parser.add_argument('--show-new', action='store_true',
                       help='Include new threads (default: False)')
    parser.add_argument('--hide-already-dmed', action='store_true', default=True,
                       help='Hide threads from authors already DMed (default: True)')
    parser.add_argument('--show-already-dmed', action='store_true',
                       help='Show threads from authors already DMed (overrides --hide-already-dmed)')
    parser.add_argument('--config', type=str, default='config.json',
                       help='Configuration file path (default: config.json)')
    parser.add_argument('--mode', type=str, choices=['dm', 'comment'], default='dm',
                       help='Processing mode: dm or comment (default: dm)')
    parser.add_argument('--sort-by', type=str, choices=['most_relevant', 'most_recent'], default='most_recent',
                       help='Sort threads by relevance or recency (default: most_recent)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging and show detailed configuration')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging (shows API requests/responses)')
    parser.add_argument('--browser', '--live', action='store_true', default=True,
                       help='Use live browser automation for sending DMs (requires camoufox)')
    parser.add_argument('--headless', action='store_true',
                       help='Run browser in headless mode (only with --browser)')
    parser.add_argument('--browser-delay', type=float, default=None,
                       help='Override delay between browser actions (seconds)')

    parsed_args = parser.parse_args()

    # Setup logging based on verbosity
    setup_logging(verbose=parsed_args.verbose, debug=parsed_args.debug)

    # Load configuration from file if it exists
    config = {}
    if os.path.exists(parsed_args.config):
        try:
            with open(parsed_args.config, 'r') as f:
                config = json.load(f)
                logger.info(f"Loaded configuration from {parsed_args.config}")
        except Exception as e:
            logger.warning(f"Failed to load config file: {e}")

    # Override config with command line arguments (only if explicitly provided)
    token = parsed_args.token or config.get('token') or os.getenv('POPSY_API_TOKEN')
    base_url = parsed_args.base_url or config.get('base_url', 'https://app.popsy.ai')

    # Handle other config values with proper precedence: CLI args -> config file -> defaults
    # Get default values from parser to avoid hardcoding
    parser_defaults = {
        'min_relevancy': 90,
        'max_threads': 100,
        'page_size': 50,
        'sort_by': 'most_recent',
        'mode': 'dm',
        'show_new': False,
        'hide_already_dmed': True,
        'browser': True,
        'headless': False
    }

    def get_effective_value(arg_name, arg_value, config_key=None):
        """Get effective value: CLI arg (if not default) -> config -> default"""
        config_key = config_key or arg_name
        default_value = parser_defaults.get(arg_name)

        # If CLI arg is different from default, use it
        if arg_value != default_value:
            return arg_value
        # Otherwise use config value or default
        return config.get(config_key, default_value)

    min_relevancy = get_effective_value('min_relevancy', parsed_args.min_relevancy)
    max_threads = get_effective_value('max_threads', parsed_args.max_threads)
    page_size = get_effective_value('page_size', parsed_args.page_size)
    sort_by = get_effective_value('sort_by', parsed_args.sort_by)
    mode = get_effective_value('mode', parsed_args.mode)
    show_new = get_effective_value('show_new', parsed_args.show_new)
    use_browser = get_effective_value('browser', parsed_args.browser)
    headless = get_effective_value('headless', parsed_args.headless)

    # Handle hide_already_dmed with override logic
    hide_already_dmed = get_effective_value('hide_already_dmed', parsed_args.hide_already_dmed)
    if parsed_args.show_already_dmed:
        hide_already_dmed = False

    # Validate browser automation requirements
    if use_browser and not BROWSER_AVAILABLE:
        logger.error("Browser automation requested but dependencies not available. Install camoufox and browserforge.")
        return

    # Browser mode only works with DM mode
    if use_browser and mode != 'dm':
        logger.error("Browser automation is only available for DM mode (--mode dm)")
        return

    # Show configuration if verbose mode is enabled
    if parsed_args.verbose or parsed_args.debug:
        effective_values = {
            'token': '[REDACTED]' if token else 'Not set',
            'base_url': base_url,
            'min_relevancy': min_relevancy,
            'max_threads': max_threads,
            'page_size': page_size,
            'sort_by': sort_by,
            'mode': mode,
            'show_new': show_new,
            'hide_already_dmed': hide_already_dmed,
            'use_browser': use_browser,
            'headless': headless,
        }
        show_configuration(config, vars(parsed_args), effective_values)

    if not token:
        logger.error("No API token provided. Use --token, config file, or POPSY_API_TOKEN env var")
        return

    automation_type = "BROWSER AUTOMATION" if use_browser else "API SIMULATION"
    logger.info("=" * 80)
    logger.info(f"REDDIT {mode.upper()} AUTOMATION - {automation_type}")
    logger.info("=" * 80)
    logger.info(f"Base URL: {base_url}")
    logger.info(f"Min Relevancy: {min_relevancy}")
    logger.info(f"Max Threads: {max_threads}")
    logger.info(f"Mode: {mode}")
    logger.info(f"Hide Already DMed: {hide_already_dmed}")
    logger.info(f"Use Browser: {use_browser}")
    if use_browser:
        logger.info(f"Headless Mode: {headless}")
    logger.info(f"Dry Run: {parsed_args.dry_run}")
    logger.info("=" * 80)
    # Setup browser automation if requested
    browser_sender = None
    dm_callback = None

    with PopsyAPIClient(base_url=base_url, token=token) as api_client:
        try:
            threads_data = api_client.fetch_threads(
                subreddit_id=parsed_args.subreddit_id,
                show_closed=parsed_args.show_closed,
                show_deleted=parsed_args.show_deleted,
                show_new=show_new,
                min_relevancy=min_relevancy,
                page_size=page_size,
                sort_by=sort_by,
                hide_already_dmed=hide_already_dmed
            )

            if not threads_data:
                logger.warning("No threads data received")
                return

            threads = parse_threads_response(threads_data)

            if not threads:
                logger.info("No threads found matching criteria")
                return

            # Limit to max_threads
            threads = threads[:max_threads]

            logger.info(f"Found {len(threads)} threads to process")

            if mode == 'dm':
                if use_browser and not parsed_args.dry_run:
                    logger.info("Setting up browser for DM automation...")
                    browser_sender = BrowserDMSender(headless=headless)
                    browser_sender.setup_browser()
                    dm_callback = create_browser_dm_callback(browser_sender)
                    logger.info("Browser automation ready!")

                processed_count, failed_count = process_threads_for_dm(
                    api_client,
                    threads,
                    dm_sender_callback=dm_callback,
                    dry_run=parsed_args.dry_run
                )
            else:  # comment mode
                if use_browser:
                    logger.warning("Browser automation not supported for comment mode, falling back to simulation")

                processed_count, failed_count = process_threads_for_comment(
                    api_client,
                    threads,
                    dry_run=parsed_args.dry_run
                )

            logger.info("=" * 80)
            logger.info(f"COMPLETED: Processed {processed_count} threads, {failed_count} failed")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"Error in main execution: {e}")
        finally:
            # Clean up browser if it was used
            if browser_sender:
                logger.info("Closing browser...")
                browser_sender.close()


if __name__ == "__main__":
    main()
