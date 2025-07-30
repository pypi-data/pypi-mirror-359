"""
WarpTest1 - Comprehensive Claude Streaming Test Suite

Tests multiple approaches to get real-time Claude output streaming.
Based on Claude Code CLI documentation and various subprocess techniques.
"""

import subprocess
import sys
import time
import os
import pty
import select
import threading
import queue
from datetime import datetime
from pathlib import Path


def main():
    """Run comprehensive Claude streaming test suite"""
    
    print("🧪 WarpTest1: Comprehensive Claude Streaming Test Suite")
    print("=" * 60)
    print("Testing multiple approaches for real-time Claude output capture...")
    print()
    
    # Short prompt for faster testing (1-3 instead of 1-10)
    prompt = """Count from 1 to 3, explaining each number briefly. 
Be descriptive but concise."""
    
    print(f"📝 Prompt: {prompt}")
    print()
    
    # Run all streaming tests
    test_results = {}
    
    # Test 1: Standard subprocess (baseline - we know this buffers)
    print("🔬 TEST 1: Standard subprocess (baseline)")
    test_results['standard'] = test_standard_subprocess(prompt)
    print()
    
    # Test 2: Unbuffered with stdbuf
    print("🔬 TEST 2: Unbuffered with stdbuf")
    test_results['stdbuf'] = test_stdbuf_approach(prompt)
    print()
    
    # Test 3: PTY (pseudo-terminal) approach
    print("🔬 TEST 3: PTY (pseudo-terminal) approach") 
    test_results['pty'] = test_pty_approach(prompt)
    print()
    
    # Test 4: Interactive mode with input file
    print("🔬 TEST 4: Interactive mode with input file")
    test_results['interactive'] = test_interactive_approach(prompt)
    print()
    
    # Test 5: Line-buffered approach
    print("🔬 TEST 5: Line-buffered approach")
    test_results['line_buffered'] = test_line_buffered_approach(prompt)
    print()
    
    # Test 6: OpenTelemetry monitoring (if available)
    print("🔬 TEST 6: OpenTelemetry monitoring test")
    test_results['otel'] = test_otel_monitoring(prompt)
    print()
    
    # Test 7: Process monitoring approach
    print("🔬 TEST 7: Process activity monitoring")
    test_results['process_monitor'] = test_process_monitoring(prompt)
    print()
    
    # Summary of results
    print_test_summary(test_results)
    
    return 0


def test_standard_subprocess(prompt):
    """Test 1: Standard subprocess approach (baseline)"""
    try:
        start_time = time.time()
        cmd = f'claude --print --dangerously-skip-permissions "{prompt}"'
        
        print(f"🚀 Command: {cmd}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,
            shell=True
        )
        
        chars_received = 0
        first_char_time = None
        
        while True:
            char = process.stdout.read(1)
            if not char:
                if process.poll() is not None:
                    break
                time.sleep(0.01)
                continue
            
            if first_char_time is None:
                first_char_time = time.time()
                print(f"⏰ First character after: {first_char_time - start_time:.2f}s")
            
            chars_received += 1
        
        # Get remaining output
        remaining, stderr = process.communicate()
        total_chars = chars_received + len(remaining)
        end_time = time.time()
        
        result = {
            'success': True,
            'total_time': end_time - start_time,
            'first_char_delay': first_char_time - start_time if first_char_time else None,
            'total_chars': total_chars,
            'streaming': first_char_time is not None and (first_char_time - start_time) < 2.0,
            'error': None
        }
        
        print(f"✅ Standard: {result['total_time']:.2f}s, {result['total_chars']} chars")
        print(f"   First char delay: {result['first_char_delay']:.2f}s" if result['first_char_delay'] else "   No streaming detected")
        
        return result
        
    except Exception as e:
        print(f"❌ Standard subprocess failed: {e}")
        return {'success': False, 'error': str(e)}


