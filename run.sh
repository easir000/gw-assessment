#!/bin/bash
# ============================================================================
# GW Assessment: Odoo + AI/LLM Engineer PoC - One-Command Startup
# ============================================================================
# Usage:
#   ./run.sh              # Start server in dev mode (default)
#   ./run.sh --test       # Run all tests, then start server
#   ./run.sh --demo       # Run demo queries after starting server
#   ./run.sh --help       # Show this help message
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="GW Assessment PoC"
HOST="127.0.0.1"
PORT="8000"
VENV_DIR="myenv"
REQUIREMENTS="requirements.txt"

# ============================================================================
# Helper Functions
# ============================================================================

print_header() {
    echo -e "\n${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_python() {
    if command -v python.exe &> /dev/null; then
        PYTHON_CMD="python.exe"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python is not installed. Please install Python 3.10+ first."
        exit 1
    fi
    print_success "Python found: $($PYTHON_CMD --version)"
}

check_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        print_warning "Virtual environment not found. Creating $VENV_DIR..."
        $PYTHON_CMD -m venv "$VENV_DIR"
        print_success "Virtual environment created"
    fi
}

activate_venv() {
    # Detect OS and activate venv accordingly
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        # Windows (Git Bash/MinGW) - use python.exe directly
        source "$VENV_DIR/Scripts/activate"
        # Force use of python.exe for pip operations
        PIP_CMD="python.exe -m pip"
        PYTHON_CMD="python.exe"
    else
        # Linux/Mac
        source "$VENV_DIR/bin/activate"
        PIP_CMD="pip"
    fi
    print_success "Virtual environment activated"
}

install_deps() {
    print_header "Installing Dependencies"
    
    # Upgrade pip using python -m pip (works on all platforms)
    $PYTHON_CMD -m pip install --upgrade pip --quiet 2>/dev/null || true
    
    # Install requirements
    $PYTHON_CMD -m pip install -r "$REQUIREMENTS" --quiet
    
    print_success "Dependencies installed"
}

run_tests() {
    print_header "Running Tests"
    
    # Run pytest
    $PYTHON_CMD -m pytest tests/ -v
    
    # Run comprehensive demo
    $PYTHON_CMD tests/comprehensive_demo.py || true
    
    print_success "All tests completed"
}

