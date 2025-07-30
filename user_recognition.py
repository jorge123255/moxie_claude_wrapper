"""
User recognition system for Moxie to identify adults vs children
"""

import os
import json
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)

class UserType(Enum):
    CHILD = "child"
    ADULT = "adult"
    UNKNOWN = "unknown"

class UserProfile:
    """Represents a Moxie user profile"""
    def __init__(self, user_id: str, name: str, user_type: UserType, 
                 voice_profile: Optional[Dict] = None, face_id: Optional[str] = None):
        self.user_id = user_id
        self.name = name
        self.user_type = user_type
        self.voice_profile = voice_profile
        self.face_id = face_id
        self.last_seen = datetime.now()
        self.preferences = {}

class MoxieUserRecognition:
    """Handles user recognition and profile management for Moxie"""
    
    def __init__(self, profiles_path: str = "/app/profiles"):
        self.profiles_path = profiles_path
        self.profiles: Dict[str, UserProfile] = {}
        self.current_user: Optional[UserProfile] = None
        self.load_profiles()
    
    def load_profiles(self):
        """Load user profiles from storage"""
        os.makedirs(self.profiles_path, exist_ok=True)
        profiles_file = os.path.join(self.profiles_path, "users.json")
        
        if os.path.exists(profiles_file):
            try:
                with open(profiles_file, 'r') as f:
                    data = json.load(f)
                    for user_id, profile_data in data.items():
                        self.profiles[user_id] = UserProfile(
                            user_id=user_id,
                            name=profile_data['name'],
                            user_type=UserType(profile_data['user_type']),
                            voice_profile=profile_data.get('voice_profile'),
                            face_id=profile_data.get('face_id')
                        )
                logger.info(f"Loaded {len(self.profiles)} user profiles")
            except Exception as e:
                logger.error(f"Error loading profiles: {e}")
    
    def save_profiles(self):
        """Save user profiles to storage"""
        profiles_file = os.path.join(self.profiles_path, "users.json")
        data = {}
        
        for user_id, profile in self.profiles.items():
            data[user_id] = {
                'name': profile.name,
                'user_type': profile.user_type.value,
                'voice_profile': profile.voice_profile,
                'face_id': profile.face_id,
                'last_seen': profile.last_seen.isoformat(),
                'preferences': profile.preferences
            }
        
        with open(profiles_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def identify_user_by_voice(self, voice_features: Dict) -> Tuple[Optional[UserProfile], float]:
        """
        Identify user by voice characteristics
        Returns: (user_profile, confidence_score)
        """
        # In a real implementation, this would use voice biometrics
        # For now, we'll use a simple mock based on pitch
        pitch = voice_features.get('pitch', 0)
        
        # Simple heuristic: higher pitch often indicates younger/child voices
        if pitch > 200:  # Hz - typical child voice range
            # Look for matching child profile
            for profile in self.profiles.values():
                if profile.user_type == UserType.CHILD:
                    return profile, 0.8
        else:
            # Look for matching adult profile
            for profile in self.profiles.values():
                if profile.user_type == UserType.ADULT:
                    return profile, 0.8
        
        return None, 0.0
    
    def identify_user_by_face(self, face_id: str) -> Optional[UserProfile]:
        """Identify user by face recognition ID from Moxie's camera"""
        for profile in self.profiles.values():
            if profile.face_id == face_id:
                profile.last_seen = datetime.now()
                return profile
        return None
    
    def identify_user_by_code(self, code: str) -> Optional[UserProfile]:
        """Identify user by spoken code/password"""
        # Simple code-based identification
        code_to_user = {
            "red dragon": "adult_user_1",
            "blue unicorn": "child_user_1",
            "green robot": "adult_user_2",
            "purple star": "child_user_2"
        }
        
        user_id = code_to_user.get(code.lower())
        if user_id and user_id in self.profiles:
            profile = self.profiles[user_id]
            profile.last_seen = datetime.now()
            return profile
        return None
    
    def create_profile(self, name: str, user_type: UserType, 
                      voice_profile: Optional[Dict] = None, 
                      face_id: Optional[str] = None) -> UserProfile:
        """Create a new user profile"""
        user_id = f"{user_type.value}_{len(self.profiles) + 1}"
        profile = UserProfile(user_id, name, user_type, voice_profile, face_id)
        self.profiles[user_id] = profile
        self.save_profiles()
        return profile
    
    def get_interaction_mode(self, user_profile: Optional[UserProfile] = None) -> Dict:
        """
        Determine interaction settings based on user profile
        Returns dict with settings for the interaction
        """
        if not user_profile:
            # Default to child-safe mode when user unknown
            return {
                "child_mode": True,
                "content_filter": "strict",
                "voice_speed": "normal",
                "complexity": "simple"
            }
        
        if user_profile.user_type == UserType.CHILD:
            return {
                "child_mode": True,
                "content_filter": "strict",
                "voice_speed": "slightly_slow",
                "complexity": "simple",
                "encourage_learning": True,
                "user_name": user_profile.name
            }
        else:  # ADULT
            return {
                "child_mode": False,
                "content_filter": "none",
                "voice_speed": "normal",
                "complexity": "full",
                "user_name": user_profile.name
            }
    
    def update_current_user(self, user_profile: Optional[UserProfile]):
        """Update the current active user"""
        self.current_user = user_profile
        if user_profile:
            logger.info(f"Current user set to: {user_profile.name} ({user_profile.user_type.value})")
        else:
            logger.info("No active user")
    
    def get_current_user(self) -> Optional[UserProfile]:
        """Get the current active user"""
        return self.current_user


# Integration with OpenMoxie
class MoxieSessionManager:
    """Manages user sessions for Moxie interactions"""
    
    def __init__(self):
        self.user_recognition = MoxieUserRecognition()
        self.session_timeout = timedelta(minutes=30)
        self.last_activity = {}
    
    def start_session(self, identification_data: Dict) -> Dict:
        """
        Start a new Moxie session with user identification
        
        identification_data can contain:
        - voice_features: Dict with voice characteristics
        - face_id: String face recognition ID
        - spoken_code: String code/password
        - user_id: Direct user ID
        """
        user_profile = None
        confidence = 0.0
        
        # Try different identification methods
        if 'voice_features' in identification_data:
            user_profile, confidence = self.user_recognition.identify_user_by_voice(
                identification_data['voice_features']
            )
        
        if not user_profile and 'face_id' in identification_data:
            user_profile = self.user_recognition.identify_user_by_face(
                identification_data['face_id']
            )
            confidence = 0.9 if user_profile else 0.0
        
        if not user_profile and 'spoken_code' in identification_data:
            user_profile = self.user_recognition.identify_user_by_code(
                identification_data['spoken_code']
            )
            confidence = 1.0 if user_profile else 0.0
        
        if not user_profile and 'user_id' in identification_data:
            user_profile = self.user_recognition.profiles.get(identification_data['user_id'])
            confidence = 1.0 if user_profile else 0.0
        
        # Update current user
        self.user_recognition.update_current_user(user_profile)
        
        # Get interaction settings
        settings = self.user_recognition.get_interaction_mode(user_profile)
        
        return {
            "session_id": f"moxie_{datetime.now().timestamp()}",
            "user_profile": {
                "user_id": user_profile.user_id if user_profile else None,
                "name": user_profile.name if user_profile else "Friend",
                "type": user_profile.user_type.value if user_profile else "unknown"
            },
            "confidence": confidence,
            "settings": settings
        }