#!/usr/bin/env python3
"""
Continuous Cognitive Demo
Generates sustained, visible cognitive activity for demonstration purposes.
"""

import asyncio
import aiohttp
import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Enhanced cognitive events for demonstration
DEMO_SCENARIOS = [
    {
        "name": "Knowledge Gap Analysis",
        "description": "Analyzing gaps in quantum computing knowledge",
        "events": [
            {
                "type": "knowledge_gap_detected",
                "data": {
                    "domain": "quantum_computing",
                    "gap_type": "conceptual",
                    "description": "Limited understanding of quantum entanglement applications",
                    "confidence": 0.85,
                    "priority": "high"
                }
            },
            {
                "type": "learning_goal_created",
                "data": {
                    "goal": "Master quantum entanglement principles",
                    "target_domain": "quantum_computing",
                    "estimated_effort": "medium",
                    "resources_needed": ["academic papers", "simulations"]
                }
            }
        ]
    },
    {
        "name": "Autonomous Learning Session",
        "description": "Self-directed learning about machine learning advances",
        "events": [
            {
                "type": "autonomous_learning_initiated",
                "data": {
                    "topic": "transformer_architectures",
                    "trigger": "knowledge_gap",
                    "learning_strategy": "progressive_exploration"
                }
            },
            {
                "type": "knowledge_acquisition_progress",
                "data": {
                    "topic": "transformer_architectures",
                    "progress": 0.45,
                    "concepts_learned": ["attention_mechanisms", "multi_head_attention"],
                    "next_concepts": ["positional_encoding", "layer_normalization"]
                }
            }
        ]
    },
    {
        "name": "Metacognitive Reflection",
        "description": "Self-assessment and strategy adjustment",
        "events": [
            {
                "type": "metacognitive_reflection",
                "data": {
                    "focus": "learning_efficiency",
                    "insights": ["Visual learning more effective than text-only", "Spaced repetition improves retention"],
                    "strategy_adjustments": ["increase_visual_content", "implement_spaced_review"]
                }
            },
            {
                "type": "cognitive_strategy_updated",
                "data": {
                    "strategy": "learning_approach",
                    "changes": {
                        "visual_content_ratio": 0.7,
                        "review_intervals": [1, 3, 7, 14, 30]
                    },
                    "reason": "metacognitive_reflection"
                }
            }
        ]
    },
    {
        "name": "Real-time Problem Solving",
        "description": "Dynamic problem-solving with cognitive monitoring",
        "events": [
            {
                "type": "problem_solving_initiated",
                "data": {
                    "problem": "Optimize neural network architecture",
                    "complexity": "high",
                    "approach": "iterative_refinement"
                }
            },
            {
                "type": "cognitive_load_assessment",
                "data": {
                    "current_load": 0.75,
                    "capacity_utilization": "high",
                    "bottlenecks": ["working_memory", "attention_span"],
                    "recommendations": ["break_into_subproblems", "use_external_memory"]
                }
            },
            {
                "type": "solution_hypothesis",
                "data": {
                    "hypothesis": "Use attention mechanisms to improve feature selection",
                    "confidence": 0.72,
                    "supporting_evidence": ["recent research", "similar successful cases"],
                    "test_strategy": "small_scale_experiment"
                }
            }
        ]
    }
]

