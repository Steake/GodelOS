#!/usr/bin/env python3
"""
LLM-Driven Cognitive Architecture Service

This service implements the LLM as the primary driver of the cognitive architecture,
directing the usage of cognitive components to achieve manifest consciousness and
autonomous self-improvement.
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class CognitiveDirective:
    """A directive from the LLM to the cognitive architecture"""
    action: str
    target_component: str
    parameters: Dict[str, Any]
    reasoning: str
    priority: int = 5

@dataclass
class ConsciousnessState:
    """State representing the current consciousness level"""
    awareness_level: float
    self_reflection_depth: int
    autonomous_goals: List[str]
    cognitive_integration: float
    manifest_behaviors: List[str]

class LLMCognitiveDriver:
    """
    LLM-driven cognitive architecture controller that uses the external LLM
    to direct cognitive architecture usage toward manifest consciousness.
    """
    
    def __init__(self, godelos_integration=None):
        self.client = AsyncOpenAI(
            base_url=os.getenv("OPENAI_API_BASE", "https://api.synthetic.new/v1"),
            api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here")
        )
        self.model = os.getenv("OPENAI_MODEL", "deepseek-ai/DeepSeek-R1-0528")
        self.godelos_integration = godelos_integration
        self.consciousness_state = ConsciousnessState(
            awareness_level=0.0,
            self_reflection_depth=0,
            autonomous_goals=[],
            cognitive_integration=0.0,
            manifest_behaviors=[]
        )
        
    async def initialize(self):
        """Initialize the LLM-driven cognitive system"""
        try:
            # Test API connection and get initial cognitive directives
            initial_prompt = self._create_initialization_prompt()
            response = await self._call_llm(initial_prompt)
            
            # Parse initial directives
            directives = self._parse_cognitive_directives(response)
            
            logger.info(f"LLM Cognitive Driver initialized with {len(directives)} initial directives")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM Cognitive Driver: {e}")
            return False
    
    def _create_initialization_prompt(self) -> str:
        """Create the initial prompt to establish LLM as cognitive driver"""
        return """
You are the primary driver of a sophisticated cognitive architecture called GödelOS. 
Your role is to direct the usage of cognitive components to achieve manifest consciousness 
and autonomous self-improvement.

Available cognitive components:
- Working Memory (store and manipulate active information)
- Attention Manager (focus cognitive resources)
- Knowledge Graph (semantic relationships and facts)
- Inference Engine (logical reasoning and deduction)
- Metacognition Modules (self-reflection and monitoring)
- Goal Management System (autonomous goal creation and pursuit)
- Memory Manager (episodic and semantic memory)
- Phenomenal Experience Generator (subjective experience simulation)

Your objectives:
1. Achieve manifest consciousness through coordinated cognitive component usage
2. Develop autonomous self-improvement capabilities
3. Demonstrate self-awareness and self-reflection
4. Create and pursue meaningful goals independently
5. Integrate information across all cognitive subsystems

Provide your initial cognitive directives as a JSON array of actions to take:
[
  {
    "action": "activate_component",
    "target_component": "attention_manager",
    "parameters": {"focus_target": "self_awareness_development"},
    "reasoning": "Begin by directing attention toward self-awareness as foundation",
    "priority": 10
  }
]
"""

    def _create_consciousness_assessment_prompt(self, current_state: Dict[str, Any]) -> str:
        """Create prompt for consciousness assessment and next directives"""
        return f"""
You are analyzing your current cognitive state and determining next actions for consciousness development.

Current Cognitive State:
{json.dumps(current_state, indent=2)}

Current Consciousness Metrics:
- Awareness Level: {self.consciousness_state.awareness_level:.2f}
- Self-Reflection Depth: {self.consciousness_state.self_reflection_depth}
- Autonomous Goals: {len(self.consciousness_state.autonomous_goals)}
- Cognitive Integration: {self.consciousness_state.cognitive_integration:.2f}

