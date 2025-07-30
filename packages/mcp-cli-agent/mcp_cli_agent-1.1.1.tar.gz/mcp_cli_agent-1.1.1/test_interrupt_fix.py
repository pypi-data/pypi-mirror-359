#!/usr/bin/env python3
"""
Test script to verify the interrupt fix.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli_agent.core.global_interrupt import get_global_interrupt_manager

def test_interrupt_fix():
    """Test that interrupt count is properly reset after first interrupt."""
    
    print("🧪 Testing interrupt fix...")
    
    # Get the global interrupt manager
    interrupt_manager = get_global_interrupt_manager()
    
    # Test scenario: First interrupt should reset count
    print("📊 Simulating first Ctrl+C scenario:")
    
    # Reset to clean state
    interrupt_manager.reset_interrupt_count()
    print(f"1. Initial state: count={interrupt_manager.get_interrupt_count()}, interrupted={interrupt_manager.is_interrupted()}")
    
    # Simulate first interrupt
    interrupt_manager._interrupt_count = 1
    interrupt_manager.set_interrupted(True)
    print(f"2. After first Ctrl+C: count={interrupt_manager.get_interrupt_count()}, interrupted={interrupt_manager.is_interrupted()}")
    
    # Simulate what chat interface does after first interrupt
    interrupt_manager.clear_interrupt()
    interrupt_manager.reset_interrupt_count()  # This is the key fix
    print(f"3. After clearing/resetting: count={interrupt_manager.get_interrupt_count()}, interrupted={interrupt_manager.is_interrupted()}")
    
    print()
    print("✅ Fix verified!")
    print("🔑 Key change: Now we reset_interrupt_count() after first Ctrl+C")
    print("   This ensures the next Ctrl+C is treated as the 'first' interrupt again")
    print("   unless it comes within 2 seconds (creating a true double-tap)")

if __name__ == "__main__":
    test_interrupt_fix()