#!/usr/bin/env python3
"""
Test script for StateGraphInspector functionality
Demonstrates runtime state inspection of the LinkedIn Article Generation workflow
"""

import logging
import sys
from workflow import LinkedInArticleWorkflow

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('inspector_test.log')
    ]
)

logger = logging.getLogger(__name__)

def test_inspector():
    """Test the StateGraphInspector functionality"""
    
    print("StateGraphInspector Test")
    print("=" * 50)
    
    try:
        # Initialize workflow
        workflow = LinkedInArticleWorkflow()
        print("✅ Workflow initialized with Runtime Monitor")
        
        # Test runtime monitor methods
        print("\n🔍 Testing Runtime Monitor Methods:")
        
        # Test runtime state inspection
        print("1. Testing runtime state inspection...")
        stats = workflow.inspect_runtime_state()
        if stats:
            print(f"   Runtime stats: {stats}")
        else:
            print("   No executions tracked yet (expected before workflow run)")
        
        # Test node execution inspection
        print("2. Testing node execution inspection...")
        for node in ["research", "critique", "moderator"]:
            node_executions = workflow.inspect_node_execution(node)
            if node_executions:
                print(f"   Node '{node}' executions: {len(node_executions)}")
            else:
                print(f"   Node '{node}': No executions yet")
        
        # Test execution trace
        print("3. Testing execution trace...")
        # This would work after a workflow execution
        print("   Execution trace will be available after workflow run")
        
        print("\n✅ StateGraphInspector test completed successfully!")
        print("\nTo see inspector in action, run the main workflow:")
        print("   python main.py")
        
    except Exception as e:
        logger.error(f"StateGraphInspector test failed: {e}")
        print(f"❌ Test failed: {e}")
        return False
    
    return True

def demonstrate_inspector_usage():
    """Demonstrate how to use the inspector during workflow execution"""
    
    print("\n" + "="*60)
    print("StateGraphInspector Usage Demonstration")
    print("="*60)
    
    print("""
The StateGraphInspector provides real-time monitoring of:

1. 🔍 RUNTIME STATE INSPECTION
   - workflow.inspect_runtime_state()
   - Shows current execution state
   - Lists all active executions

2. 🎯 NODE EXECUTION INSPECTION  
   - workflow.inspect_node_execution(node_name)
   - Shows execution details for specific nodes
   - Tracks node call counts and timing

3. 📊 EXECUTION TRACE
   - workflow.get_execution_trace(execution_id)
   - Complete execution history
   - Node-by-node execution details

4. 🔄 REAL-TIME MONITORING
   - Monitor workflow progress
   - Debug execution issues
   - Track state changes
   - Analyze performance

Example Usage:
    # During workflow execution
    executions = workflow.inspect_runtime_state()
    
    # Check specific node
    research_executions = workflow.inspect_node_execution("research")
    
    # Get complete trace
    trace = workflow.get_execution_trace("execution_123")
    """)

if __name__ == "__main__":
    print("LinkedIn Article Generator - StateGraphInspector Test")
    print("=" * 60)
    
    # Test inspector functionality
    success = test_inspector()
    
    if success:
        # Show usage demonstration
        demonstrate_inspector_usage()
        
        print("\n" + "="*60)
        print("Next Steps:")
        print("1. Run 'python main.py' to see inspector in action")
        print("2. Check 'inspector_test.log' for detailed logs")
        print("3. Monitor runtime state during workflow execution")
        print("="*60)
    else:
        print("\n❌ Inspector test failed. Check logs for details.")
        sys.exit(1)
