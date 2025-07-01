#!/usr/bin/env python3
"""
Direct Cognitive Event Generator

This script directly generates cognitive events through the enhanced metacognition
system to ensure visible streaming activity.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def generate_direct_cognitive_events():
    """Generate cognitive events directly through the enhanced metacognition system."""
    
    print("🧠 Direct Cognitive Event Generation")
    print("=" * 40)
    
    try:
        # Import enhanced metacognition components
        from backend.enhanced_cognitive_api import enhanced_metacognition_manager
        from backend.metacognition_modules.cognitive_models import (
            CognitiveEventType, GranularityLevel, CognitiveEvent
        )
        
        if not enhanced_metacognition_manager:
            print("❌ Enhanced metacognition manager not available")
            return False
            
        print("✅ Enhanced metacognition manager available")
        
        # Generate diverse cognitive events
        events_to_generate = [
            {
                "type": CognitiveEventType.REASONING,
                "data": {
                    "reasoning_step": "Analyzing relationship between consciousness and information processing",
                    "confidence": 0.85,
                    "domain": "cognitive_science",
                    "complexity": "high",
                    "context": ["philosophy_of_mind", "information_theory"]
                },
                "granularity": GranularityLevel.STANDARD
            },
            {
                "type": CognitiveEventType.KNOWLEDGE_GAP,
                "data": {
                    "gap_concept": "quantum_consciousness_interface",
                    "priority": 0.9,
                    "confidence": 0.75,
                    "related_domains": ["quantum_physics", "neuroscience", "consciousness_studies"],
                    "acquisition_strategy": "interdisciplinary_synthesis"
                },
                "granularity": GranularityLevel.DETAILED
            },
            {
                "type": CognitiveEventType.REFLECTION,
                "data": {
                    "reflection_content": "Metacognitive analysis of learning patterns and knowledge integration",
                    "learning_impact": 0.8,
                    "insights": [
                        "Cross-domain knowledge synthesis enhances understanding",
                        "Recursive self-analysis improves cognitive performance",
                        "Gap detection enables targeted learning"
                    ],
                    "context": ["self_monitoring", "cognitive_enhancement"]
                },
                "granularity": GranularityLevel.STANDARD
            },
            {
                "type": CognitiveEventType.ACQUISITION,
                "data": {
                    "acquisition_target": "emergent_properties_complex_systems",
                    "status": "initiated",
                    "progress": 0.3,
                    "sources": ["complexity_theory", "systems_science", "emergence_research"],
                    "estimated_completion": "processing"
                },
                "granularity": GranularityLevel.DETAILED
            }
        ]
        
        print(f"\n🎯 Generating {len(events_to_generate)} cognitive events...")
        
        for i, event_config in enumerate(events_to_generate, 1):
            try:
                await enhanced_metacognition_manager._emit_cognitive_event(
                    event_config["type"],
                    event_config["data"], 
                    event_config["granularity"]
                )
                
                print(f"   ✅ Event {i}: {event_config['type'].value}")
                
                # Delay between events for realistic streaming
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"   ❌ Event {i} failed: {e}")
        
        # Generate reasoning chain
        print(f"\n🔗 Generating reasoning chain...")
        reasoning_chain = [
            "Initial problem analysis",
            "Knowledge retrieval from relevant domains", 
            "Pattern recognition across domains",
            "Hypothesis formation",
            "Logical inference steps",
            "Conclusion synthesis",
            "Confidence assessment",
            "Knowledge gap identification"
        ]
        
        for i, step in enumerate(reasoning_chain, 1):
            await enhanced_metacognition_manager._emit_cognitive_event(
                CognitiveEventType.REASONING,
                {
                    "reasoning_step": step,
                    "chain_position": i,
                    "total_steps": len(reasoning_chain),
                    "confidence": 0.7 + (i * 0.03),
                    "reasoning_type": "analytical_chain"
                },
                GranularityLevel.DETAILED
            )
            
            print(f"   🔗 Step {i}: {step}")
            await asyncio.sleep(1)
        
        # Generate autonomous learning cycle
        print(f"\n🤖 Generating autonomous learning cycle...")
        learning_cycle = [
            ("gap_detection", "Detecting knowledge gaps in current understanding"),
            ("priority_assessment", "Assessing gap priority for learning"),
            ("acquisition_planning", "Planning knowledge acquisition strategy"),
            ("active_learning", "Actively acquiring new knowledge"),
            ("integration", "Integrating new knowledge with existing"),
            ("validation", "Validating learning outcomes"),
            ("optimization", "Optimizing learning strategies")
        ]
        
        for i, (phase, description) in enumerate(learning_cycle, 1):
            # Alternate between different event types based on phase
            if "gap" in phase:
                event_type = CognitiveEventType.KNOWLEDGE_GAP
            elif "acquisition" in phase or "learning" in phase:
                event_type = CognitiveEventType.ACQUISITION
            else:
                event_type = CognitiveEventType.REFLECTION
            
            await enhanced_metacognition_manager._emit_cognitive_event(
                event_type,
                {
                    "learning_phase": phase,
                    "description": description,
                    "cycle_position": i,
                    "total_phases": len(learning_cycle),
                    "autonomous": True
                },
                GranularityLevel.STANDARD
            )
            
            print(f"   🔄 Phase {i}: {phase}")
            await asyncio.sleep(1.5)
        
        print(f"\n✅ Direct cognitive event generation complete!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure the backend is running and enhanced cognitive system is initialized")
        return False
    except Exception as e:
        print(f"❌ Event generation error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def continuous_event_stream():
    """Generate continuous stream of cognitive events."""
    print(f"\n🌊 Starting continuous cognitive event stream...")
    
    try:
        from backend.enhanced_cognitive_api import enhanced_metacognition_manager
        from backend.metacognition_modules.cognitive_models import (
            CognitiveEventType, GranularityLevel
        )
        
        if not enhanced_metacognition_manager:
            print("❌ Enhanced metacognition manager not available")
            return
        
        event_templates = [
            (CognitiveEventType.REASONING, "processing_conceptual_relationships"),
            (CognitiveEventType.REFLECTION, "metacognitive_self_assessment"),
            (CognitiveEventType.KNOWLEDGE_GAP, "identifying_learning_opportunities"),
            (CognitiveEventType.ACQUISITION, "expanding_knowledge_base")
        ]
        
        stream_count = 0
        max_events = 20  # Limit for demo
        
        while stream_count < max_events:
            stream_count += 1
            
            # Select event type
            event_type, activity = event_templates[stream_count % len(event_templates)]
            
            # Generate contextual data
            event_data = {
                "activity": activity,
                "stream_position": stream_count,
                "timestamp": "real_time",
                "cognitive_load": 0.6 + (stream_count % 4) * 0.1,
                "processing_depth": ["shallow", "moderate", "deep"][stream_count % 3]
            }
            
            try:
                await enhanced_metacognition_manager._emit_cognitive_event(
                    event_type,
                    event_data,
                    GranularityLevel.STANDARD
                )
                
                print(f"   💫 Stream {stream_count}: {event_type.value} - {activity}")
                
                # Variable delay for natural rhythm
                import random
                delay = random.uniform(3, 6)
                await asyncio.sleep(delay)
                
            except Exception as e:
                print(f"   ❌ Stream event {stream_count} failed: {e}")
        
        print(f"   ✅ Generated {stream_count} continuous stream events")
        
    except Exception as e:
        print(f"❌ Continuous stream error: {e}")

async def main():
    """Main event generation function."""
    print("🚀 Enhanced Cognitive System Event Priming")
    print("=" * 50)
    
    # Generate direct events
    success = await generate_direct_cognitive_events()
    
    if success:
        # Start continuous stream
        await continuous_event_stream()
        
        print("\n🎉 Cognitive Event Priming Complete!")
        print("=" * 40)
        print("🌐 Now check your demo interfaces:")
        print("   • HTML Demo: enhanced_cognitive_demo.html")
        print("   • Svelte Frontend: http://localhost:3000")
        print("   • WebSocket Test: python test_websocket_streaming.py")
        print("\n💡 You should now see active cognitive events streaming!")
    else:
        print("\n❌ Event priming failed. Ensure backend is running with enhanced cognitive features.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Event generation stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
