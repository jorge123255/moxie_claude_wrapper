"""
Moxie-specific integration features for Claude wrapper
"""

import re
import logging
from typing import Dict, Optional, List, Tuple

logger = logging.getLogger(__name__)

class MoxieEmotionDetector:
    """Detect emotions from text for Moxie animations"""
    
    EMOTION_PATTERNS = {
        "happy": [
            r"\b(happy|joy|excited|wonderful|great|amazing|fantastic|love|fun)\b",
            r"[!]{2,}",  # Multiple exclamation marks
            r"😊|😄|😃|🎉|❤️|💖"
        ],
        "sad": [
            r"\b(sad|sorry|miss|lonely|hurt|cry|tears)\b",
            r"😢|😭|💔"
        ],
        "curious": [
            r"\b(wonder|think|maybe|perhaps|interesting|hmm|curious)\b",
            r"\?{2,}",  # Multiple question marks
            r"🤔|🧐"
        ],
        "excited": [
            r"\b(wow|awesome|incredible|can't wait|exciting)\b",
            r"[!]{3,}",
            r"🤩|🎊|✨"
        ],
        "caring": [
            r"\b(care|help|support|understand|here for you|hug)\b",
            r"🤗|💕|🫂"
        ]
    }
    
    def detect_emotion(self, text: str) -> str:
        """Detect primary emotion from text"""
        text_lower = text.lower()
        emotion_scores = {}
        
        for emotion, patterns in self.EMOTION_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                score += len(matches)
            emotion_scores[emotion] = score
        
        # Get emotion with highest score
        if max(emotion_scores.values()) > 0:
            return max(emotion_scores, key=emotion_scores.get)
        return "neutral"

class MoxieContentFilter:
    """Filter content to ensure child-appropriate responses"""
    
    INAPPROPRIATE_WORDS = [
        # Add inappropriate words/phrases here
        # This is a simplified example
    ]
    
    def filter_response(self, text: str) -> str:
        """Filter and modify text to be child-appropriate"""
        # Remove any inappropriate content
        filtered_text = text
        
        # Ensure friendly tone
        filtered_text = self._ensure_friendly_tone(filtered_text)
        
        return filtered_text
    
    def _ensure_friendly_tone(self, text: str) -> str:
        """Make sure the tone is friendly and appropriate for children"""
        # Simple replacements for more child-friendly language
        replacements = {
            "I don't know": "That's a great question! Let me think about that",
            "I can't": "Let's see what we can do instead",
            "No": "Hmm, how about we try something else"
        }
        
        for old, new in replacements.items():
            if text.startswith(old):
                text = text.replace(old, new, 1)
        
        return text

class MoxieResponseEnhancer:
    """Enhance Claude responses for Moxie"""
    
    def __init__(self):
        self.emotion_detector = MoxieEmotionDetector()
        self.content_filter = MoxieContentFilter()
    
    def enhance_response(self, response_text: str, include_emotion: bool = True) -> Dict:
        """
        Enhance Claude's response for Moxie
        
        Returns:
            Dict with:
            - text: filtered response text
            - emotion: detected emotion
            - moxie_commands: list of Moxie-specific commands
        """
        # Filter content first
        filtered_text = self.content_filter.filter_response(response_text)
        
        # Detect emotion
        emotion = self.emotion_detector.detect_emotion(filtered_text)
        
        # Generate Moxie commands based on emotion
        moxie_commands = self._generate_moxie_commands(emotion, filtered_text)
        
        result = {
            "text": filtered_text,
            "emotion": emotion,
            "moxie_commands": moxie_commands
        }
        
        # Add TTSFM integration if emotion should be included
        if include_emotion:
            result["ttsfm_params"] = {
                "voice": "sage",
                "emotion": emotion,
                "emotion_instruction": self._get_emotion_instruction(emotion)
            }
        
        return result
    
    def _generate_moxie_commands(self, emotion: str, text: str) -> List[str]:
        """Generate Moxie-specific commands based on emotion and content"""
        commands = []
        
        # Map emotions to Moxie animations/expressions
        emotion_to_animation = {
            "happy": "cmd:animate:joy",
            "sad": "cmd:animate:sympathetic",
            "curious": "cmd:animate:thinking",
            "excited": "cmd:animate:celebrate",
            "caring": "cmd:animate:hug",
            "neutral": "cmd:animate:friendly"
        }
        
        if emotion in emotion_to_animation:
            commands.append(emotion_to_animation[emotion])
        
        # Add pauses for longer text
        if len(text) > 200:
            commands.append("cmd:pause:2")
        
        return commands
    
    def _get_emotion_instruction(self, emotion: str) -> str:
        """Get TTSFM emotion instruction"""
        emotion_instructions = {
            "happy": "Speak with joy and enthusiasm, upbeat and cheerful",
            "sad": "Speak with a gentle, sympathetic tone, slightly slower",
            "curious": "Speak with wonder and interest, rising intonation on questions",
            "excited": "Speak with high energy and excitement, faster pace",
            "caring": "Speak with warmth and compassion, gentle and reassuring",
            "neutral": "Speak in a friendly, conversational tone"
        }
        return emotion_instructions.get(emotion, emotion_instructions["neutral"])

def format_moxie_response(claude_response: str, enable_ttsfm: bool = False) -> Dict:
    """
    Format Claude's response for Moxie with all enhancements
    
    Args:
        claude_response: Raw response from Claude
        enable_ttsfm: Whether to include TTSFM parameters
        
    Returns:
        Enhanced response dict suitable for Moxie
    """
    enhancer = MoxieResponseEnhancer()
    enhanced = enhancer.enhance_response(claude_response, include_emotion=enable_ttsfm)
    
    # Build Moxie markup if commands exist
    if enhanced["moxie_commands"]:
        commands_markup = "\n".join([f"<{cmd}>" for cmd in enhanced["moxie_commands"]])
        enhanced["moxie_markup"] = f"{commands_markup}\n{enhanced['text']}"
    else:
        enhanced["moxie_markup"] = enhanced["text"]
    
    return enhanced