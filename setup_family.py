#!/usr/bin/env python3
"""
Setup script to configure family members for Moxie
"""

import requests
import json

MOXIE_API = "http://localhost:8000"

def setup_family_profiles():
    """Create user profiles for a typical family"""
    
    print("Setting up Moxie family profiles...")
    
    # Adult profiles
    adults = [
        {"name": "Dad", "type": "adult", "voice_profile": {"avg_pitch": 120}},
        {"name": "Mom", "type": "adult", "voice_profile": {"avg_pitch": 180}},
    ]
    
    # Child profiles
    children = [
        {"name": "Emma", "type": "child", "voice_profile": {"avg_pitch": 250}},
        {"name": "Liam", "type": "child", "voice_profile": {"avg_pitch": 240}},
    ]
    
    all_users = adults + children
    
    for user in all_users:
        response = requests.post(
            f"{MOXIE_API}/v1/moxie/users",
            json=user
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Created profile for {user['name']} ({user['type']})")
            print(f"  User ID: {data['user_id']}")
        else:
            print(f"✗ Failed to create profile for {user['name']}: {response.text}")
    
    print("\n" + "="*50)
    print("Family profiles created!")
    print("\nVoice-based identification will work automatically based on pitch.")
    print("\nYou can also use code words:")
    print("- Adults say: 'red dragon' or 'green robot'")
    print("- Children say: 'blue unicorn' or 'purple star'")
    print("="*50)

def test_identification():
    """Test user identification"""
    
    print("\nTesting user identification...")
    
    # Test voice-based identification (adult)
    response = requests.post(
        f"{MOXIE_API}/v1/moxie/identify",
        json={"voice_features": {"pitch": 120}}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nAdult voice detected:")
        print(f"- User: {data['user_profile']['name']}")
        print(f"- Mode: {'Child' if data['settings']['child_mode'] else 'Adult'}")
        print(f"- Confidence: {data['confidence']}")
    
    # Test voice-based identification (child)
    response = requests.post(
        f"{MOXIE_API}/v1/moxie/identify",
        json={"voice_features": {"pitch": 250}}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nChild voice detected:")
        print(f"- User: {data['user_profile']['name']}")
        print(f"- Mode: {'Child' if data['settings']['child_mode'] else 'Adult'}")
        print(f"- Confidence: {data['confidence']}")
    
    # Test code word identification
    response = requests.post(
        f"{MOXIE_API}/v1/moxie/identify",
        json={"spoken_code": "blue unicorn"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nCode word 'blue unicorn' recognized:")
        print(f"- User: {data['user_profile']['name']}")
        print(f"- Mode: {'Child' if data['settings']['child_mode'] else 'Adult'}")

def show_registered_users():
    """Display all registered users"""
    
    response = requests.get(f"{MOXIE_API}/v1/moxie/users")
    
    if response.status_code == 200:
        data = response.json()
        print("\nRegistered Moxie Users:")
        print("="*40)
        for user in data['users']:
            print(f"- {user['name']} ({user['type']}) - ID: {user['user_id']}")

if __name__ == "__main__":
    setup_family_profiles()
    test_identification()
    show_registered_users()