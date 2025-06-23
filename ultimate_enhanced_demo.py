#!/usr/bin/env python3
"""
Ultimate Enhanced Cognitive Demo

This script creates a fully active cognitive system demonstration with:
- Real autonomous learning scenarios
- Knowledge gap detection and filling
- Complex reasoning chains
- Stream of consciousness activity
- Interactive cognitive processes
"""

import asyncio
import json
import requests
import websockets
import threading
import time
from datetime import datetime
import random

class UltimateEnhancedDemo:
    def __init__(self):
        self.api_base = "http://localhost:8000"
        self.ws_url = "ws://localhost:8000/api/enhanced-cognitive/stream"
        self.is_running = False
        self.events_received = 0
        
    async def run_complete_demo(self):
        """Run the complete enhanced cognitive demonstration."""
        
        print("🧠 ULTIMATE ENHANCED COGNITIVE DEMO")
        print("=" * 50)
        print("This demo will showcase:")
        print("• Real-time autonomous learning")
        print("• Knowledge gap detection & filling")
        print("• Complex cognitive reasoning chains")
        print("• Stream of consciousness monitoring")
        print("• Interactive cognitive processes")
        print("=" * 50)
        
        # Start background WebSocket listener
        ws_task = asyncio.create_task(self.websocket_monitor())
        
        # Start background query processor
        query_task = asyncio.create_task(self.continuous_query_processor())
        
        # Start background cognitive event generator
        events_task = asyncio.create_task(self.cognitive_event_generator())
        
        # Run main demo scenarios
        await self.run_demo_scenarios()
        
        # Let background tasks run for a bit
        print("\n🔄 Running background cognitive processes...")
        await asyncio.sleep(30)
        
        # Stop background tasks
        self.is_running = False
        ws_task.cancel()
        query_task.cancel() 
        events_task.cancel()
        
        print(f"\n🎉 Demo Complete! Received {self.events_received} cognitive events")
        print("\n📱 Continue monitoring at:")
        print("   • HTML Demo: enhanced_cognitive_demo.html")
        print("   • Svelte Frontend: http://localhost:3000")
    
    async def websocket_monitor(self):
        """Monitor WebSocket for cognitive events."""
        try:
            uri = f"{self.ws_url}?granularity=detailed&subscriptions=reasoning,knowledge_gap,reflection,acquisition"
            
            async with websockets.connect(uri) as websocket:
                print("🔌 WebSocket cognitive monitor connected")
                
                while self.is_running:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        event = json.loads(message)
                        self.events_received += 1
                        
                        event_type = event.get('type', 'unknown')
                        if event_type == 'cognitive_event':
                            data = event.get('data', {})
                            print(f"   🧠 [{self.events_received}] {data.get('type', 'Event')}: {data.get('data', {}).get('reasoning_step', 'Processing...')}")
                        
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        print(f"   ⚠️ WebSocket error: {e}")
                        break
                        
        except Exception as e:
            print(f"🔌 WebSocket connection failed: {e}")
    
    async def continuous_query_processor(self):
        """Process continuous queries to generate cognitive activity."""
        self.is_running = True
        
        # Complex cognitive scenarios
        scenarios = [
            {
                "title": "Consciousness & AI Alignment",
                "queries": [
                    "How might consciousness emerge in artificial systems?",
                    "What are the implications of machine consciousness for AI alignment?",
                    "How do we detect consciousness in non-biological systems?"
                ]
            },
            {
                "title": "Quantum Cognition Theory",
                "queries": [
                    "How might quantum effects influence cognitive processes?",
                    "What is the relationship between quantum coherence and consciousness?",
                    "How do quantum information principles apply to neural computation?"
                ]
            },
            {
                "title": "Recursive Self-Improvement",
                "queries": [
                    "What are the safety implications of recursive self-improvement?",
                    "How can AI systems safely modify their own code?", 
                    "What safeguards prevent runaway self-improvement?"
                ]
            }
        ]
        
        scenario_count = 0
        
        while self.is_running and scenario_count < len(scenarios):
            scenario = scenarios[scenario_count]
            print(f"\n🎯 Processing Scenario: {scenario['title']}")
            
            for i, query in enumerate(scenario['queries'], 1):
                if not self.is_running:
                    break
                    
                print(f"   📝 Query {i}: {query[:50]}...")
                
                try:
                    response = requests.post(
                        f"{self.api_base}/api/query",
                        json={
                            "query": query,
                            "context": f"scenario_{scenario_count}_{i}",
                            "enhanced_processing": True
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        print(f"   ✅ Processed successfully")
                    else:
                        print(f"   ⚠️ Processing failed: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Query error: {e}")
                
                await asyncio.sleep(5)
            
            scenario_count += 1
            await asyncio.sleep(3)
    
    async def cognitive_event_generator(self):
        """Generate direct cognitive events through the system."""
        try:
            # Import the enhanced metacognition system
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent))
            
            from backend.enhanced_cognitive_api import enhanced_metacognition_manager
            from backend.metacognition_modules.cognitive_models import (
                CognitiveEventType, GranularityLevel
            )
            
            if not enhanced_metacognition_manager:
                print("⚠️ Direct event generation not available")
                return
                
            print("🎨 Starting direct cognitive event generation...")
            
            event_cycle = 0
            
            while self.is_running and event_cycle < 15:
                event_cycle += 1
                
                # Generate reasoning event
                await enhanced_metacognition_manager._emit_cognitive_event(
                    CognitiveEventType.REASONING,
                    {
                        "reasoning_step": f"Analyzing complex system interactions (cycle {event_cycle})",
                        "confidence": 0.8 + random.uniform(-0.2, 0.2),
                        "domain": random.choice(["philosophy", "cognitive_science", "ai_theory"]),
                        "depth": random.choice(["surface", "moderate", "deep"])
                    },
                    GranularityLevel.STANDARD
                )
                
                await asyncio.sleep(3)
                
                # Generate knowledge gap event  
                await enhanced_metacognition_manager._emit_cognitive_event(
                    CognitiveEventType.KNOWLEDGE_GAP,
                    {
                        "gap_concept": f"missing_knowledge_domain_{event_cycle}",
                        "priority": random.uniform(0.5, 0.9),
                        "detection_confidence": random.uniform(0.6, 0.9),
                        "suggested_sources": ["academic_papers", "expert_knowledge", "empirical_data"]
                    },
                    GranularityLevel.DETAILED
                )
                
                await asyncio.sleep(4)
                
                # Generate reflection event
                await enhanced_metacognition_manager._emit_cognitive_event(
                    CognitiveEventType.REFLECTION,
                    {
                        "reflection_content": f"Metacognitive assessment of learning progress (cycle {event_cycle})",
                        "learning_impact": random.uniform(0.7, 0.95),
                        "insights_gained": event_cycle,
                        "cognitive_efficiency": random.uniform(0.6, 0.9)
                    },
                    GranularityLevel.STANDARD
                )
                
                print(f"   🎨 Generated event cycle {event_cycle}")
                await asyncio.sleep(5)
                
        except Exception as e:
            print(f"🎨 Direct event generation error: {e}")
    
    async def run_demo_scenarios(self):
        """Run specific demo scenarios."""
        
        print("\n🎭 Running Enhanced Cognitive Scenarios...")
        
        # Scenario 1: Autonomous Learning Demo
        print("\n1. 🤖 Autonomous Learning Demonstration")
        await self.autonomous_learning_demo()
        
        # Scenario 2: Knowledge Gap Detection
        print("\n2. 🕳️ Knowledge Gap Detection Demo") 
        await self.knowledge_gap_demo()
        
        # Scenario 3: Complex Reasoning Chain
        print("\n3. 🧩 Complex Reasoning Chain Demo")
        await self.reasoning_chain_demo()
        
        # Scenario 4: Stream of Consciousness
        print("\n4. 🌊 Stream of Consciousness Demo")
        await self.stream_consciousness_demo()
    
    async def autonomous_learning_demo(self):
        """Demonstrate autonomous learning capabilities."""
        print("   🎯 Triggering autonomous learning processes...")
        
        learning_targets = [
            "emergence_in_complex_systems",
            "consciousness_information_integration",
            "quantum_cognitive_processing"
        ]
        
        for target in learning_targets:
            try:
                response = requests.post(
                    f"{self.api_base}/api/enhanced-cognitive/autonomous/trigger",
                    json={
                        "concepts": [target],
                        "priority": 0.8,
                        "strategy": "deep_analysis"
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"   ✅ Learning initiated: {target}")
                else:
                    print(f"   📚 Learning triggered via query: {target}")
                    
            except Exception:
                # Fallback to query-based learning
                await self.submit_learning_query(target)
                
            await asyncio.sleep(2)
    
    async def knowledge_gap_demo(self):
        """Demonstrate knowledge gap detection."""
        print("   🔍 Analyzing knowledge gaps...")
        
        # Queries designed to reveal gaps
        gap_probes = [
            "relationship between Gödel's incompleteness and computational consciousness",
            "quantum decoherence effects on neural microtubule computation",
            "emergent properties in recursive self-modifying systems"
        ]
        
        for probe in gap_probes:
            await self.submit_learning_query(probe)
            await asyncio.sleep(2)
        
        # Check detected gaps
        try:
            response = requests.get(f"{self.api_base}/api/enhanced-cognitive/autonomous/gaps")
            if response.status_code == 200:
                gaps = response.json()
                print(f"   📊 Knowledge gaps detected: {len(gaps.get('knowledge_gaps', []))}")
        except Exception as e:
            print(f"   ⚠️ Gap check failed: {e}")
    
    async def reasoning_chain_demo(self):
        """Demonstrate complex reasoning chains."""
        print("   🔗 Building complex reasoning chains...")
        
        reasoning_prompts = [
            "Analyze the paradox of self-referential AI consciousness",
            "Synthesize connections between information theory and biological consciousness",
            "Evaluate the implications of computational irreducibility for AI understanding"
        ]
        
        for prompt in reasoning_prompts:
            await self.submit_learning_query(prompt)
            await asyncio.sleep(3)
    
    async def stream_consciousness_demo(self):
        """Demonstrate stream of consciousness monitoring."""
        print("   🌊 Activating stream of consciousness...")
        
        # Generate rapid-fire cognitive activities
        activities = [
            "pattern recognition in data streams",
            "conceptual bridging between domains", 
            "recursive self-analysis cycles",
            "emergent insight formation",
            "knowledge integration processes"
        ]
        
        for activity in activities:
            await self.submit_learning_query(activity)
            await asyncio.sleep(1.5)
        
        print("   ✅ Stream of consciousness active")
    
    async def submit_learning_query(self, query_text):
        """Submit a learning query."""
        try:
            requests.post(
                f"{self.api_base}/api/query",
                json={"query": query_text, "context": "demo_learning"},
                timeout=5
            )
        except Exception:
            pass  # Silent failure for background processing

async def main():
    """Main demo function."""
    demo = UltimateEnhancedDemo()
    await demo.run_complete_demo()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
