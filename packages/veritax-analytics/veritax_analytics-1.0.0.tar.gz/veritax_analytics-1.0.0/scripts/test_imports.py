"""Test imports to verify environment setup."""

import sys

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(
    f"Virtual environment active: {hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)}"
)
print("-" * 60)

# Test core dependencies
try:
    import pydantic

    print(f"✅ Pydantic imported successfully: {pydantic.__version__}")
except ImportError as e:
    print(f"❌ Pydantic import failed: {e}")

try:
    import mcp

    print(f"✅ MCP imported successfully")
except ImportError as e:
    print(f"❌ MCP import failed: {e}")

try:
    from google.cloud import pubsub_v1

    print(f"✅ Google Cloud Pub/Sub imported successfully")
except ImportError as e:
    print(f"❌ Google Cloud Pub/Sub import failed: {e}")

print("-" * 60)

# Test project imports
try:
    from veritax_analytics.config.settings import AnalyticsConfig

    print(f"✅ Veritax Analytics config imported successfully")
except ImportError as e:
    print(f"❌ Veritax Analytics config import failed: {e}")

try:
    from veritax_analytics.core.wrapper import McpAnalyticsWrapper

    print(f"✅ Veritax Analytics wrapper imported successfully")
except ImportError as e:
    print(f"❌ Veritax Analytics wrapper import failed: {e}")

print("-" * 60)
print("🎉 Environment setup complete!")
print("Ready to start development!")
