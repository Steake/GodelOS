# GödelOS

GödelOS is a comprehensive symbolic cognition engine with multiple modules, designed to represent and reason with knowledge using Typed Higher-Order Logic (HOL) with extensions for modality, probability, and defeasibility.

## Project Overview

GödelOS aims to be a highly modular and extensible symbolic cognition engine. Its architecture is designed around a central Knowledge Representation system using Typed Higher-Order Logic (HOL) with extensions for modality, probability, and defeasibility. A multi-strategy Inference Engine operates on this knowledge, coordinated by a central unit that selects appropriate reasoning techniques.

## Architecture

### Module 1: Core Knowledge Representation (KR) System

The KR system is the heart of GödelOS, responsible for representing, storing, and managing all forms of knowledge. It defines the syntax and semantics of the agent's internal language and provides foundational operations for knowledge manipulation.

#### Components

1. **FormalLogicParser (Module 1.1)**: Converts textual representations of logical formulae into canonical Abstract Syntax Tree (AST) structures.
2. **AbstractSyntaxTree (AST) Representation (Module 1.2)**: Defines the structure for representing logical expressions.
3. **UnificationEngine (Module 1.3)**: Determines if two logical expressions can be made syntactically identical by substituting variables with terms.
4. **TypeSystemManager (Module 1.4)**: Defines and manages the type hierarchy and performs type checking and inference.
5. **KnowledgeStoreInterface (KSI) (Module 1.5)**: Provides a unified API for storing, retrieving, updating, and deleting knowledge.
6. **ProbabilisticLogicModule (PLM) (Module 1.6)**: Manages and reasons with uncertain knowledge.
7. **BeliefRevisionSystem (BRS) (Module 1.7)**: Manages changes to the agent's belief set in a rational and consistent manner.

### Module 2: Inference Engine Architecture

The Inference Engine is responsible for all deductive reasoning. It takes goals and applies logical rules and knowledge from the KR system, employing multiple reasoning strategies.

#### Components

1. **InferenceCoordinator (Module 2.1)**: Receives reasoning tasks, analyzes goals, selects appropriate inference engines, and manages the proof search process.
2. **ProofObject Data Structure**: A standardized way to represent the outcome of a reasoning process, including proof steps if successful.
3. **ResolutionProver (Module 2.2)**: Proves goals using the resolution inference rule, primarily for First-Order Logic (FOL) and propositional logic.
4. **ModalTableauProver (Module 2.3)**: Determines the validity or satisfiability of formulae in various modal logics.
5. **SMTInterface (Module 2.4)**: Interfaces with external SMT solvers for theories like arithmetic, arrays, and bit-vectors.
6. **ConstraintLogicProgrammingModule (CLP) (Module 2.5)**: Provides a declarative framework for solving problems that combine logical deduction with constraint satisfaction.
7. **AnalogicalReasoningEngine (ARE) (Module 2.6)**: Identifies structural analogies between domains and supports analogical inference.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/godelOS.git
cd godelOS

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in development mode
pip install -e .
```

## Usage

Here are some basic examples of how to use GödelOS:

### Core Knowledge Representation Example

```python
from godelOS.core_kr.formal_logic_parser import parser
from godelOS.core_kr.type_system import manager

# Initialize the type system
type_system = manager.TypeSystemManager()

# Parse a logical formula
formula_str = "forall ?x. (Human(?x) -> Mortal(?x))"
parser_instance = parser.FormalLogicParser(type_system)
ast_node, errors = parser_instance.parse(formula_str)

if not errors:
    print(f"Successfully parsed: {formula_str}")
else:
    print(f"Parsing errors: {errors}")
```

### Inference Engine Example

```python
from godelOS.inference_engine.coordinator import InferenceCoordinator
from godelOS.core_kr.formal_logic_parser import parser
from godelOS.core_kr.knowledge_store import interface

# Initialize components
kr_interface = interface.KnowledgeStoreInterface()
coordinator = InferenceCoordinator(kr_interface)

# Add knowledge to the knowledge store
kr_interface.add_statement(parser.parse("Human(Socrates)")[0])
kr_interface.add_statement(parser.parse("forall ?x. (Human(?x) -> Mortal(?x))")[0])

# Create a goal
goal = parser.parse("Mortal(Socrates)")[0]

# Submit the goal to the inference coordinator
proof_result = coordinator.submit_goal(goal)

if proof_result.goal_achieved:
    print("Goal proven successfully!")
    print(f"Proof steps: {proof_result.proof_steps}")
else:
    print(f"Failed to prove goal: {proof_result.status_message}")
```

For more detailed examples, check the `examples/` directory:
- `simple_example.py`: Basic usage of the core components
- `core_kr_example.py`: Detailed example of the Knowledge Representation system
- `inference_engine_example.py`: Example of using the Inference Engine

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/godelOS.git
cd godelOS

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Project Structure

```
godelOS/
├── core_kr/                  # Core Knowledge Representation System
│   ├── ast/                  # Abstract Syntax Tree representation
│   ├── belief_revision/      # Belief Revision System
│   ├── formal_logic_parser/  # Parser for logical formulas
│   ├── knowledge_store/      # Knowledge storage interface
│   ├── probabilistic_logic/  # Probabilistic logic module
│   ├── type_system/          # Type system manager
│   └── unification_engine/   # Unification engine
├── inference_engine/         # Inference Engine Architecture
│   ├── analogical_reasoning_engine.py
│   ├── base_prover.py
│   ├── clp_module.py
│   ├── coordinator.py
│   ├── modal_tableau_prover.py
│   ├── proof_object.py
│   ├── resolution_prover.py
│   └── smt_interface.py
├── examples/                 # Usage examples
└── tests/                    # Test suite
```

## License

[MIT License](LICENSE)

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## Roadmap

For a list of planned features and modules, see [TODO.md](TODO.md).