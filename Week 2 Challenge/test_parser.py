#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script to verify parser functionality with sample transcripts"""
import sys
import logging
import io
from pathlib import Path
from src.parser import TranscriptParser
from src.action_detector import ActionDetector
from src.summary_generator import SummaryGenerator
from src.exceptions import (
    MeetingExtractorError,
    FileNotFoundError,
    EmptyTranscriptError,
    MalformedTranscriptError
)

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Setup logging
logging.basicConfig(level=logging.WARNING)


def test_transcript(file_path: str, expected_format: str):
    """Test parsing a single transcript file"""
    print(f"\n{'='*70}")
    print(f"Testing: {file_path}")
    print(f"Expected format: {expected_format}")
    print('='*70)
    
    try:
        # Parse transcript
        parser = TranscriptParser()
        messages = parser.parse_file(file_path)
        
        print(f"✅ Parsing successful!")
        print(f"   Messages found: {len(messages)}")
        
        # Get statistics
        stats = parser.get_format_stats(messages)
        print(f"\n📊 Format Statistics:")
        print(f"   Total messages: {stats['total_messages']}")
        print(f"   With timestamps: {stats['with_timestamps']}")
        print(f"   Without timestamps: {stats['without_timestamps']}")
        print(f"   Unique speakers: {stats['unique_speakers']}")
        print(f"   Unknown speakers: {stats['unknown_speakers']}")
        
        # Show speakers
        speakers = parser.get_speakers(messages)
        print(f"\n👥 Speakers detected: {', '.join(speakers)}")
        
        # Show sample messages
        print(f"\n📝 Sample messages:")
        for i, msg in enumerate(messages[:3], 1):
            timestamp = f"[{msg['timestamp']}] " if msg['timestamp'] else ""
            text_preview = msg['text'][:60] + "..." if len(msg['text']) > 60 else msg['text']
            print(f"   {i}. {timestamp}{msg['speaker']}: {text_preview}")
        
        # Extract action items
        print(f"\n🎯 Extracting action items...")
        detector = ActionDetector()
        action_items = detector.extract_action_items(messages)
        
        print(f"   Action items found: {len(action_items)}")
        
        if action_items:
            # Show action item statistics
            item_stats = detector.get_statistics(action_items)
            print(f"\n📈 Action Item Statistics:")
            print(f"   Total: {item_stats['total']}")
            print(f"   High priority: {item_stats['by_priority']['high']}")
            print(f"   Medium priority: {item_stats['by_priority']['medium']}")
            print(f"   Low priority: {item_stats['by_priority']['low']}")
            print(f"   With deadlines: {item_stats['with_deadline']}")
            print(f"   Without deadlines: {item_stats['without_deadline']}")
            
            print(f"\n   By assignee:")
            for assignee, count in sorted(item_stats['by_assignee'].items()):
                print(f"      {assignee}: {count}")
            
            # Show sample action items
            print(f"\n✅ Sample action items:")
            for i, item in enumerate(action_items[:5], 1):
                priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(item.priority, '⚪')
                assignee = f"@{item.assignee}" if item.assignee else "Unassigned"
                deadline = f" (Due: {item.deadline})" if item.deadline else ""
                task_preview = item.task[:70] + "..." if len(item.task) > 70 else item.task
                print(f"   {i}. {priority_emoji} {task_preview}")
                print(f"      Assignee: {assignee}{deadline}")
            
            # Generate summary
            print(f"\n📝 Generating summary...")
            generator = SummaryGenerator()
            summary = generator.generate_compact_summary(action_items)
            print(f"   {summary}")
        
        return True
        
    except MeetingExtractorError as e:
        print(f"❌ Error: {e.message}")
        if e.suggestion:
            print(f"💡 {e.suggestion}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run tests on all sample transcripts"""
    print("\n" + "="*70)
    print("MEETING ACTION ITEMS EXTRACTOR - PARSER TEST SUITE")
    print("="*70)
    
    test_cases = [
        ("sample_transcripts/zoom_meeting.txt", "Zoom format with timestamps"),
        ("sample_transcripts/google_meet.txt", "Google Meet format"),
        ("sample_transcripts/plain_meeting.txt", "Plain text format"),
    ]
    
    results = []
    
    for file_path, expected_format in test_cases:
        if not Path(file_path).exists():
            print(f"\n⚠️  Warning: {file_path} not found, skipping...")
            results.append(False)
            continue
        
        success = test_transcript(file_path, expected_format)
        results.append(success)
    
    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print('='*70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1


def test_error_handling():
    """Test error handling with invalid inputs"""
    print(f"\n{'='*70}")
    print("Testing Error Handling")
    print('='*70)
    
    parser = TranscriptParser()
    
    # Test empty content
    print("\n1. Testing empty content...")
    try:
        parser.parse("")
        print("   ❌ Should have raised EmptyTranscriptError")
    except EmptyTranscriptError as e:
        print(f"   ✅ Correctly raised error: {e.message}")
    
    # Test file not found
    print("\n2. Testing non-existent file...")
    try:
        parser.parse_file("nonexistent_file.txt")
        print("   ❌ Should have raised FileNotFoundError")
    except FileNotFoundError as e:
        print(f"   ✅ Correctly raised error: {e.message}")
    
    # Test invalid content
    print("\n3. Testing content with no valid messages...")
    try:
        parser.parse("This is just random text without any structure")
        print("   ❌ Should have raised MalformedTranscriptError")
    except MalformedTranscriptError as e:
        print(f"   ✅ Correctly raised error: {e.message}")
    
    print("\n✅ Error handling tests completed")


if __name__ == '__main__':
    # Run main tests
    exit_code = run_all_tests()
    
    # Run error handling tests
    test_error_handling()
    
    print("\n" + "="*70)
    print("Testing complete!")
    print("="*70 + "\n")
    
    sys.exit(exit_code)
