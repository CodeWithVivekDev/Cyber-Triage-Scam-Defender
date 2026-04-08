#!/bin/bash
# Smart entrypoint for OpenEnv compliance
# Determines whether to run inference.py or fast_server.py based on context

# Check if we're in a testing/CI environment (OpenEnv Phase 1)
if [ "$OPENENV_PHASE" = "1" ] || [ "$RUN_INFERENCE" = "1" ]; then
    echo "Running in OpenEnv Phase 1 mode (inference)..."
    python inference.py
    exit $?
fi

# Check if OPENAI_API_KEY is set and we should run inference
if [ -n "$OPENAI_API_KEY" ] && [ "$RUN_SERVER" != "1" ]; then
    echo "Running inference.py..."
    python inference.py
    exit $?
fi

# Default to web server for interactive use (Hugging Face Spaces)
echo "Starting FastAPI web server..."
uvicorn fast_server:app --host 0.0.0.0 --port 7860
