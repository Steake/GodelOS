"""
Simple example demonstrating how the GödelOS components interact.

This example creates a simple knowledge base with a few facts and rules,
and demonstrates how to use the various components of the GödelOS system.
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from godelOS.core_kr.type_system.manager import TypeSystemManager
from godelOS.core_kr.ast.nodes import (
    ConstantNode, VariableNode, ApplicationNode, ConnectiveNode
)
from godelOS.core_kr.formal_logic_parser.parser import FormalLogicParser
from godelOS.core_kr.unification_engine.engine import UnificationEngine
from godelOS.core_kr.knowledge_store.interface import KnowledgeStoreInterface
from godelOS.core_kr.probabilistic_logic.module import ProbabilisticLogicModule
from godelOS.core_kr.belief_revision.system import BeliefRevisionSystem


def main():
    """Run the example."""
    print("GödelOS Simple Example")
    print("=====================")
    
    # Initialize the type system
    print("\nInitializing Type System...")
    type_system = TypeSystemManager()
    
    # Create some basic types
    entity_type = type_system.get_type("Entity")
    human_type = type_system.define_atomic_type("Human", ["Entity"])
    
    # Define some predicates
    type_system.define_function_signature("Mortal", ["Entity"], "Boolean")
    type_system.define_function_signature("Human", ["Entity"], "Boolean")
    
    print(f"Defined types: Entity, Human")
    print(f"Defined predicates: Mortal(Entity) -> Boolean, Human(Entity) -> Boolean")
    
    # Initialize the parser
    print("\nInitializing Parser...")
    parser = FormalLogicParser(type_system)
    
    # Initialize the unification engine
    print("\nInitializing Unification Engine...")
    unification_engine = UnificationEngine(type_system)
    
    # Initialize the knowledge store
    print("\nInitializing Knowledge Store...")
    ksi = KnowledgeStoreInterface(type_system)
    
    # Create some AST nodes manually (normally this would be done by the parser)
    print("\nCreating AST nodes...")
    
    # Constants
    socrates = ConstantNode("Socrates", human_type)
    print(f"Created constant: Socrates: {human_type}")
    
    # Predicates
    human_pred = ConstantNode("Human", type_system.get_type("Human"))
    mortal_pred = ConstantNode("Mortal", type_system.get_type("Mortal"))
    print(f"Created predicates: Human, Mortal")
    
    # Applications
    human_socrates = ApplicationNode(
        human_pred, 
        [socrates], 
        type_system.get_type("Boolean")
    )
    mortal_socrates = ApplicationNode(
        mortal_pred, 
        [socrates], 
        type_system.get_type("Boolean")
    )
    print(f"Created applications: Human(Socrates), Mortal(Socrates)")
    
    # Add facts to the knowledge store
    print("\nAdding facts to the knowledge store...")
    ksi.add_statement(human_socrates, context_id="TRUTHS")
    print(f"Added fact: Human(Socrates)")
    
    # Create a rule: All humans are mortal
    print("\nCreating rule: All humans are mortal...")
    
    # Create a variable for the rule
    x_var = VariableNode("?x", 1, entity_type)
    
    # Create the antecedent: Human(?x)
    human_x = ApplicationNode(
        human_pred, 
        [x_var], 
        type_system.get_type("Boolean")
    )
    
    # Create the consequent: Mortal(?x)
    mortal_x = ApplicationNode(
        mortal_pred, 
        [x_var], 
        type_system.get_type("Boolean")
    )
    
    # Create the implication: Human(?x) => Mortal(?x)
    all_humans_mortal = ConnectiveNode(
        "IMPLIES", 
        [human_x, mortal_x], 
        type_system.get_type("Boolean")
    )
    
    # Add the rule to the knowledge store
    ksi.add_statement(all_humans_mortal, context_id="TRUTHS")
    print(f"Added rule: Human(?x) => Mortal(?x)")
    
    # Query the knowledge store
    print("\nQuerying the knowledge store...")
    results = ksi.query_statements_match_pattern(human_socrates, context_ids=["TRUTHS"])
    print(f"Query: Human(Socrates)")
    print(f"Results: {results}")
    
    # Demonstrate unification
    print("\nDemonstrating unification...")
    query_var = VariableNode("?who", 2, human_type)
    query = ApplicationNode(
        human_pred, 
        [query_var], 
        type_system.get_type("Boolean")
    )
    
    bindings, errors = unification_engine.unify(query, human_socrates)
    if bindings:
        print(f"Unified query Human(?who) with Human(Socrates)")
        print(f"Bindings: ?who -> Socrates")
    else:
        print(f"Failed to unify: {errors}")
    
    # Demonstrate inference (simplified)
    print("\nDemonstrating inference (simplified)...")
    print(f"Given: Human(Socrates) and Human(?x) => Mortal(?x)")
    print(f"We can infer: Mortal(Socrates)")
    
    # In a real implementation, this would use the inference engine
    # For now, we just add the inferred fact to the knowledge store
    ksi.add_statement(mortal_socrates, context_id="TRUTHS")
    
    # Query the inferred fact
    results = ksi.query_statements_match_pattern(mortal_socrates, context_ids=["TRUTHS"])
    print(f"Query: Mortal(Socrates)")
    print(f"Results: {results}")
    
    print("\nExample completed successfully!")


if __name__ == "__main__":
    main()