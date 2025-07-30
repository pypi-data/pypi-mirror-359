#!/usr/bin/env python3
"""
Test script to demonstrate the new interrupt behavior.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli_agent.core.global_interrupt import get_global_interrupt_manager

def test_interrupt_behavior():
    """Test the new two-stage interrupt behavior."""
    
    print("🧪 Testing new interrupt behavior...")
    print("This demonstrates the new Ctrl+C behavior:")
    print("1. First Ctrl+C: Interrupts operations and clears input")
    print("2. Second Ctrl+C: Exits the application")
    print()
    
    # Get the global interrupt manager
    interrupt_manager = get_global_interrupt_manager()
    
    # Test the interrupt count behavior
    print("📊 Testing interrupt count logic:")
    
    # Reset to clean state
    interrupt_manager.reset_interrupt_count()
    print(f"Initial interrupt count: {interrupt_manager.get_interrupt_count()}")
    
    # Simulate first interrupt
    interrupt_manager._interrupt_count = 1
    interrupt_manager._interrupted = True
    print(f"After first interrupt: count={interrupt_manager.get_interrupt_count()}, interrupted={interrupt_manager.is_interrupted()}")
    
    # Clear interrupt (what happens after first Ctrl+C)
    interrupt_manager.clear_interrupt()
    print(f"After clearing first interrupt: count={interrupt_manager.get_interrupt_count()}, interrupted={interrupt_manager.is_interrupted()}")
    
    # Simulate second interrupt
    interrupt_manager._interrupt_count = 2
    interrupt_manager._interrupted = True
    print(f"After second interrupt: count={interrupt_manager.get_interrupt_count()}, interrupted={interrupt_manager.is_interrupted()}")
    
    print()
    print("✅ Interrupt behavior test completed!")
    print()
    print("🔄 New behavior summary:")
    print("   First Ctrl+C  → 🛑 Operation interrupted and input cleared. Press Ctrl+C again to exit.")
    print("   Second Ctrl+C → 👋 Exiting...")
    print()
    print("🎯 Benefits:")
    print("   • First Ctrl+C clears current input and cancels operations")
    print("   • Allows continuing work after clearing unwanted input")
    print("   • Second Ctrl+C provides clean exit")
    print("   • Maintains operation interruption for long-running tasks")

if __name__ == "__main__":
    test_interrupt_behavior()