#!/usr/bin/env python3
"""Quick test to verify hooks system fixes."""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_hook_events():
    """Test that hook events have required attributes."""
    from cli_agent.core.hooks.hook_events import HookExecutionStartEvent, HookExecutionCompleteEvent
    from cli_agent.core.event_system import EventType
    
    # Test start event
    start_event = HookExecutionStartEvent(
        hook_type="PreToolUse",
        hook_command="echo test"
    )
    
    assert start_event.event_type == EventType.SYSTEM
    assert hasattr(start_event, 'system_type')
    assert start_event.system_type == "hook_execution_start"
    
    # Test complete event
    complete_event = HookExecutionCompleteEvent(
        hook_type="PostToolUse", 
        hook_command="echo test"
    )
    
    assert complete_event.event_type == EventType.SYSTEM
    assert hasattr(complete_event, 'system_type')
    assert complete_event.system_type == "hook_execution_complete"
    
    print("✅ Hook events have correct attributes")

def test_hook_loading():
    """Test that hooks load correctly from new directory."""
    from cli_agent.core.hooks.hook_config import HookConfig
    
    config = HookConfig.load_from_multiple_sources()
    
    # Should have hooks from ~/.config/agent/hooks/
    assert len(config.hooks) > 0
    
    # Should have the hook types we expect
    from cli_agent.core.hooks.hook_config import HookType
    expected_types = {HookType.PRE_TOOL_USE, HookType.POST_TOOL_USE, HookType.NOTIFICATION, HookType.STOP}
    actual_types = set(config.hooks.keys())
    
    assert expected_types.issubset(actual_types), f"Missing hook types: {expected_types - actual_types}"
    
    print("✅ Hooks load correctly from new directory structure")

def test_notification_hook_specificity():
    """Test that notification hook now has specific matcher."""
    from cli_agent.core.hooks.hook_config import HookConfig
    from pathlib import Path
    
    # Load hooks and find notification hooks
    config = HookConfig.load_from_multiple_sources()
    
    from cli_agent.core.hooks.hook_config import HookType
    notification_matchers = config.hooks.get(HookType.NOTIFICATION, [])
    
    # Find the desktop notification hook
    desktop_hook = None
    for matcher in notification_matchers:
        for hook in matcher.hooks:
            if "display notification" in hook.command or "notify-send" in hook.command:
                desktop_hook = (matcher, hook)
                break
    
    assert desktop_hook is not None, "Desktop notification hook not found"
    matcher, hook = desktop_hook
    
    # Should no longer use "*" matcher - should be more specific
    assert matcher.pattern != "*", f"Notification hook still uses '*' matcher: {matcher.pattern}"
    
    print("✅ Notification hook uses specific matcher (not '*')")

if __name__ == "__main__":
    test_hook_events()
    test_hook_loading() 
    test_notification_hook_specificity()
    print("\n🎉 All hook fixes verified!")