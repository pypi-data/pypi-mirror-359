# This is a concrete implementation of the ChatbotClient. It's designed to communicate with any chatbot that exposes an HTTP API endpoint. Its behavior is controlled entirely by the config.yaml file.

import logging
import requests
import json
from typing import Dict, Any

from .base import ChatbotClient

logger = logging.getLogger(__name__)

class ApiClient(ChatbotClient):
    """
    A concrete client for sending questions to a chatbot via an HTTP API.
    
    This client is highly configurable and supports various HTTP methods,
    headers, and dynamic request bodies.
    """
    def __init__(self, settings: Dict[str, Any]):
        super().__init__(settings)
        # Validate required settings
        if 'url' not in self.settings or 'body_template' not in self.settings:
            raise ValueError("ApiClient settings must include 'url' and 'body_template'.")
        
        self.url = self.settings['url']
        self.method = self.settings.get('method', 'POST').upper()
        self.headers = self.settings.get('headers', {})
        self.body_template = self.settings['body_template']

    def send(self, question: str, session_id: str):
        """
        Formats and sends an HTTP request to the configured chatbot API endpoint.

        Args:
            question: The text of the question.
            session_id: The unique session ID for this interaction.

        Raises:
            requests.exceptions.RequestException: For issues like connection
                                                  errors, timeouts, or bad responses.
        """
        # The body can be constructed as a dictionary or a string. If the template starts with '{' we assume it's a JSON string.
        # This implementation uses str.replace for simplicity. A more robust solution might use f-strings or templating engines.
        if isinstance(self.body_template, str) and self.body_template.strip().startswith('{'):
            # It's a JSON string template
            body_str = self.body_template.replace("{question}", json.dumps(question)[1:-1]).replace("{session_id}", session_id)
            try:
                payload = json.loads(body_str)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse body_template as JSON for session {session_id}. Check your config.")
                raise ValueError("Invalid JSON in 'body_template' configuration.")
        else:
            # For simpler cases or non-JSON bodies.
            # This is less likely for APIs but provides flexibility.
            payload = self.body_template.format(question=question, session_id=session_id)

        try:
            response = requests.request(
                method=self.method,
                url=self.url,
                headers=self.headers,
                json=payload if isinstance(payload, dict) else None,
                data=payload if isinstance(payload, str) else None,
                timeout=30 # A reasonable default timeout
            )
            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()
            logger.debug(f"API request to {self.url} for session {session_id} successful.")

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for session {session_id}: {e}")
            raise # Re-raise the exception to be handled by the TestRunner