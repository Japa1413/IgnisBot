# IgnisBot Dockerfile
# Multi-stage build for optimized image size
# Force rebuild: 2025-01-11-02:00:00

FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 ignisbot && \
    mkdir -p /app/logs && \
    chown -R ignisbot:ignisbot /app

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/ignisbot/.local

# Copy application files - copy explicitly to ensure nothing is missed
# First copy root Python files
COPY --chown=ignisbot:ignisbot ignis_main.py /app/
COPY --chown=ignisbot:ignisbot requirements.txt /app/

# Copy all directories explicitly
COPY --chown=ignisbot:ignisbot utils/ /app/utils/
COPY --chown=ignisbot:ignisbot cogs/ /app/cogs/
COPY --chown=ignisbot:ignisbot services/ /app/services/
COPY --chown=ignisbot:ignisbot repositories/ /app/repositories/
COPY --chown=ignisbot:ignisbot events/ /app/events/
COPY --chown=ignisbot:ignisbot domain/ /app/domain/
COPY --chown=ignisbot:ignisbot config/ /app/config/ 2>/dev/null || true

# Set environment variables BEFORE switching user
ENV PATH=/home/ignisbot/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH
ENV PYTHONUNBUFFERED=1

# Verify files were copied (MUST run AFTER COPY, BEFORE USER switch)
# Run as root to verify, then switch user
RUN echo "=== Verifying copied files ===" && \
    ls -la /app/ && \
    echo "--- Contents of /app/utils/ ---" && \
    ls -la /app/utils/ && \
    echo "--- Checking for required files ---" && \
    test -f /app/utils/config.py && echo "✓ utils/config.py exists" || echo "✗ utils/config.py MISSING" && \
    test -f /app/utils/__init__.py && echo "✓ utils/__init__.py exists" || echo "✗ utils/__init__.py MISSING" && \
    test -f /app/ignis_main.py && echo "✓ ignis_main.py exists" || echo "✗ ignis_main.py MISSING" && \
    echo "--- Python path test (as root) ---" && \
    python -c "import sys; print('PYTHONPATH:', sys.path)" && \
    python -c "import os; print('Current dir:', os.getcwd()); print('Files in /app:', os.listdir('/app'))" && \
    echo "--- Testing import (as root) ---" && \
    PYTHONPATH=/app python -c "from utils.config import TOKEN; print('✓ Import successful!')" || echo "✗ Import failed" && \
    echo "=== Verification complete ==="

# Switch to non-root user (AFTER setting ENV and verification)
USER ignisbot

# Run the bot with explicit PYTHONPATH
CMD ["sh", "-c", "PYTHONPATH=/app:$PYTHONPATH python ignis_main.py"]

