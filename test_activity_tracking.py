#!/usr/bin/env python3
"""
Test file for activity tracking demonstration
This file will trigger the monitoring system to capture file changes.
"""

def test_function():
    """A simple test function to demonstrate activity tracking"""
    print("This file was created to test the activity monitoring system")
    print("Adding this line to trigger file modification event")
    return True

def additional_function():
    """Added to demonstrate file changes are tracked"""
    return "Activity tracking works!"

if __name__ == "__main__":
    test_function()