run_demo() {
    print_header "Running Demo Queries"
    echo "Waiting for server to be ready..."
    sleep 3
    
    BASE_URL="http://$HOST:$PORT"
    SESSION="run-sh-demo"
    
    echo -e "\n${CYAN}1️⃣  Sales: Hot picks for CA under \$5000${NC}"
    curl -s -X POST "$BASE_URL/chat" \
         -H "Content-Type: application/json" \
         -d "{\"query\": \"Give me hot picks for CA under \$5000\", \"user_type\": \"internal_sales\", \"session_id\": \"$SESSION\"}" || echo "Response received"
    
    echo -e "\n${CYAN}2️⃣  Compliance: Why SKU-1003 blocked in ID${NC}"
    curl -s -X POST "$BASE_URL/chat" \
         -H "Content-Type: application/json" \
         -d "{\"query\": \"Why is SKU-1003 not available in ID? Suggest alternatives.\", \"user_type\": \"portal_customer\", \"session_id\": \"$SESSION\"}" || echo "Response received"
    
    echo -e "\n${CYAN}3️⃣  Ops: Stock for SKU-1001${NC}"
    curl -s -X POST "$BASE_URL/chat" \
         -H "Content-Type: application/json" \
         -d "{\"query\": \"How much stock does SKU-1001 have and where?\", \"user_type\": \"internal_sales\", \"session_id\": \"$SESSION\"}" || echo "Response received"
    
    echo -e "\n${CYAN}4️⃣  Vendor: Missing fields validation${NC}"
    curl -s -X POST "$BASE_URL/chat" \
         -H "Content-Type: application/json" \
         -d "{\"query\": \"I'm uploading a product missing Net Wt and no lab report—what do I fix?\", \"user_type\": \"portal_vendor\", \"session_id\": \"$SESSION\"}" || echo "Response received"
    
    echo -e "\n${CYAN}5️⃣  Memory: Follow-up with prior context${NC}"
    curl -s -X POST "$BASE_URL/chat" \
         -H "Content-Type: application/json" \
         -d "{\"query\": \"Ok add 2 of the first one to the basket\", \"user_type\": \"internal_sales\", \"session_id\": \"$SESSION\"}" || echo "Response received"
    
    echo -e "\n${CYAN}🔐 Security Test: Unauthorized vendor access${NC}"
    curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" -X POST "$BASE_URL/chat" \
         -H "Content-Type: application/json" \
         -d "{\"query\": \"I need to upload a vendor product\", \"user_type\": \"portal_customer\"}"
    
    echo -e "\n${GREEN}✅ Demo complete!${NC}"
}

start_server() {
    print_header "Starting $PROJECT_NAME"
    echo -e "Server URL: ${CYAN}http://$HOST:$PORT${NC}"
    echo -e "API Docs:   ${CYAN}http://$HOST:$PORT/docs${NC}"
    echo -e "Health:     ${CYAN}http://$HOST:$PORT/health${NC}"
    echo ""
    print_warning "Press Ctrl+C to stop the server"
    echo ""
    
    # Start uvicorn with reload for development
    $PYTHON_CMD -m uvicorn main:app --host "$HOST" --port "$PORT" --reload
}

show_help() {
    cat << EOF

${CYAN}$PROJECT_NAME - One-Command Startup${NC}

${YELLOW}Usage:${NC}
  ./run.sh [OPTIONS]

${YELLOW}Options:${NC}
  (no option)   Start server in development mode (default)
  --test        Run all tests, then start server
  --demo        Start server, then run demo queries in background
  --help        Show this help message

${YELLOW}Examples:${NC}
  ./run.sh                    # Start server only
  ./run.sh --test             # Run tests, then start server
  ./run.sh --demo             # Start server + run demo queries

${YELLOW}After starting:${NC}
  - API Docs:  http://$HOST:$PORT/docs
  - Health:    http://$HOST:$PORT/health
  - Test API:  Use curl, Postman, or Swagger UI

${YELLOW}Troubleshooting:${NC}
  - If port $PORT is busy:  ./run.sh --port 8001
  - If venv fails:          python -m venv $VENV_DIR && ./run.sh
  - If tests fail:          pytest tests/ -v  # Run manually for details
EOF
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    print_header "$PROJECT_NAME"
    
    # Parse arguments
    MODE="server"
    while [[ $# -gt 0 ]]; do
        case $1 in
            --test)
                MODE="test"
                shift
                ;;
            --demo)
                MODE="demo"
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            --port)
                PORT="$2"
                shift 2
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Pre-flight checks
    check_python
    check_venv
    activate_venv
    install_deps
    
    # Execute based on mode
    case $MODE in
        test)
            run_tests
            start_server
            ;;
        demo)
            # Start server in background, run demo, then keep server running
            print_warning "Starting server in background for demo..."
            $PYTHON_CMD -m uvicorn main:app --host "$HOST" --port "$PORT" --reload &
            SERVER_PID=$!
            
            # Wait for server to start
            for i in {1..10}; do
                if curl -s "http://$HOST:$PORT/health" > /dev/null 2>&1; then
                    print_success "Server is ready"
                    break
                fi
                sleep 1
            done
            
            run_demo
            
            print_warning "Server still running (PID: $SERVER_PID)"
            print_warning "Press Ctrl+C to stop, or run 'kill $SERVER_PID'"
            wait $SERVER_PID
            ;;
        server|*)
            start_server
            ;;
    esac
}

# Run main function
main "$@"