#!/usr/bin/env bash
# test-bead-stats.sh - Test suite for bead-stats script

set -euo pipefail

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
RESET='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Script path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BEAD_STATS="${SCRIPT_DIR}/bead-stats"
FIXTURES_DIR="${SCRIPT_DIR}/test-fixtures"

# Helper: Print test status
print_test() {
    local status="$1"
    local name="$2"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if [[ "$status" == "PASS" ]]; then
        echo -e "${GREEN}✓${RESET} $name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗${RESET} $name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

# Helper: Run bead-stats and capture output
run_stats() {
    local file="$1"
    "$BEAD_STATS" -f "$file" 2>&1 || true
}

# Test 1: Empty beads file
test_empty_file() {
    echo ""
    echo "Test: Empty beads file"
    echo "────────────────────────────────────────"
    
    local output
    output=$(run_stats "${FIXTURES_DIR}/empty.jsonl")
    
    if echo "$output" | grep -q "The beads file exists but is empty"; then
        print_test "PASS" "Handles empty file gracefully"
    else
        print_test "FAIL" "Handles empty file gracefully"
        echo "Expected: 'The beads file exists but is empty'"
        echo "Got: $output"
    fi
}

# Test 2: Mixed status distribution
test_mixed_status() {
    echo ""
    echo "Test: Mixed status distribution"
    echo "────────────────────────────────────────"
    
    local output
    output=$(run_stats "${FIXTURES_DIR}/mixed-status.jsonl") || true
    
    # Check for key elements in output
    local pass=true
    
    if ! echo "$output" | grep -q "📊 BEAD STATS"; then
        pass=false
        echo "Missing: Stats header"
    fi
    
    if ! echo "$output" | grep -q "Open:.*2"; then
        pass=false
        echo "Missing: 2 open tasks"
    fi
    
    if ! echo "$output" | grep -q "Closed:.*2"; then
        pass=false
        echo "Missing: 2 closed tasks"
    fi
    
    if ! echo "$output" | grep -q "Blocked:.*1"; then
        pass=false
        echo "Missing: 1 blocked task"
    fi
    
    if ! echo "$output" | grep -q "In Progress:.*1"; then
        pass=false
        echo "Missing: 1 in progress task"
    fi
    
    if ! echo "$output" | grep -q "Total:.*6"; then
        pass=false
        echo "Missing: Total of 6 tasks"
    fi
    
    if [[ "$pass" == true ]]; then
        print_test "PASS" "Calculates status distribution correctly"
    else
        print_test "FAIL" "Calculates status distribution correctly"
    fi
}

# Test 3: No blockers scenario
test_no_blockers() {
    echo ""
    echo "Test: No blockers"
    echo "────────────────────────────────────────"
    
    local output
    output=$(run_stats "${FIXTURES_DIR}/no-blockers.jsonl")
    
    if echo "$output" | grep -q "No blockers 🎉"; then
        print_test "PASS" "Detects no blockers scenario"
    else
        print_test "FAIL" "Detects no blockers scenario"
        echo "Expected: 'No blockers 🎉'"
        echo "Got: $output"
    fi
}

# Test 4: All closed tasks
test_all_closed() {
    echo ""
    echo "Test: All tasks closed (100% completion)"
    echo "────────────────────────────────────────"
    
    local output
    output=$(run_stats "${FIXTURES_DIR}/all-closed.jsonl")
    
    local pass=true
    
    if ! echo "$output" | grep -q "Closed:.*4.*100%"; then
        pass=false
        echo "Missing: 100% closed"
    fi
    
    if ! echo "$output" | grep -q "Open:.*0"; then
        pass=false
        echo "Missing: 0 open tasks"
    fi
    
    if [[ "$pass" == true ]]; then
        print_test "PASS" "Shows 100% completion correctly"
    else
        print_test "FAIL" "Shows 100% completion correctly"
    fi
}

# Test 5: Blocker analysis
test_blockers() {
    echo ""
    echo "Test: Blocker analysis"
    echo "────────────────────────────────────────"
    
    local output
    output=$(run_stats "${FIXTURES_DIR}/with-blockers.jsonl")
    
    local pass=true
    
    if ! echo "$output" | grep -q "Top Blockers:"; then
        pass=false
        echo "Missing: Top Blockers section"
    fi
    
    if ! echo "$output" | grep -q "BLOCKER-001.*blocks 3 tasks"; then
        pass=false
        echo "Missing: BLOCKER-001 blocks 3 tasks"
    fi
    
    if ! echo "$output" | grep -q "BLOCKER-002.*blocks 1 task"; then
        pass=false
        echo "Missing: BLOCKER-002 blocks 1 task"
    fi
    
    if [[ "$pass" == true ]]; then
        print_test "PASS" "Identifies and ranks blockers correctly"
    else
        print_test "FAIL" "Identifies and ranks blockers correctly"
    fi
}

# Test 6: Missing status defaults to open
test_missing_status() {
    echo ""
    echo "Test: Missing status defaults to open"
    echo "────────────────────────────────────────"
    
    local output
    output=$(run_stats "${FIXTURES_DIR}/missing-status.jsonl")
    
    # Should have 2 open (defaults) + 1 closed = 3 total
    if echo "$output" | grep -q "Open:.*2"; then
        print_test "PASS" "Defaults missing status to 'open'"
    else
        print_test "FAIL" "Defaults missing status to 'open'"
        echo "Expected: 2 open tasks"
        echo "Got: $output"
    fi
}

# Test 7: Non-existent file
test_nonexistent_file() {
    echo ""
    echo "Test: Non-existent file error handling"
    echo "────────────────────────────────────────"
    
    local output
    local exit_code=0
    output=$("$BEAD_STATS" -f "/nonexistent/file.jsonl" 2>&1) || exit_code=$?
    
    if [[ $exit_code -ne 0 ]] && echo "$output" | grep -q "Beads file not found"; then
        print_test "PASS" "Handles non-existent file with proper error"
    else
        print_test "FAIL" "Handles non-existent file with proper error"
        echo "Expected: Exit code != 0 and 'Beads file not found'"
        echo "Got exit code: $exit_code"
        echo "Got output: $output"
    fi
}

# Main test runner
main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║          BEAD-STATS TEST SUITE                           ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    
    # Check if bead-stats exists
    if [[ ! -x "$BEAD_STATS" ]]; then
        echo -e "${RED}Error: bead-stats script not found or not executable${RESET}"
        echo "Path: $BEAD_STATS"
        exit 1
    fi
    
    # Check if fixtures directory exists
    if [[ ! -d "$FIXTURES_DIR" ]]; then
        echo -e "${RED}Error: Test fixtures directory not found${RESET}"
        echo "Path: $FIXTURES_DIR"
        exit 1
    fi
    
    # Run all tests
    test_empty_file
    test_mixed_status
    test_no_blockers
    test_all_closed
    test_blockers
    test_missing_status
    test_nonexistent_file
    
    # Summary
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║          TEST SUMMARY                                    ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    echo "Tests run:    $TESTS_RUN"
    echo -e "Tests passed: ${GREEN}$TESTS_PASSED${RESET}"
    
    if [[ $TESTS_FAILED -gt 0 ]]; then
        echo -e "Tests failed: ${RED}$TESTS_FAILED${RESET}"
        echo ""
        exit 1
    else
        echo -e "Tests failed: ${GREEN}0${RESET}"
        echo ""
        echo -e "${GREEN}✓ All tests passed!${RESET}"
        echo ""
        exit 0
    fi
}

main "$@"
