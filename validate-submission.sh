#!/bin/bash
echo "Validating Cyber-Triage Scam Defender submission..."

# Check requirements
if [ ! -f "openenv.yaml" ]; then
    echo "ERROR: openenv.yaml not found."
    exit 1
fi
if [ ! -f "env.py" ]; then
    echo "ERROR: env.py not found."
    exit 1
fi
if [ ! -f "inference.py" ]; then
    echo "ERROR: inference.py not found."
    exit 1
fi

echo "All required files found."

# Test Docker build (Optional flag for full test)
if [ "$1" == "--build" ]; then
    echo "Testing Docker build..."
    docker build -t openenv-validation .
    if [ $? -ne 0 ]; then
        echo "ERROR: Docker build failed."
        exit 1
    fi
    echo "Docker build successful."
fi

echo "Validation passed! Ready for submission."
exit 0