class ContinuousCognitiveDemo:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.running = False
        
    async def start_session(self):
        """Initialize the HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def close_session(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            
    async def send_cognitive_event(self, event: Dict[str, Any]) -> bool:
        """Send a cognitive event to the backend"""
        try:
            async with self.session.post(
                f"{self.base_url}/api/enhanced-cognitive/events",
                json=event,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    print(f"✅ Event sent: {event['type']}")
                    return True
                else:
                    print(f"❌ Failed to send event: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Error sending event: {e}")
            return False
            
    async def simulate_thinking_process(self, topic: str, duration: int = 30):
        """Simulate a continuous thinking process"""
        print(f"🧠 Starting thinking simulation: {topic}")
        
        thoughts = [
            f"Analyzing {topic}...",
            f"Considering different approaches to {topic}",
            f"Evaluating evidence related to {topic}",
            f"Synthesizing insights about {topic}",
            f"Drawing conclusions on {topic}",
            f"Identifying next steps for {topic}"
        ]
        
        for i in range(duration):
            thought = random.choice(thoughts)
            event = {
                "type": "thought_process",
                "data": {
                    "content": thought,
                    "topic": topic,
                    "step": i + 1,
                    "total_steps": duration,
                    "cognitive_load": random.uniform(0.3, 0.9),
                    "confidence": random.uniform(0.5, 0.95)
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.send_cognitive_event(event)
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
    async def run_scenario(self, scenario: Dict[str, Any]):
        """Run a specific cognitive scenario"""
        print(f"\n🎭 Running scenario: {scenario['name']}")
        print(f"📝 Description: {scenario['description']}")
        
        for i, event in enumerate(scenario['events']):
            # Add timestamp and sequence info
            event_with_meta = {
                **event,
                "timestamp": datetime.utcnow().isoformat(),
                "scenario": scenario['name'],
                "sequence": i + 1,
                "total_in_sequence": len(scenario['events'])
            }
            
            await self.send_cognitive_event(event_with_meta)
            
            # Realistic delays between events
            delay = random.uniform(2, 5)
            print(f"⏱️  Waiting {delay:.1f}s before next event...")
            await asyncio.sleep(delay)
            
    async def generate_autonomous_insights(self):
        """Generate autonomous insights and discoveries"""
        insights = [
            "Pattern recognition efficiency improved by 15%",
            "New correlation discovered between concepts A and B",
            "Learning strategy optimization yielding better results",
            "Memory consolidation process showing improvements",
            "Attention allocation strategy proving more effective"
        ]
        
        for insight in insights:
            event = {
                "type": "autonomous_insight",
                "data": {
                    "insight": insight,
                    "confidence": random.uniform(0.7, 0.95),
                    "impact_assessment": random.choice(["low", "medium", "high"]),
                    "suggested_actions": [
                        "incorporate_into_strategy",
                        "validate_with_experiments",
                        "share_with_learning_network"
                    ]
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await self.send_cognitive_event(event)
            await asyncio.sleep(random.uniform(3, 8))
            
    async def run_continuous_demo(self, duration_minutes: int = 10):
        """Run the continuous cognitive demonstration"""
        print(f"\n🚀 Starting Continuous Cognitive Demo")
        print(f"⏰ Duration: {duration_minutes} minutes")
        print(f"🌐 Backend: {self.base_url}")
        print("=" * 50)
        
        await self.start_session()
        
        try:
            self.running = True
            end_time = datetime.now() + timedelta(minutes=duration_minutes)
            
            # Create background tasks
            tasks = []
            
            # Task 1: Run scenarios in sequence
            async def scenario_runner():
                while self.running and datetime.now() < end_time:
                    scenario = random.choice(DEMO_SCENARIOS)
                    await self.run_scenario(scenario)
                    await asyncio.sleep(random.uniform(10, 20))
                    
            # Task 2: Simulate continuous thinking
            async def thinking_simulator():
                topics = [
                    "artificial intelligence",
                    "cognitive architecture",
                    "learning optimization",
                    "knowledge representation",
                    "metacognitive strategies"
                ]
                while self.running and datetime.now() < end_time:
                    topic = random.choice(topics)
                    await self.simulate_thinking_process(topic, random.randint(10, 25))
                    await asyncio.sleep(random.uniform(5, 15))
                    
            # Task 3: Generate autonomous insights
            async def insight_generator():
                while self.running and datetime.now() < end_time:
                    await self.generate_autonomous_insights()
                    await asyncio.sleep(random.uniform(15, 30))
            
            # Start all tasks
            tasks = [
                asyncio.create_task(scenario_runner()),
                asyncio.create_task(thinking_simulator()),
                asyncio.create_task(insight_generator())
            ]
            
            # Wait for completion
            try:
                await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=duration_minutes * 60
                )
            except asyncio.TimeoutError:
                print("⏰ Demo duration completed")
                
        except KeyboardInterrupt:
            print("\n⛔ Demo interrupted by user")
        finally:
            self.running = False
            for task in tasks:
                if not task.done():
                    task.cancel()
            await self.close_session()
            print("\n✅ Continuous Cognitive Demo completed")

async def main():
    demo = ContinuousCognitiveDemo()
    
    # Run a 10-minute continuous demo
    await demo.run_continuous_demo(duration_minutes=10)

if __name__ == "__main__":
    print("🧠 Enhanced GödelOS Continuous Cognitive Demo")
    print("============================================")
    print("This will generate sustained cognitive activity for 10 minutes.")
    print("Open http://localhost:3000 or enhanced_cognitive_demo.html to see the activity!")
    print("\nPress Ctrl+C to stop early\n")
    
    asyncio.run(main())
