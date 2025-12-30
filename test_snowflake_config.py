#!/usr/bin/env python3
"""
Standalone test script for Snowflake configuration
This runs the Snowflake assessment configurator directly without requiring Databricks authentication
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from databricks.labs.blueprint.tui import Prompts
from databricks.labs.lakebridge.assessments.configure_assessment import create_assessment_configurator
from databricks.labs.lakebridge.assessments import PROFILER_SOURCE_SYSTEM

def main():
    print("=" * 70)
    print("🚀 LAKEBRIDGE SNOWFLAKE CONFIGURATION TEST")
    print("=" * 70)
    print()
    print("📝 This test demonstrates the simplified Snowflake configuration")
    print("   with clear authentication options and comprehensive profiling")
    print()
    
    # Show available systems
    print("Available profiler source systems:")
    for i, system in enumerate(PROFILER_SOURCE_SYSTEM):
        print(f"[{i}] {system}")
    print()
    
    # Create prompts instance
    prompts = Prompts()
    
    # Let user select source system
    source_tech = prompts.choice("Select the source technology", PROFILER_SOURCE_SYSTEM).lower()
    print(f"Selected: {source_tech}")
    print()
    
    # Create assessment configurator
    try:
        print(f"Creating {source_tech} assessment configurator...")
        assessment = create_assessment_configurator(
            source_system=source_tech,
            product_name="lakebridge",
            prompts=prompts
        )
        print(f"✅ Created: {type(assessment).__name__}")
        print()
        
        print("=" * 70)
        print("📋 CONFIGURATION PREVIEW:")
        print("   • Authentication options clearly explained with JDBC examples")
        print("   • Comprehensive profiling (90-day lookback, all objects/metrics)")
        print("   • Simplified credential gathering like the original demo")
        print("=" * 70)
        print()
        
        # Run the configuration
        print("🔧 Starting configuration process...")
        assessment.run()
        
        print()
        print("✅ Configuration completed successfully!")
        print()
        print("🎯 NEXT STEPS:")
        print("   1. Your credentials are saved locally")
        print("   2. Assessment will profile all objects comprehensively")
        print("   3. Ready to run full Snowflake assessment with these settings")
        
    except KeyboardInterrupt:
        print("\n❌ Configuration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during configuration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()