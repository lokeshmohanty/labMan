"""
Background email queue for Lab Manager application.

This module provides a lightweight background task queue for sending emails
asynchronously to avoid blocking the main application thread.
"""
import queue
import threading
import time
from typing import Callable, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailQueue:
    """
    Singleton background email queue using threading.
    
    Emails are processed in a background thread to avoid blocking
    the main application. The queue persists for the lifetime of
    the application.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Ensure singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the email queue and start worker thread"""
        if self._initialized:
            return
            
        self.queue = queue.Queue()
        self.worker_thread = threading.Thread(
            target=self._worker,
            daemon=True,
            name="EmailQueueWorker"
        )
        self.worker_thread.start()
        self._initialized = True
        logger.info("Email queue initialized")
    
    def enqueue(self, email_func: Callable, **kwargs):
        """
        Add an email task to the queue.
        
        Args:
            email_func: The email function to call
            **kwargs: Arguments to pass to the email function
        """
        self.queue.put((email_func, kwargs))
        logger.debug(f"Enqueued email task: {email_func.__name__}")
    
    def enqueue_batch(self, email_func: Callable, recipients: list, **common_kwargs):
        """
        Enqueue multiple emails with the same function but different recipients.
        
        Args:
            email_func: The email function to call
            recipients: List of recipient dictionaries
            **common_kwargs: Common arguments for all emails
        """
        for recipient in recipients:
            kwargs = {**common_kwargs, 'recipient': recipient}
            self.enqueue(email_func, **kwargs)
        logger.info(f"Enqueued {len(recipients)} batch emails")
    
    def _worker(self):
        """
        Background worker thread that processes the email queue.
        
        Runs continuously, processing emails as they are added to the queue.
        Errors are logged but don't stop the worker.
        """
        logger.info("Email queue worker started")
        
        while True:
            try:
                email_func, kwargs = self.queue.get(timeout=1)
                
                try:
                    logger.debug(f"Processing email: {email_func.__name__}")
                    result = email_func(**kwargs)
                    
                    if result:
                        logger.debug(f"Email sent successfully: {email_func.__name__}")
                    else:
                        logger.warning(f"Email failed: {email_func.__name__}")
                        
                except Exception as e:
                    logger.error(f"Error processing email {email_func.__name__}: {e}")
                    
                finally:
                    self.queue.task_done()
                    
            except queue.Empty:
                # No items in queue, continue waiting
                continue
            except Exception as e:
                logger.error(f"Email queue worker error: {e}")
                time.sleep(1)  # Brief pause before continuing
    
    def wait_for_completion(self, timeout: int = 30):
        """
        Wait for all queued emails to be processed.
        
        Useful for testing or graceful shutdown.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if all emails processed, False if timeout
        """
        try:
            self.queue.join()
            return True
        except Exception as e:
            logger.error(f"Error waiting for queue completion: {e}")
            return False
    
    def get_queue_size(self) -> int:
        """
        Get the current number of emails in the queue.
        
        Returns:
            int: Number of pending emails
        """
        return self.queue.qsize()


# Global email queue instance
email_queue = EmailQueue()