def test_stdbuf_approach(prompt):
    """Test 2: Force unbuffered output with stdbuf"""
    try:
        start_time = time.time()
        # Use stdbuf to force line buffering
        cmd = f'stdbuf -oL claude --print --dangerously-skip-permissions "{prompt}"'
        
        print(f"🚀 Command: {cmd}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            shell=True
        )
        
        chars_received = 0
        first_char_time = None
        
        while True:
            char = process.stdout.read(1)
            if not char:
                if process.poll() is not None:
                    break
                time.sleep(0.01)
                continue
            
            if first_char_time is None:
                first_char_time = time.time()
                print(f"⏰ First character after: {first_char_time - start_time:.2f}s")
            
            chars_received += 1
        
        remaining, stderr = process.communicate()
        total_chars = chars_received + len(remaining)
        end_time = time.time()
        
        result = {
            'success': True,
            'total_time': end_time - start_time,
            'first_char_delay': first_char_time - start_time if first_char_time else None,
            'total_chars': total_chars,
            'streaming': first_char_time is not None and (first_char_time - start_time) < 2.0,
            'error': None
        }
        
        print(f"✅ Stdbuf: {result['total_time']:.2f}s, {result['total_chars']} chars")
        print(f"   First char delay: {result['first_char_delay']:.2f}s" if result['first_char_delay'] else "   No streaming detected")
        
        return result
        
    except Exception as e:
        print(f"❌ Stdbuf approach failed: {e}")
        return {'success': False, 'error': str(e)}


def test_pty_approach(prompt):
    """Test 3: Use pseudo-terminal to force interactive mode"""
    try:
        start_time = time.time()
        
        print(f"🚀 Using PTY approach")
        
        # Create a pseudo-terminal
        master, slave = pty.openpty()
        
        cmd = f'claude --print --dangerously-skip-permissions "{prompt}"'
        
        process = subprocess.Popen(
            cmd,
            stdin=slave,
            stdout=slave,
            stderr=slave,
            text=True,
            shell=True
        )
        
        os.close(slave)  # Close slave in parent
        
        chars_received = 0
        first_char_time = None
        output_buffer = ""
        
        while True:
            # Use select to check if data is available
            ready, _, _ = select.select([master], [], [], 0.1)
            
            if ready:
                try:
                    data = os.read(master, 1024).decode('utf-8')
                    if data:
                        if first_char_time is None:
                            first_char_time = time.time()
                            print(f"⏰ First data after: {first_char_time - start_time:.2f}s")
                        
                        chars_received += len(data)
                        output_buffer += data
                except OSError:
                    break
            
            if process.poll() is not None:
                # Process finished, try to read any remaining data
                try:
                    remaining = os.read(master, 4096).decode('utf-8')
                    chars_received += len(remaining)
                    output_buffer += remaining
                except OSError:
                    pass
                break
        
        os.close(master)
        end_time = time.time()
        
        result = {
            'success': True,
            'total_time': end_time - start_time,
            'first_char_delay': first_char_time - start_time if first_char_time else None,
            'total_chars': chars_received,
            'streaming': first_char_time is not None and (first_char_time - start_time) < 2.0,
            'error': None
        }
        
        print(f"✅ PTY: {result['total_time']:.2f}s, {result['total_chars']} chars")
        print(f"   First char delay: {result['first_char_delay']:.2f}s" if result['first_char_delay'] else "   No streaming detected")
        
        return result
        
    except Exception as e:
        print(f"❌ PTY approach failed: {e}")
        return {'success': False, 'error': str(e)}


def test_interactive_approach(prompt):
    """Test 4: Interactive mode with conversation file"""
    try:
        start_time = time.time()
        
        # Create a temporary conversation ID
        conv_file = Path.cwd() / ".warptest_conversation_id"
        
        print(f"🚀 Using interactive mode")
        
        # First, try to start a conversation
        cmd = f'claude "{prompt}"'
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        
        # Send the prompt and immediately send EOF to finish
        stdout, stderr = process.communicate(input="\n")
        
        end_time = time.time()
        
        result = {
            'success': True,
            'total_time': end_time - start_time,
            'first_char_delay': None,  # Can't measure for this approach
            'total_chars': len(stdout),
            'streaming': False,  # This approach doesn't support streaming
            'error': None
        }
        
        print(f"✅ Interactive: {result['total_time']:.2f}s, {result['total_chars']} chars")
        print(f"   Note: Interactive mode doesn't support real-time streaming")
        
        return result
        
    except Exception as e:
        print(f"❌ Interactive approach failed: {e}")
        return {'success': False, 'error': str(e)}


