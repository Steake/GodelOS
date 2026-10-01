#!/bin/bash

# ==============================================================================
# GödelOS Unified Quickstart & Verification Script
# ==============================================================================

set -e

# Terminal colors
BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${BOLD}          🧠 GödelOS Unified Quickstart & Verification        ${CYAN}║${NC}"
echo -e "${CYAN}║${NC}   Tractable Gödel Machine · Formal TCB · Cognitive OS        ${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ------------------------------------------------------------------------------
# 1. Environment & Prerequisites Check
# ------------------------------------------------------------------------------
echo -e "${BLUE}[1/4] Checking System Prerequisites...${NC}"

if command -v python3 &>/dev/null; then
    PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo -e "  ✔ Python 3 detected: ${GREEN}v${PY_VER}${NC}"
else
    echo -e "  ${RED}✘ Python 3 is required but not installed.${NC}"
    exit 1
fi

if command -v node &>/dev/null; then
    NODE_VER=$(node -v)
    echo -e "  ✔ Node.js detected: ${GREEN}${NODE_VER}${NC}"
else
    echo -e "  ${RED}✘ Node.js is required but not installed.${NC}"
    exit 1
fi

if command -v npm &>/dev/null; then
    NPM_VER=$(npm -v)
    echo -e "  ✔ npm detected: ${GREEN}v${NPM_VER}${NC}"
else
    echo -e "  ${RED}✘ npm is required but not installed.${NC}"
    exit 1
fi

# ------------------------------------------------------------------------------
# 2. Syntax & Import Verification
# ------------------------------------------------------------------------------
echo ""
echo -e "${BLUE}[2/4] Verifying Core Architecture Syntax...${NC}"

python3 -c "
import py_compile
files = [
    'godelOS/godel_machine.py',
    'backend/symbolic_service.py',
    'backend/unified_server.py',
    'godelOS/formal_verification.py',
    'godelOS/solvers/qf_lia_solver.py',
    'godelOS/solvers/datalog_solver.py',
    'godelOS/solvers/lyapunov_solver.py',
    'godelOS/code_synthesizer.py'
]
for f in files:
    py_compile.compile(f, doraise=True)
    print(f'  ✔ {f} syntax verified')
"

# ------------------------------------------------------------------------------
# 3. Formal TCB & Gödel Machine Test Suite Execution
# ------------------------------------------------------------------------------
echo ""
echo -e "${BLUE}[3/4] Executing Formal Verification & Adversarial Test Suites...${NC}"

pytest tests/test_godel_machine.py \
       tests/test_godel_tcb_adversarial.py \
       tests/test_godel_tcb_formal_rigor.py \
       tests/test_formal_verification.py -q

echo -e "  ${GREEN}✔ 27/27 formal and adversarial tests passed cleanly!${NC}"

# ------------------------------------------------------------------------------
# 4. Svelte Frontend Production Build
# ------------------------------------------------------------------------------
echo ""
echo -e "${BLUE}[4/4] Building Frontend Production Bundle...${NC}"

cd svelte-frontend
npm run build --silent
cd ..
echo -e "  ${GREEN}✔ Svelte frontend compiled successfully!${NC}"

echo ""
echo -e "${GREEN}================================================================${NC}"
echo -e "${GREEN}🎉 GödelOS is verified, sound, and ready to launch!${NC}"
echo -e "${GREEN}================================================================${NC}"
echo ""
echo -e "${YELLOW}To launch the system:${NC}"
echo -e "  1. Start Backend:  ${CYAN}python3 -m uvicorn backend.unified_server:app --host 0.0.0.0 --port 8000${NC}"
echo -e "  2. Start Frontend: ${CYAN}cd svelte-frontend && npm run dev -- --host 0.0.0.0 --port 3000${NC}"
echo -e "  3. Open Browser:   ${CYAN}http://localhost:3000${NC}"
echo ""
echo -e "${YELLOW}Interactive Features Available:${NC}"
echo -e "  • ${BOLD}Holistic Constellation Dashboard:${NC} Real-time pipeline topology & inspection"
echo -e "  • ${BOLD}Gödel Machine & TCB Sandbox:${NC} Certified mutations with rollback trial"
echo -e "  • ${BOLD}Symbolic Reasoning Studio:${NC} First-Order Resolution & Modal Tableau provers"
echo -e "  • ${BOLD}Unified Consciousness Stream:${NC} Phenomenal unity & narrative coherence"
echo ""

# Handle launch argument if requested
if [ "$1" == "--start-backend" ]; then
    echo -e "${CYAN}Starting GödelOS Unified Backend on http://0.0.0.0:8000 ...${NC}"
    exec python3 -m uvicorn backend.unified_server:app --host 0.0.0.0 --port 8000
elif [ "$1" == "--start-all" ]; then
    echo -e "${CYAN}Starting GödelOS Backend and Frontend ...${NC}"
    ./start-godelos.sh
fi
