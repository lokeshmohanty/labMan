"""
Helper utilities for Lab Manager application.

This module provides common helper functions used throughout the application
to reduce code duplication and improve maintainability.
"""
import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()


def get_lab_name() -> str:
    """
    Get the configured lab name from environment variables.
    
    Returns:
        str: The lab name, defaults to 'Lab Manager' if not configured
    """
    return os.getenv('LAB_NAME', 'Lab Manager')


def get_lab_group() -> Optional[Dict[str, Any]]:
    """
    Get the default lab group from the database.
    
    Returns:
        Optional[Dict[str, Any]]: The lab group record, or None if not found
    """
    from labman.lib.data import query_db
    lab_name = get_lab_name()
    group = query_db('SELECT id FROM research_groups WHERE name = ?', [lab_name], one=True)
    return dict(group) if group else None


def get_lab_members() -> List[Dict[str, Any]]:
    """
    Get all members of the default lab group.
    
    Returns:
        List[Dict[str, Any]]: List of user records who are members of the lab group
    """
    from labman.lib.groups import get_group_members
    lab_group = get_lab_group()
    if not lab_group:
        return []
    return get_group_members(lab_group['id'])


def get_smtp_config() -> Dict[str, str]:
    """
    Get SMTP configuration from environment variables.
    
    Returns:
        Dict[str, str]: Dictionary containing SMTP configuration
    """
    return {
        'server': os.getenv('SMTP_SERVER', ''),
        'port': int(os.getenv('SMTP_PORT', '587')),
        'username': os.getenv('SMTP_USERNAME', ''),
        'password': os.getenv('SMTP_PASSWORD', ''),
        'sender_email': os.getenv('SENDER_EMAIL', os.getenv('SMTP_USERNAME', ''))
    }


def get_server_url() -> str:
    """
    Get the server URL for generating links.
    
    Returns:
        str: The server URL (e.g., 'http://localhost:9000')
    """
    host = os.getenv('HOST_IP', 'localhost')
    port = os.getenv('SERVER_PORT', '9000')
    return f"http://{host}:{port}"


def format_user_name(user: Dict[str, Any]) -> str:
    """
    Format user name for display.
    
    Args:
        user: User dictionary
        
    Returns:
        str: Formatted user name
    """
    return user.get('name', 'Unknown User')


def is_email_configured() -> bool:
    """
    Check if email is properly configured.
    
    Returns:
        bool: True if SMTP settings are configured
    """
    config = get_smtp_config()
    return bool(config['server'] and config['username'])