def test_line_buffered_approach(prompt):
    """Test 5: Line-buffered reading"""
    try:
        start_time = time.time()
        cmd = f'claude --print --dangerously-skip-permissions "{prompt}"'
        
        print(f"🚀 Command: {cmd} (line-buffered)")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            shell=True
        )
        
        lines_received = 0
        first_line_time = None
        total_chars = 0
        
        for line in iter(process.stdout.readline, ''):
            if first_line_time is None:
                first_line_time = time.time()
                print(f"⏰ First line after: {first_line_time - start_time:.2f}s")
            
            lines_received += 1
            total_chars += len(line)
        
        process.wait()
        end_time = time.time()
        
        result = {
            'success': True,
            'total_time': end_time - start_time,
            'first_char_delay': first_line_time - start_time if first_line_time else None,
            'total_chars': total_chars,
            'lines': lines_received,
            'streaming': first_line_time is not None and (first_line_time - start_time) < 2.0,
            'error': None
        }
        
        print(f"✅ Line-buffered: {result['total_time']:.2f}s, {result['total_chars']} chars, {result['lines']} lines")
        print(f"   First line delay: {result['first_char_delay']:.2f}s" if result['first_char_delay'] else "   No streaming detected")
        
        return result
        
    except Exception as e:
        print(f"❌ Line-buffered approach failed: {e}")
        return {'success': False, 'error': str(e)}


def test_otel_monitoring(prompt):
    """Test 6: OpenTelemetry monitoring if available"""
    try:
        start_time = time.time()
        
        print(f"🚀 Testing OTEL monitoring")
        
        # Set up OTEL environment
        env = os.environ.copy()
        env.update({
            'CLAUDE_CODE_ENABLE_TELEMETRY': '1',
            'OTEL_LOGS_EXPORTER': 'console',
            'OTEL_LOGS_EXPORT_INTERVAL': '1000'
        })
        
        cmd = f'claude --print --dangerously-skip-permissions "{prompt}"'
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            shell=True
        )
        
        stdout, stderr = process.communicate()
        end_time = time.time()
        
        # Check if OTEL events were captured
        otel_events = []
        if stderr:
            # Look for OTEL-like output in stderr
            for line in stderr.split('\n'):
                if any(keyword in line.lower() for keyword in ['otel', 'telemetry', 'claude_code.']):
                    otel_events.append(line.strip())
        
        result = {
            'success': True,
            'total_time': end_time - start_time,
            'total_chars': len(stdout),
            'otel_events': len(otel_events),
            'has_otel': len(otel_events) > 0,
            'streaming': False,  # OTEL doesn't provide streaming
            'error': None
        }
        
        print(f"✅ OTEL: {result['total_time']:.2f}s, {result['total_chars']} chars")
        print(f"   OTEL events detected: {result['otel_events']}")
        
        return result
        
    except Exception as e:
        print(f"❌ OTEL monitoring failed: {e}")
        return {'success': False, 'error': str(e)}


def test_process_monitoring(prompt):
    """Test 7: Process activity monitoring"""
    try:
        start_time = time.time()
        
        print(f"🚀 Testing process activity monitoring")
        
        cmd = f'claude --print --dangerously-skip-permissions "{prompt}"'
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        
        # Monitor process activity
        activity_checks = []
        while process.poll() is None:
            current_time = time.time()
            activity_checks.append({
                'time': current_time - start_time,
                'status': 'running'
            })
            time.sleep(0.5)  # Check every 500ms
        
        stdout, stderr = process.communicate()
        end_time = time.time()
        
        result = {
            'success': True,
            'total_time': end_time - start_time,
            'total_chars': len(stdout),
            'activity_checks': len(activity_checks),
            'process_active': len(activity_checks) > 0,
            'streaming': False,  # Process monitoring doesn't provide content streaming
            'error': None
        }
        
        print(f"✅ Process Monitor: {result['total_time']:.2f}s, {result['total_chars']} chars")
        print(f"   Activity checks: {result['activity_checks']} (every 0.5s)")
        
        return result
        
    except Exception as e:
        print(f"❌ Process monitoring failed: {e}")
        return {'success': False, 'error': str(e)}


