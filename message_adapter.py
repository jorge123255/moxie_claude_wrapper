from typing import List, Optional, Dict, Any
from models import Message
import re


class MessageAdapter:
    """Converts between OpenAI message format and Claude Code prompts."""
    
    @staticmethod
    def messages_to_prompt(messages: List[Message]) -> tuple[str, Optional[str]]:
        """
        Convert OpenAI messages to Claude Code prompt format.
        Returns (prompt, system_prompt)
        """
        system_prompt = None
        conversation_parts = []
        
        for message in messages:
            if message.role == "system":
                # Use the last system message as the system prompt
                system_prompt = message.content
            elif message.role == "user":
                conversation_parts.append(f"Human: {message.content}")
            elif message.role == "assistant":
                conversation_parts.append(f"Assistant: {message.content}")
        
        # Join conversation parts
        prompt = "\n\n".join(conversation_parts)
        
        # If the last message wasn't from the user, add a prompt for assistant
        if messages and messages[-1].role != "user":
            prompt += "\n\nHuman: Please continue."
            
        return prompt, system_prompt
    
    @staticmethod
    def filter_content(content: str) -> str:
        """
        Filter content for unsupported features (like images).
        Replace image references with text placeholders.
        """
        # Pattern to match image references or base64 data
        image_pattern = r'\[Image:.*?\]|data:image/.*?;base64,.*?(?=\s|$)'
        
        def replace_image(match):
            return "[Image: Content not supported by Claude Code]"
        
        filtered = re.sub(image_pattern, replace_image, content)
        return filtered
    
    @staticmethod
    def format_claude_response(content: str, model: str, finish_reason: str = "stop") -> Dict[str, Any]:
        """Format Claude response for OpenAI compatibility."""
        return {
            "role": "assistant",
            "content": content,
            "finish_reason": finish_reason,
            "model": model
        }
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Rough estimation of token count.
        OpenAI's rule of thumb: ~4 characters per token for English text.
        """
        return len(text) // 4