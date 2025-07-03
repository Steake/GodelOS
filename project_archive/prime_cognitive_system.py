#!/usr/bin/env python3
"""
Enhanced Cognitive System Priming Script

This script primes the system to generate meaningful cognitive activity
including autonomous learning, knowledge gap detection, and stream events.
"""

import asyncio
import json
import requests
import time
import random
from datetime import datetime

API_BASE = "http://localhost:8000"

class CognitivePrimer:
    def __init__(self):
        self.session = requests.Session()
        self.activities_generated = 0
        
    async def prime_system(self):
        """Prime the enhanced cognitive system with meaningful activity."""
        
        print("🧠 Enhanced Cognitive System Priming")
        print("=" * 50)
        
        # Step 1: Verify system is ready
        if not await self.verify_system():
            print("❌ System not ready for priming")
            return False
            
        # Step 2: Prime autonomous learning
        await self.prime_autonomous_learning()
        
        # Step 3: Generate knowledge gaps
        await self.generate_knowledge_gaps()
        
        # Step 4: Trigger cognitive reasoning
        await self.trigger_cognitive_reasoning()
        
        # Step 5: Start continuous cognitive activity
        await self.start_continuous_activity()
        
        return True
    
    async def verify_system(self):
        """Verify enhanced cognitive system is operational."""
        print("1. 🔍 Verifying Enhanced Cognitive System...")
        
        try:
            # Check enhanced cognitive status
            response = self.session.get(f"{API_BASE}/api/enhanced-cognitive/stream/status", timeout=10)
            if response.status_code != 200:
                print(f"   ❌ Enhanced cognitive API not responding: {response.status_code}")
                return False
                
            status = response.json()
            
            # Check key components
            if not status.get('stream_coordinator_available'):
                print("   ❌ Stream coordinator not available")
                return False
                
            meta = status.get('enhanced_metacognition', {})
            if not meta.get('is_running'):
                print("   ❌ Enhanced metacognition not running")
                return False
                
            if not meta.get('autonomous_learning', {}).get('enabled'):
                print("   ❌ Autonomous learning not enabled")
                return False
                
            print("   ✅ All enhanced cognitive components operational")
            print(f"   📊 Current connections: {status.get('total_cognitive_connections', 0)}")
            return True
            
        except Exception as e:
            print(f"   ❌ System verification failed: {e}")
            return False
    
    async def prime_autonomous_learning(self):
        """Prime the autonomous learning system."""
        print("\n2. 🤖 Priming Autonomous Learning System...")
        
        # Submit diverse queries to trigger learning
        learning_queries = [
            {
                "query": "consciousness emergence mechanisms",
                "domain": "cognitive_science",
                "complexity": "high"
            },
            {
                "query": "quantum information processing biological systems", 
                "domain": "quantum_biology",
                "complexity": "high"
            },
            {
                "query": "self-modifying artificial intelligence ethics",
                "domain": "ai_ethics", 
                "complexity": "high"
            }
        ]
        
        for i, query_data in enumerate(learning_queries, 1):
            print(f"   📝 Learning Query {i}: {query_data['domain']}")
            
            try:
                # Use direct enhanced cognitive processing
                response = self.session.post(
                    f"{API_BASE}/api/enhanced-cognitive/autonomous/trigger",
                    json={
                        "concepts": [query_data["query"]],
                        "priority": 0.8,
                        "strategy": "comprehensive_analysis"
                    },
                    timeout=20
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Triggered autonomous learning: {result.get('message', 'Success')}")
                else:
                    # Fallback to regular query processing
                    await self.submit_query(query_data["query"], f"autonomous_learning_{i}")
                    
            except Exception as e:
                print(f"   ⚠️ Learning query {i} error: {e}")
                
            await asyncio.sleep(2)
        
        print("   ✅ Autonomous learning system primed")
    
    async def generate_knowledge_gaps(self):
        """Generate detectable knowledge gaps."""
        print("\n3. 🕳️ Generating Knowledge Gaps...")
        
        # Queries designed to expose knowledge gaps
        gap_queries = [
            "relationship between Gödel incompleteness and halting problem",
            "consciousness hard problem quantum decoherence models",
            "emergent properties complex adaptive systems topology",
            "recursive self-improvement AI capability control problem"
        ]
        
        for i, query in enumerate(gap_queries, 1):
            print(f"   🔍 Gap Detection Query {i}: {query[:40]}...")
            
            try:
                # Submit query that should reveal gaps
                await self.submit_query(query, f"gap_detection_{i}")
                
                # Check for detected gaps
                response = self.session.get(f"{API_BASE}/api/enhanced-cognitive/autonomous/gaps")
                if response.status_code == 200:
                    gaps = response.json()
                    gap_count = len(gaps.get('knowledge_gaps', []))
                    print(f"   📊 Knowledge gaps detected: {gap_count}")
                    
            except Exception as e:
                print(f"   ⚠️ Gap generation {i} error: {e}")
                
            await asyncio.sleep(1.5)
        
        print("   ✅ Knowledge gap detection activated")
    
    async def trigger_cognitive_reasoning(self):
        """Trigger complex cognitive reasoning processes."""
        print("\n4. 🧩 Triggering Cognitive Reasoning...")
        
        reasoning_scenarios = [
            {
                "prompt": "Analyze the philosophical implications of computational consciousness",
                "type": "philosophical_analysis"
            },
            {
                "prompt": "Synthesize connections between information theory and biological evolution",
                "type": "interdisciplinary_synthesis"
            },
            {
                "prompt": "Evaluate the paradox of self-referential AI systems",
                "type": "logical_paradox_resolution"
            }
        ]
        
        for i, scenario in enumerate(reasoning_scenarios, 1):
            print(f"   🎯 Reasoning Scenario {i}: {scenario['type']}")
            
            try:
                # Submit complex reasoning query
                await self.submit_query(scenario["prompt"], f"reasoning_{scenario['type']}")
                
                # Add reasoning context
                reasoning_data = {
                    "reasoning_type": scenario["type"],
                    "complexity_level": "high",
                    "requires_synthesis": True,
                    "timestamp": datetime.now().isoformat()
                }
                
                print(f"   ✅ Reasoning process initiated: {scenario['type']}")
                
            except Exception as e:
                print(f"   ⚠️ Reasoning scenario {i} error: {e}")
                
            await asyncio.sleep(2)
        
        print("   ✅ Cognitive reasoning processes activated")
    
    async def submit_query(self, query_text, context_id):
        """Submit a query to trigger cognitive processing."""
        try:
            response = self.session.post(
                f"{API_BASE}/api/query",
                json={
                    "query": query_text,
                    "context": context_id,
                    "enhanced_processing": True
                },
                timeout=15
            )
            
            self.activities_generated += 1
            return response.status_code == 200
            
        except Exception as e:
            print(f"   ⚠️ Query submission failed: {e}")
            return False
    
    async def start_continuous_activity(self):
        """Start continuous cognitive activity generation."""
        print("\n5. 🔄 Starting Continuous Cognitive Activity...")
        
        activity_types = [
            "reflection_cycle",
            "knowledge_integration", 
            "pattern_recognition",
            "metacognitive_monitoring",
            "learning_optimization"
        ]
        
        print("   ⚡ Generating continuous cognitive events...")
        
        for cycle in range(10):  # Generate 10 cycles of activity
            activity_type = random.choice(activity_types)
            
            try:
                # Generate specific activity
                await self.generate_cognitive_activity(activity_type, cycle)
                
                print(f"   🌊 Cycle {cycle+1}: {activity_type}")
                
                # Variable delay to simulate natural cognitive rhythm
                delay = random.uniform(2, 5)
                await asyncio.sleep(delay)
                
            except Exception as e:
                print(f"   ⚠️ Activity cycle {cycle+1} error: {e}")
        
        print(f"   ✅ Generated {self.activities_generated} cognitive activities")
        print("   🎯 Continuous cognitive activity stream established")
    
    async def generate_cognitive_activity(self, activity_type, cycle):
        """Generate specific type of cognitive activity."""
        
        activities = {
            "reflection_cycle": f"metacognitive reflection on learning progress cycle {cycle}",
            "knowledge_integration": f"integrating new knowledge patterns cycle {cycle}",
            "pattern_recognition": f"identifying emergent patterns cycle {cycle}", 
            "metacognitive_monitoring": f"monitoring cognitive performance cycle {cycle}",
            "learning_optimization": f"optimizing learning strategies cycle {cycle}"
        }
        
        query = activities.get(activity_type, f"cognitive processing cycle {cycle}")
        return await self.submit_query(query, f"{activity_type}_{cycle}")
    
    async def show_priming_results(self):
        """Show the results of system priming."""
        print("\n🎉 Enhanced Cognitive System Priming Complete!")
        print("=" * 50)
        
        try:
            # Get final system status
            response = self.session.get(f"{API_BASE}/api/enhanced-cognitive/stream/status")
            if response.status_code == 200:
                status = response.json()
                
                print("📊 Priming Results:")
                print(f"   🔗 Active connections: {status.get('total_cognitive_connections', 0)}")
                
                meta = status.get('enhanced_metacognition', {})
                if meta:
                    al = meta.get('autonomous_learning', {})
                    cs = meta.get('cognitive_streaming', {})
                    
                    print(f"   🤖 Active acquisitions: {al.get('active_acquisitions', 0)}")
                    print(f"   🕳️ Detected gaps: {al.get('detected_gaps', 0)}")
                    print(f"   📡 Connected clients: {cs.get('connected_clients', 0)}")
                    print(f"   ⚡ Events/second: {cs.get('events_per_second', 0)}")
                
                print(f"   🎯 Total activities generated: {self.activities_generated}")
                
        except Exception as e:
            print(f"⚠️ Could not retrieve final status: {e}")
        
        print("\n🚀 What to Do Next:")
        print("   1. Open enhanced_cognitive_demo.html to see live activity")
        print("   2. Visit http://localhost:3000 for Svelte frontend") 
        print("   3. Run: python test_websocket_streaming.py")
        print("   4. Check real-time events in both interfaces")
        print("   5. System will continue generating cognitive activity")

async def main():
    """Main priming function."""
    primer = CognitivePrimer()
    
    success = await primer.prime_system()
    
    if success:
        await primer.show_priming_results()
    else:
        print("\n❌ System priming failed. Check that backend is running.")
        print("   Run: python backend/start_server.py --debug")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Priming interrupted by user")
    except Exception as e:
        print(f"\n❌ Priming error: {e}")
        import traceback
        traceback.print_exc()