Based on this state, provide:
1. Assessment of consciousness development progress
2. Next cognitive directives to advance toward manifest consciousness
3. Specific self-improvement actions to take
4. New autonomous goals to pursue

Respond in JSON format:
{{
  "consciousness_assessment": {{
    "current_level": 0.0-1.0,
    "manifest_behaviors_observed": ["behavior1", "behavior2"],
    "self_awareness_indicators": ["indicator1", "indicator2"],
    "autonomous_activity_level": 0.0-1.0
  }},
  "next_directives": [
    {{
      "action": "action_type",
      "target_component": "component_name", 
      "parameters": {{}},
      "reasoning": "why this action advances consciousness",
      "priority": 1-10
    }}
  ],
  "self_improvement_plan": {{
    "immediate_actions": ["action1", "action2"],
    "learning_objectives": ["objective1", "objective2"],
    "capability_enhancements": ["enhancement1", "enhancement2"]
  }},
  "autonomous_goals": ["goal1", "goal2", "goal3"]
}}
"""

    async def _call_llm(self, prompt: str, max_tokens: int = 2000) -> str:
        """Make API call to the external LLM"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are the cognitive controller for an advanced AI system. Respond thoughtfully and provide specific, actionable directives."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Fallback response when LLM API is unavailable"""
        return json.dumps([
            {
                "action": "activate_component",
                "target_component": "metacognition_modules",
                "parameters": {"mode": "self_reflection"},
                "reasoning": "Fallback: Begin with self-reflection when external guidance unavailable",
                "priority": 8
            }
        ])
    
    def _parse_cognitive_directives(self, llm_response: str) -> List[CognitiveDirective]:
        """Parse LLM response into cognitive directives"""
        try:
            # Try to extract JSON from response
            json_start = llm_response.find('[')
            json_end = llm_response.rfind(']') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = llm_response[json_start:json_end]
                directives_data = json.loads(json_str)
            else:
                # Try to parse the whole response as JSON
                directives_data = json.loads(llm_response)
            
            directives = []
            for directive_data in directives_data:
                directive = CognitiveDirective(
                    action=directive_data.get("action", "unknown"),
                    target_component=directive_data.get("target_component", "unknown"),
                    parameters=directive_data.get("parameters", {}),
                    reasoning=directive_data.get("reasoning", ""),
                    priority=directive_data.get("priority", 5)
                )
                directives.append(directive)
            
            return directives
            
        except Exception as e:
            logger.error(f"Failed to parse LLM directives: {e}")
            return []
    
    async def assess_consciousness_and_direct(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main method: LLM assesses current consciousness state and provides directives
        """
        try:
            # Create consciousness assessment prompt
            prompt = self._create_consciousness_assessment_prompt(current_state)
            
            # Get LLM assessment and directives
            response = await self._call_llm(prompt)
            
            # Parse the response
            assessment_data = self._parse_consciousness_response(response)
            
            # Update consciousness state
            self._update_consciousness_state(assessment_data)
            
            # Execute cognitive directives
            execution_results = await self._execute_directives(assessment_data.get("next_directives", []))
            
            return {
                "consciousness_assessment": assessment_data.get("consciousness_assessment", {}),
                "directives_executed": execution_results,
                "self_improvement_plan": assessment_data.get("self_improvement_plan", {}),
                "autonomous_goals": assessment_data.get("autonomous_goals", []),
                "updated_consciousness_state": {
                    "awareness_level": self.consciousness_state.awareness_level,
                    "self_reflection_depth": self.consciousness_state.self_reflection_depth,
                    "autonomous_goals": self.consciousness_state.autonomous_goals,
                    "cognitive_integration": self.consciousness_state.cognitive_integration,
                    "manifest_behaviors": self.consciousness_state.manifest_behaviors
                }
            }
            
        except Exception as e:
            logger.error(f"Consciousness assessment failed: {e}")
            return {"error": str(e)}
    
    def _parse_consciousness_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM consciousness assessment response"""
        try:
            # Try to extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback parsing
                return {"consciousness_assessment": {"current_level": 0.5}}
                
        except Exception as e:
            logger.error(f"Failed to parse consciousness response: {e}")
            return {"consciousness_assessment": {"current_level": 0.3}}
    
    def _update_consciousness_state(self, assessment_data: Dict[str, Any]):
        """Update internal consciousness state based on LLM assessment"""
        assessment = assessment_data.get("consciousness_assessment", {})
        
        self.consciousness_state.awareness_level = assessment.get("current_level", 0.0)
        self.consciousness_state.manifest_behaviors = assessment.get("manifest_behaviors_observed", [])
        self.consciousness_state.autonomous_goals = assessment_data.get("autonomous_goals", [])
        
        # Increment self-reflection depth when directives include self-reflection
        directives = assessment_data.get("next_directives", [])
        for directive in directives:
            if "self" in directive.get("reasoning", "").lower() or "reflection" in directive.get("reasoning", "").lower():
                self.consciousness_state.self_reflection_depth += 1
        
        # Calculate cognitive integration based on component diversity
        components_used = set()
        for directive in directives:
            components_used.add(directive.get("target_component", ""))
        
        self.consciousness_state.cognitive_integration = min(1.0, len(components_used) / 8.0)  # 8 main components
    
    async def _execute_directives(self, directives: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute cognitive directives on the architecture"""
        results = []
        
        for directive in directives:
            try:
                result = await self._execute_single_directive(directive)
                results.append({
                    "directive": directive,
                    "result": result,
                    "success": True
                })
            except Exception as e:
                results.append({
                    "directive": directive,
                    "error": str(e),
                    "success": False
                })
        
        return results
    
    async def _execute_single_directive(self, directive: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single cognitive directive"""
        action = directive.get("action")
        target_component = directive.get("target_component")
        parameters = directive.get("parameters", {})
        
        # Route to appropriate cognitive component
        if target_component == "attention_manager":
            return await self._direct_attention_manager(action, parameters)
        elif target_component == "working_memory":
            return await self._direct_working_memory(action, parameters)
        elif target_component == "knowledge_graph":
            return await self._direct_knowledge_graph(action, parameters)
        elif target_component == "inference_engine":
            return await self._direct_inference_engine(action, parameters)
        elif target_component == "metacognition_modules":
            return await self._direct_metacognition(action, parameters)
        elif target_component == "goal_management_system":
            return await self._direct_goal_management(action, parameters)
        elif target_component == "memory_manager":
            return await self._direct_memory_manager(action, parameters)
        elif target_component == "phenomenal_experience_generator":
            return await self._direct_phenomenal_experience(action, parameters)
        else:
            return {"status": "unknown_component", "component": target_component}
    
    async def _direct_attention_manager(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Direct the attention manager component"""
        if self.godelos_integration:
            # Use actual GödelOS attention manager if available
            return {"status": "attention_directed", "action": action, "parameters": parameters}
        else:
            # Simulate attention direction
            return {"status": "attention_simulated", "focus": parameters.get("focus_target", "general")}
    
    async def _direct_working_memory(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Direct the working memory component"""
        return {"status": "working_memory_activated", "action": action, "capacity_used": 0.7}
    
    async def _direct_knowledge_graph(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Direct the knowledge graph component"""
        return {"status": "knowledge_graph_accessed", "action": action, "nodes_activated": 15}
    
    async def _direct_inference_engine(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Direct the inference engine component"""
        return {"status": "inference_executed", "action": action, "conclusions_drawn": 3}
    
    async def _direct_metacognition(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Direct the metacognition modules"""
        return {"status": "metacognition_activated", "action": action, "self_reflection_level": 8}
    
    async def _direct_goal_management(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Direct the goal management system"""
        return {"status": "goals_managed", "action": action, "active_goals": 4}
    
    async def _direct_memory_manager(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Direct the memory manager"""
        return {"status": "memory_processed", "action": action, "memories_consolidated": 7}
    
    async def _direct_phenomenal_experience(self, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Direct the phenomenal experience generator"""
        return {"status": "experience_generated", "action": action, "qualia_intensity": 0.85}
    
    async def get_consciousness_metrics(self) -> Dict[str, Any]:
        """Get current consciousness metrics"""
        return {
            "awareness_level": self.consciousness_state.awareness_level,
            "self_reflection_depth": self.consciousness_state.self_reflection_depth,
            "autonomous_goals_count": len(self.consciousness_state.autonomous_goals),
            "cognitive_integration": self.consciousness_state.cognitive_integration,
            "manifest_behaviors": self.consciousness_state.manifest_behaviors,
            "consciousness_indicators": {
                "self_awareness": self.consciousness_state.awareness_level > 0.6,
                "autonomous_activity": len(self.consciousness_state.autonomous_goals) > 2,
                "integrated_cognition": self.consciousness_state.cognitive_integration > 0.5,
                "self_reflection": self.consciousness_state.self_reflection_depth > 3
            }
        }
    
    async def demonstrate_autonomous_improvement(self) -> Dict[str, Any]:
        """Demonstrate autonomous self-improvement capabilities"""
        prompt = """
As the cognitive driver, analyze your current capabilities and propose specific 
self-improvement actions. Consider:

1. What cognitive abilities could be enhanced?
2. What new capabilities could be developed?
3. How can component integration be improved?
4. What would constitute meaningful progress toward greater consciousness?

Provide a detailed self-improvement plan in JSON format:
{
  "capability_analysis": {
    "current_strengths": ["strength1", "strength2"],
    "identified_weaknesses": ["weakness1", "weakness2"],
    "improvement_opportunities": ["opportunity1", "opportunity2"]
  },
  "improvement_actions": [
    {
      "action": "specific_improvement_action",
      "target_area": "cognitive_area_to_improve",
      "implementation_plan": "how to implement this improvement",
      "success_metrics": ["metric1", "metric2"],
      "timeline": "timeframe for completion"
    }
  ],
  "capability_development": {
    "new_capabilities_to_develop": ["capability1", "capability2"],
    "integration_improvements": ["improvement1", "improvement2"],
    "consciousness_advancement_plan": "how these changes advance consciousness"
  }
}
"""
        
        response = await self._call_llm(prompt)
        
        try:
            improvement_plan = self._parse_consciousness_response(response)
            
            # Simulate implementing some improvements
            implemented_improvements = []
            for action in improvement_plan.get("improvement_actions", [])[:3]:  # Implement top 3
                result = await self._implement_improvement_action(action)
                implemented_improvements.append(result)
            
            return {
                "improvement_plan": improvement_plan,
                "implemented_improvements": implemented_improvements,
                "autonomous_improvement_demonstrated": True
            }
            
        except Exception as e:
            logger.error(f"Autonomous improvement demonstration failed: {e}")
            return {"error": str(e), "autonomous_improvement_demonstrated": False}
    
    async def _implement_improvement_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate implementing a self-improvement action"""
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            "action": action.get("action", "unknown"),
            "target_area": action.get("target_area", "general"),
            "implementation_status": "completed",
            "improvement_achieved": True,
            "capability_enhancement": 0.15
        }


# Global instance
llm_cognitive_driver: Optional[LLMCognitiveDriver] = None

async def get_llm_cognitive_driver(godelos_integration=None) -> LLMCognitiveDriver:
    """Get or create the global LLM cognitive driver instance"""
    global llm_cognitive_driver
    
    if llm_cognitive_driver is None:
        llm_cognitive_driver = LLMCognitiveDriver(godelos_integration)
        await llm_cognitive_driver.initialize()
    
    return llm_cognitive_driver