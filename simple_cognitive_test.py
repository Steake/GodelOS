#!/usr/bin/env python3
"""
Simple cognitive event sender to test frontend updates
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def send_test_events():
    """Send a series of test cognitive events"""
    
    events = [
        {
            "type": "system_startup",
            "data": {
                "message": "Enhanced cognitive system initializing",
                "components": ["metacognition", "autonomous_learning", "streaming"],
                "timestamp": datetime.utcnow().isoformat()
            }
        },
        {
            "type": "knowledge_gap_detected", 
            "data": {
                "domain": "machine_learning",
                "gap_description": "Limited understanding of transformer attention mechanisms",
                "confidence": 0.85,
                "priority": "high",
                "suggested_resources": ["research papers", "interactive tutorials"]
            }
        },
        {
            "type": "autonomous_learning_initiated",
            "data": {
                "topic": "attention_mechanisms",
                "learning_strategy": "progressive_exploration",
                "estimated_duration": "2 hours",
                "resources_identified": 5
            }
        },
        {
            "type": "thought_process",
            "data": {
                "content": "Analyzing the relationship between attention and memory",
                "cognitive_load": 0.75,
                "focus_intensity": 0.85,
                "processing_mode": "analytical"
            }
        },
        {
            "type": "metacognitive_reflection",
            "data": {
                "insight": "Learning efficiency improves with spaced repetition",
                "confidence": 0.92,
                "impact": "strategy_adjustment",
                "next_actions": ["implement_spaced_review", "track_retention_metrics"]
            }
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        print("🧠 Sending test cognitive events...")
        
        for i, event in enumerate(events, 1):
            try:
                async with session.post(
                    "http://localhost:8000/api/enhanced-cognitive/events",
                    json=event,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ {i}/5 Event '{event['type']}' sent successfully")
                    else:
                        print(f"❌ {i}/5 Failed to send '{event['type']}': {response.status}")
                        
            except Exception as e:
                print(f"❌ {i}/5 Error sending '{event['type']}': {e}")
            
            # Wait between events
            await asyncio.sleep(2)
        
        print("\n🎉 Test events completed!")
        print("Check the frontend for updates...")

if __name__ == "__main__":
    asyncio.run(send_test_events())
