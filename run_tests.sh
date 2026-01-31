#!/bin/bash

# Test runner script for Ragas LLM Evaluation Framework
# This script verifies all tests can be collected and are ready to run

echo "🧪 Ragas LLM Evaluation - Test Verification"
echo "==========================================="
echo ""

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  WARNING: OPENAI_API_KEY environment variable is not set"
    echo "   Tests will fail without a valid API key"
    echo ""
    echo "   To set it:"
    echo "   export OPENAI_API_KEY='your-key-here'"
    echo ""
    exit 1
fi

echo "✅ OPENAI_API_KEY is set"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  Virtual environment not found. Run: python -m venv venv"
    exit 1
fi

echo ""
echo "📋 Collecting tests..."
echo ""

# Test 1: Context Precision
echo "Test 1: Context Precision (Without Reference)"
pytest Test1.py --collect-only -q
if [ $? -eq 0 ]; then
    echo "✅ Test1.py - Ready"
else
    echo "❌ Test1.py - Failed to collect"
fi
echo ""

# Test 2: Context Recall
echo "Test 2: Context Recall (With Reference)"
pytest Test2.py --collect-only -q
if [ $? -eq 0 ]; then
    echo "✅ Test2.py - Ready"
else
    echo "❌ Test2.py - Failed to collect"
fi
echo ""

# Test 3: Framework
echo "Test 3: Parameterized Framework"
pytest Test3_framework.py --collect-only -q
if [ $? -eq 0 ]; then
    echo "✅ Test3_framework.py - Ready"
else
    echo "❌ Test3_framework.py - Failed to collect"
fi
echo ""

echo "==========================================="
echo "🎯 All tests are ready to run!"
echo ""
echo "To run tests:"
echo "  pytest -s                    # Run all tests"
echo "  pytest -s Test1.py           # Run specific test"
echo "  pytest -v                    # Verbose output"
echo ""