def print_test_summary(results):
    """Print comprehensive test results summary"""
    print()
    print("=" * 60)
    print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
    print("=" * 60)
    
    successful_tests = [name for name, result in results.items() if result.get('success', False)]
    failed_tests = [name for name, result in results.items() if not result.get('success', False)]
    
    print(f"✅ Successful tests: {len(successful_tests)}/{len(results)}")
    print(f"❌ Failed tests: {len(failed_tests)}")
    print()
    
    # Detailed results
    for test_name, result in results.items():
        if result.get('success', False):
            streaming_status = "🟢 STREAMING" if result.get('streaming', False) else "🔴 BUFFERED"
            delay = f"{result.get('first_char_delay', 0):.2f}s" if result.get('first_char_delay') else "N/A"
            
            print(f"🔬 {test_name.upper():<15} | {streaming_status} | Time: {result.get('total_time', 0):.2f}s | Delay: {delay}")
        else:
            print(f"🔬 {test_name.upper():<15} | ❌ FAILED | Error: {result.get('error', 'Unknown')}")
    
    print()
    print("🎯 CONCLUSIONS:")
    
    streaming_tests = [name for name, result in results.items() 
                      if result.get('success', False) and result.get('streaming', False)]
    
    if streaming_tests:
        print(f"✅ Real-time streaming works with: {', '.join(streaming_tests)}")
    else:
        print("❌ No real-time streaming detected in any method")
        print("💡 Claude Code CLI appears to buffer all output until completion")
    
    fastest_test = min(
        [(name, result) for name, result in results.items() if result.get('success', False)],
        key=lambda x: x[1].get('total_time', float('inf')),
        default=(None, None)
    )
    
    if fastest_test[0]:
        print(f"🏃 Fastest method: {fastest_test[0]} ({fastest_test[1]['total_time']:.2f}s)")
    
    print()
    print("💡 RECOMMENDATIONS FOR WARPCODE:")
    print("   1. Use process monitoring instead of output streaming")
    print("   2. Monitor file changes and conversation state")
    print("   3. Show 'Claude is thinking...' indicators during execution")
    print("   4. Update scoreboards based on process activity, not output parsing")


if __name__ == "__main__":
    sys.exit(main())


def test_conversation_continuity():
    """Test if we can use conversation continuity"""
    
    try:
        # Try to find conversation ID
        from pathlib import Path
        conversation_file = Path.cwd() / ".warpcode_conversation_id"
        
        if conversation_file.exists():
            with open(conversation_file, 'r') as f:
                conversation_id = f.read().strip()
            
            if conversation_id:
                print(f"📞 Found conversation ID: {conversation_id[:12]}...")
                
                # Test continuing conversation
                cmd = ['claude', '-c', conversation_id, '--print', '--dangerously-skip-permissions', 
                       "What was the last number I asked you to count to?"]
                
                print("🧪 Testing conversation memory...")
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    print(f"✅ Conversation continuity works!")
                    print(f"🗣️  Claude remembers: {result.stdout[:100]}...")
                else:
                    print(f"❌ Conversation continuity failed: {result.stderr}")
            else:
                print("❌ Empty conversation ID file")
        else:
            print("ℹ️  No conversation ID file found")
            
    except Exception as e:
        print(f"⚠️  Conversation test error: {e}")


def test_line_streaming():
    """Alternative method: Line-by-line streaming"""
    
    print("🧪 Alternative Test: Line-by-line streaming")
    
    prompt = "List 5 programming languages with brief descriptions"
    cmd = ['claude', '--print', '--dangerously-skip-permissions', prompt]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        
        line_count = 0
        for line in iter(process.stdout.readline, ''):
            print(f"[Line {line_count}] {line}", end='')
            line_count += 1
            
        process.wait()
        
        print(f"\n✅ Line streaming test complete - {line_count} lines")
        
    except Exception as e:
        print(f"❌ Line streaming error: {e}")


if __name__ == "__main__":
    sys.exit(main())