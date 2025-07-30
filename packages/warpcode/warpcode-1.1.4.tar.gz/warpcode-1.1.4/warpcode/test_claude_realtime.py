"""
WarpTest2 - Claude Code Real-Time Monitoring via Log Files and Telemetry

Based on research findings:
1. Claude Code produces JSONL transcript files 
2. Claude Code supports OpenTelemetry streaming logs
3. Claude Code has --output-format stream-json for headless mode
4. There are session log files that update in real-time
"""

import subprocess
import sys
import time
import os
import json
import threading
import queue
from datetime import datetime
from pathlib import Path
import select
import tempfile


def main():
    """Test real-time Claude monitoring via multiple approaches"""
    
    print("🔍 WarpTest2: Claude Code Real-Time Monitoring Test Suite")
    print("=" * 65)
    print("Testing real-time monitoring via log files and telemetry...")
    print()
    
    # Short prompt for faster testing
    prompt = """Count from 1 to 3, explaining each number briefly. 
Be descriptive but concise."""
    
    print(f"📝 Prompt: {prompt}")
    print()
    
    # Run all real-time monitoring tests
    test_results = {}
    
    # Test 1: JSON transcript file monitoring
    print("🔬 TEST 1: JSONL transcript file monitoring")
    test_results['jsonl_logs'] = test_jsonl_transcript_monitoring(prompt)
    print()
    
    # Test 2: OpenTelemetry real-time events
    print("🔬 TEST 2: OpenTelemetry real-time event streaming") 
    test_results['otel_events'] = test_otel_event_streaming(prompt)
    print()
    
    # Test 3: Stream-JSON output format
    print("🔬 TEST 3: Stream-JSON output format")
    test_results['stream_json'] = test_stream_json_output(prompt)
    print()
    
    # Test 4: Session log file monitoring
    print("🔬 TEST 4: Session log file monitoring")
    test_results['session_logs'] = test_session_log_monitoring(prompt)
    print()
    
    # Test 5: Config directory log monitoring
    print("🔬 TEST 5: Config directory log file monitoring")
    test_results['config_logs'] = test_config_directory_logs(prompt)
    print()
    
    # Test 6: Verbose output monitoring
    print("🔬 TEST 6: Verbose output with file monitoring")
    test_results['verbose_logs'] = test_verbose_output_monitoring(prompt)
    print()
    
    # Summary of results
    print_realtime_test_summary(test_results)
    
    return 0


def test_jsonl_transcript_monitoring(prompt):
    """Test 1: Monitor JSONL transcript files in real-time"""
    try:
        start_time = time.time()
        
        # Look for potential transcript file locations
        possible_paths = [
            Path.home() / ".claude" / "transcripts",
            Path.home() / ".config" / "claude" / "transcripts", 
            Path.home() / "Library" / "Application Support" / "Claude" / "transcripts",
            Path.cwd() / ".claude" / "transcripts"
        ]
        
        print(f"🚀 Searching for Claude transcript directories...")
        transcript_dir = None
        for path in possible_paths:
            if path.exists():
                transcript_dir = path
                print(f"✅ Found transcript directory: {path}")
                break
        
        if not transcript_dir:
            print(f"ℹ️  Creating transcript monitoring in current directory")
            transcript_dir = Path.cwd() / ".claude_transcripts"
            transcript_dir.mkdir(exist_ok=True)
        
        # Start monitoring for new files
        existing_files = set(transcript_dir.glob("*.jsonl")) if transcript_dir.exists() else set()
        
        # Run Claude command
        cmd = ['claude', '--print', '--dangerously-skip-permissions', prompt]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Monitor for new transcript files
        events_detected = 0
        first_event_time = None
        
        while process.poll() is None:
            if transcript_dir.exists():
                current_files = set(transcript_dir.glob("*.jsonl"))
                new_files = current_files - existing_files
                
                for new_file in new_files:
                    if first_event_time is None:
                        first_event_time = time.time()
                        print(f"⏰ First transcript file after: {first_event_time - start_time:.2f}s")
                    
                    # Try to read new content
                    try:
                        with open(new_file, 'r') as f:
                            lines = f.readlines()
                            events_detected += len(lines)
                            if lines:
                                print(f"📝 New transcript events: {len(lines)}")
                    except (FileNotFoundError, PermissionError):
                        pass
                
                existing_files = current_files
            
            time.sleep(0.1)  # Check every 100ms
        
        # Get final output
        stdout, stderr = process.communicate()
        end_time = time.time()
        
        result = {
            'success': True,
            'total_time': end_time - start_time,
            'first_event_delay': first_event_time - start_time if first_event_time else None,
            'events_detected': events_detected,
            'real_time_updates': first_event_time is not None,
            'method': 'jsonl_transcript_monitoring'
        }
        
        print(f"✅ JSONL Transcripts: {result['total_time']:.2f}s, {result['events_detected']} events")
        if result['first_event_delay']:
            print(f"   First event delay: {result['first_event_delay']:.2f}s")
        else:
            print(f"   No real-time events detected")
        
        return result
        
    except Exception as e:
        print(f"❌ JSONL transcript monitoring failed: {e}")
        return {'success': False, 'error': str(e), 'method': 'jsonl_transcript_monitoring'}


def test_otel_event_streaming(prompt):
    """Test 2: Monitor OpenTelemetry events in real-time"""
    try:
        start_time = time.time()
        
        print(f"🚀 Setting up OpenTelemetry console monitoring...")
        
        # Set up OTEL environment for console output
        env = os.environ.copy()
        env.update({
            'CLAUDE_CODE_ENABLE_TELEMETRY': '1',
            'OTEL_LOGS_EXPORTER': 'console',
            'OTEL_LOGS_EXPORT_INTERVAL': '1000',  # 1 second for fast testing
            'OTEL_LOG_USER_PROMPTS': '1'  # Enable prompt content logging
        })
        
        cmd = ['claude', '--print', '--dangerously-skip-permissions', prompt]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        events_detected = 0
        first_event_time = None
        otel_events = []
        
        # Monitor stderr for OTEL console output
        while process.poll() is None:
            # Use select to check for available data
            ready_read, _, _ = select.select([process.stderr], [], [], 0.1)
            
            if ready_read:
                line = process.stderr.readline()
                if line:
                    # Look for OTEL event patterns
                    if any(keyword in line.lower() for keyword in [
                        'claude_code.', 'user_prompt', 'tool_result', 'api_request', 'otel'
                    ]):
                        if first_event_time is None:
                            first_event_time = time.time()
                            print(f"⏰ First OTEL event after: {first_event_time - start_time:.2f}s")
                        
                        events_detected += 1
                        otel_events.append(line.strip())
                        print(f"📊 OTEL Event {events_detected}: {line.strip()[:60]}...")
        
        # Get remaining output
        stdout, stderr = process.communicate()
        
        # Parse any remaining OTEL events from final stderr
        for line in stderr.split('\n'):
            if any(keyword in line.lower() for keyword in [
                'claude_code.', 'user_prompt', 'tool_result', 'api_request'
            ]):
                events_detected += 1
                otel_events.append(line.strip())
        
        end_time = time.time()
        
        result = {
            'success': True,
            'total_time': end_time - start_time,
            'first_event_delay': first_event_time - start_time if first_event_time else None,
            'events_detected': events_detected,
            'real_time_updates': first_event_time is not None,
            'sample_events': otel_events[:3],  # First 3 events as examples
            'method': 'otel_event_streaming'
        }
        
        print(f"✅ OTEL Events: {result['total_time']:.2f}s, {result['events_detected']} events")
        if result['first_event_delay']:
            print(f"   First event delay: {result['first_event_delay']:.2f}s")
        else:
            print(f"   No OTEL events detected")
        
        return result
        
    except Exception as e:
        print(f"❌ OTEL event streaming failed: {e}")
        return {'success': False, 'error': str(e), 'method': 'otel_event_streaming'}


def test_stream_json_output(prompt):
    """Test 3: Use Claude's stream-json output format"""
    try:
        start_time = time.time()
        
        print(f"🚀 Testing --output-format stream-json...")
        
        cmd = ['claude', '--output-format', 'stream-json', '--print', '--dangerously-skip-permissions', prompt]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0  # Unbuffered
        )
        
        json_chunks = 0
        first_chunk_time = None
        json_events = []
        
        while True:
            char = process.stdout.read(1)
            if not char:
                if process.poll() is not None:
                    break
                time.sleep(0.01)
                continue
            
            if char == '{' or char == '[':  # Start of JSON
                if first_chunk_time is None:
                    first_chunk_time = time.time()
                    print(f"⏰ First JSON chunk after: {first_chunk_time - start_time:.2f}s")
                
                # Try to read a complete JSON object
                json_buffer = char
                brace_count = 1 if char == '{' else 0
                bracket_count = 1 if char == '[' else 0
                
                while brace_count > 0 or bracket_count > 0:
                    next_char = process.stdout.read(1)
                    if not next_char:
                        break
                    json_buffer += next_char
                    
                    if next_char == '{':
                        brace_count += 1
                    elif next_char == '}':
                        brace_count -= 1
                    elif next_char == '[':
                        bracket_count += 1
                    elif next_char == ']':
                        bracket_count -= 1
                
                if json_buffer:
                    json_chunks += 1
                    json_events.append(json_buffer[:50] + "..." if len(json_buffer) > 50 else json_buffer)
                    print(f"📦 JSON Chunk {json_chunks}: {json_buffer[:40]}...")
        
        # Get remaining output
        remaining, stderr = process.communicate()
        end_time = time.time()
        
        result = {
            'success': True,
            'total_time': end_time - start_time,
            'first_chunk_delay': first_chunk_time - start_time if first_chunk_time else None,
            'json_chunks': json_chunks,
            'real_time_updates': first_chunk_time is not None,
            'sample_chunks': json_events[:3],
            'method': 'stream_json_output'
        }
        
        print(f"✅ Stream JSON: {result['total_time']:.2f}s, {result['json_chunks']} chunks")
        if result['first_chunk_delay']:
            print(f"   First chunk delay: {result['first_chunk_delay']:.2f}s")
        else:
            print(f"   No JSON streaming detected")
        
        return result
        
    except Exception as e:
        print(f"❌ Stream JSON test failed: {e}")
        return {'success': False, 'error': str(e), 'method': 'stream_json_output'}


def test_session_log_monitoring(prompt):
    """Test 4: Monitor Claude session log files"""
    try:
        start_time = time.time()
        
        print(f"🚀 Monitoring Claude session logs...")
        
        # Common log locations for Claude
        log_paths = [
            Path.home() / ".claude" / "logs",
            Path.home() / ".config" / "claude" / "logs",
            Path.home() / "Library" / "Logs" / "Claude",
            Path.home() / "Library" / "Application Support" / "Claude" / "logs",
        ]
        
        # Find existing log files before starting
        existing_logs = set()
        active_log_dir = None
        
        for log_path in log_paths:
            if log_path.exists():
                existing_logs.update(log_path.glob("*.log"))
                existing_logs.update(log_path.glob("*.jsonl"))
                if existing_logs:
                    active_log_dir = log_path
                    print(f"✅ Found active log directory: {log_path}")
                    break
        
        # Start Claude command
        cmd = ['claude', '--print', '--dangerously-skip-permissions', prompt]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        log_updates = 0
        first_update_time = None
        
        # Monitor for log file changes
        while process.poll() is None:
            if active_log_dir and active_log_dir.exists():
                current_logs = set()
                current_logs.update(active_log_dir.glob("*.log"))
                current_logs.update(active_log_dir.glob("*.jsonl"))
                
                new_logs = current_logs - existing_logs
                for new_log in new_logs:
                    if first_update_time is None:
                        first_update_time = time.time()
                        print(f"⏰ First log update after: {first_update_time - start_time:.2f}s")
                    
                    log_updates += 1
                    print(f"📋 New log file: {new_log.name}")
                
                # Check for size changes in existing logs
                for log_file in existing_logs:
                    if log_file.exists():
                        try:
                            # Check if file was modified recently
                            mod_time = log_file.stat().st_mtime
                            if mod_time > start_time:
                                if first_update_time is None:
                                    first_update_time = time.time()
                                    print(f"⏰ First log update after: {first_update_time - start_time:.2f}s")
                                log_updates += 1
                        except (OSError, FileNotFoundError):
                            pass
                
                existing_logs = current_logs
            
            time.sleep(0.2)  # Check every 200ms
        
        # Get final output
        stdout, stderr = process.communicate()
        end_time = time.time()
        
        result = {
            'success': True,
            'total_time': end_time - start_time,
            'first_update_delay': first_update_time - start_time if first_update_time else None,
            'log_updates': log_updates,
            'real_time_updates': first_update_time is not None,
            'log_directory': str(active_log_dir) if active_log_dir else None,
            'method': 'session_log_monitoring'
        }
        
        print(f"✅ Session Logs: {result['total_time']:.2f}s, {result['log_updates']} updates")
        if result['first_update_delay']:
            print(f"   First update delay: {result['first_update_delay']:.2f}s")
        else:
            print(f"   No session log updates detected")
        
        return result
        
    except Exception as e:
        print(f"❌ Session log monitoring failed: {e}")
        return {'success': False, 'error': str(e), 'method': 'session_log_monitoring'}


def test_config_directory_logs(prompt):
    """Test 5: Monitor Claude config directory for log files"""
    try:
        start_time = time.time()
        
        print(f"🚀 Monitoring Claude config directory logs...")
        
        # Get Claude config directory
        config_dir = os.environ.get('CLAUDE_CONFIG_DIR')
        if not config_dir:
            # Try common config locations
            possible_configs = [
                Path.home() / ".claude",
                Path.home() / ".config" / "claude",
                Path.home() / "Library" / "Application Support" / "Claude"
            ]
            for path in possible_configs:
                if path.exists():
                    config_dir = str(path)
                    break
        
        if config_dir:
            config_path = Path(config_dir)
            print(f"✅ Monitoring config directory: {config_path}")
        else:
            config_path = Path.home() / ".claude"
            config_path.mkdir(exist_ok=True)
            print(f"ℹ️  Created config directory: {config_path}")
        
        # Get baseline file state
        existing_files = set(config_path.rglob("*")) if config_path.exists() else set()
        existing_sizes = {f: f.stat().st_size for f in existing_files if f.is_file()}
        
        # Start Claude command
        cmd = ['claude', '--print', '--dangerously-skip-permissions', prompt]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        file_changes = 0
        first_change_time = None
        
        # Monitor for file changes
        while process.poll() is None:
            if config_path.exists():
                current_files = set(config_path.rglob("*"))
                new_files = current_files - existing_files
                
                # Check for new files
                for new_file in new_files:
                    if new_file.is_file() and first_change_time is None:
                        first_change_time = time.time()
                        print(f"⏰ First config change after: {first_change_time - start_time:.2f}s")
                        file_changes += 1
                        print(f"📁 New config file: {new_file.name}")
                
                # Check for size changes in existing files
                for file_path in existing_files:
                    if file_path.is_file() and file_path.exists():
                        try:
                            current_size = file_path.stat().st_size
                            original_size = existing_sizes.get(file_path, 0)
                            if current_size != original_size:
                                if first_change_time is None:
                                    first_change_time = time.time()
                                    print(f"⏰ First config change after: {first_change_time - start_time:.2f}s")
                                file_changes += 1
                                print(f"📝 Config file changed: {file_path.name} ({original_size} -> {current_size} bytes)")
                                existing_sizes[file_path] = current_size
                        except (OSError, FileNotFoundError):
                            pass
                
                existing_files = current_files
            
            time.sleep(0.1)  # Check every 100ms
        
        # Get final output
        stdout, stderr = process.communicate()
        end_time = time.time()
        
        result = {
            'success': True,
            'total_time': end_time - start_time,
            'first_change_delay': first_change_time - start_time if first_change_time else None,
            'file_changes': file_changes,
            'real_time_updates': first_change_time is not None,
            'config_directory': str(config_path),
            'method': 'config_directory_logs'
        }
        
        print(f"✅ Config Logs: {result['total_time']:.2f}s, {result['file_changes']} changes")
        if result['first_change_delay']:
            print(f"   First change delay: {result['first_change_delay']:.2f}s")
        else:
            print(f"   No config changes detected")
        
        return result
        
    except Exception as e:
        print(f"❌ Config directory monitoring failed: {e}")
        return {'success': False, 'error': str(e), 'method': 'config_directory_logs'}


def test_verbose_output_monitoring(prompt):
    """Test 6: Use verbose output with file monitoring"""
    try:
        start_time = time.time()
        
        print(f"🚀 Testing verbose output with file monitoring...")
        
        # Create temporary file for output redirection
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.log', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Run Claude with verbose output redirected to file
        cmd = ['claude', '--verbose', '--print', '--dangerously-skip-permissions', prompt]
        
        with open(temp_path, 'w') as log_file:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=log_file,  # Redirect verbose output to file
                text=True
            )
        
        verbose_updates = 0
        first_update_time = None
        last_size = 0
        
        # Monitor the log file for real-time updates
        while process.poll() is None:
            try:
                current_size = Path(temp_path).stat().st_size
                if current_size > last_size:
                    if first_update_time is None:
                        first_update_time = time.time()
                        print(f"⏰ First verbose update after: {first_update_time - start_time:.2f}s")
                    
                    verbose_updates += 1
                    new_bytes = current_size - last_size
                    print(f"📊 Verbose update {verbose_updates}: +{new_bytes} bytes")
                    
                    # Read new content
                    with open(temp_path, 'r') as f:
                        f.seek(last_size)
                        new_content = f.read(min(100, new_bytes))  # Read up to 100 chars
                        if new_content.strip():
                            print(f"   Content: {new_content.strip()[:50]}...")
                    
                    last_size = current_size
            except (OSError, FileNotFoundError):
                pass
            
            time.sleep(0.1)  # Check every 100ms
        
        # Get final output
        stdout, stderr = process.communicate()
        end_time = time.time()
        
        # Read final log content
        try:
            with open(temp_path, 'r') as f:
                log_content = f.read()
            final_size = len(log_content)
            
            # Clean up temp file
            os.unlink(temp_path)
        except (OSError, FileNotFoundError):
            final_size = 0
            log_content = ""
        
        result = {
            'success': True,
            'total_time': end_time - start_time,
            'first_update_delay': first_update_time - start_time if first_update_time else None,
            'verbose_updates': verbose_updates,
            'final_log_size': final_size,
            'real_time_updates': first_update_time is not None,
            'log_sample': log_content[:200] + "..." if len(log_content) > 200 else log_content,
            'method': 'verbose_output_monitoring'
        }
        
        print(f"✅ Verbose Output: {result['total_time']:.2f}s, {result['verbose_updates']} updates")
        print(f"   Final log size: {result['final_log_size']} bytes")
        if result['first_update_delay']:
            print(f"   First update delay: {result['first_update_delay']:.2f}s")
        else:
            print(f"   No verbose updates detected")
        
        return result
        
    except Exception as e:
        print(f"❌ Verbose output monitoring failed: {e}")
        return {'success': False, 'error': str(e), 'method': 'verbose_output_monitoring'}


def print_realtime_test_summary(results):
    """Print comprehensive test results summary"""
    print()
    print("=" * 65)
    print("📊 REAL-TIME MONITORING TEST RESULTS SUMMARY")
    print("=" * 65)
    
    successful_tests = [name for name, result in results.items() if result.get('success', False)]
    failed_tests = [name for name, result in results.items() if not result.get('success', False)]
    
    print(f"✅ Successful tests: {len(successful_tests)}/{len(results)}")
    print(f"❌ Failed tests: {len(failed_tests)}")
    print()
    
    # Detailed results
    print("📋 DETAILED RESULTS:")
    for test_name, result in results.items():
        if result.get('success', False):
            real_time_status = "🟢 REAL-TIME" if result.get('real_time_updates', False) else "🔴 NO UPDATES"
            delay = f"{result.get('first_event_delay', result.get('first_update_delay', result.get('first_chunk_delay', result.get('first_change_delay', 0)))):.2f}s" if result.get('real_time_updates') else "N/A"
            
            updates = result.get('events_detected', result.get('log_updates', result.get('json_chunks', result.get('file_changes', result.get('verbose_updates', 0)))))
            
            print(f"🔬 {test_name.upper():<20} | {real_time_status} | Time: {result.get('total_time', 0):.2f}s | Updates: {updates} | Delay: {delay}")
        else:
            print(f"🔬 {test_name.upper():<20} | ❌ FAILED | Error: {result.get('error', 'Unknown')}")
    
    print()
    print("🎯 CONCLUSIONS:")
    
    real_time_tests = [name for name, result in results.items() 
                      if result.get('success', False) and result.get('real_time_updates', False)]
    
    if real_time_tests:
        print(f"✅ Real-time monitoring works with: {', '.join(real_time_tests)}")
        
        # Find best method
        best_method = None
        best_delay = float('inf')
        
        for name, result in results.items():
            if result.get('success', False) and result.get('real_time_updates', False):
                delay = result.get('first_event_delay', result.get('first_update_delay', 
                        result.get('first_chunk_delay', result.get('first_change_delay', float('inf')))))
                if delay and delay < best_delay:
                    best_delay = delay
                    best_method = name
        
        if best_method:
            print(f"🏆 Best real-time method: {best_method} ({best_delay:.2f}s delay)")
    else:
        print("❌ No real-time monitoring detected in any method")
        print("💡 Claude Code CLI appears to buffer all output until completion")
    
    print()
    print("💡 RECOMMENDATIONS FOR WARPCODE:")
    if real_time_tests:
        print("   1. Use file monitoring approach for real-time updates")
        print("   2. Monitor OTEL events or log files for progress tracking")
        print("   3. Implement dashboard updates based on file changes")
        print("   4. Use stream-json format for structured progress data")
    else:
        print("   1. Use process monitoring instead of output streaming")
        print("   2. Monitor file changes and conversation state")
        print("   3. Show 'Claude is thinking...' indicators during execution")
        print("   4. Update scoreboards based on process activity, not output parsing")
        print("   5. Consider implementing session monitoring via Claude config directory")


if __name__ == "__main__":
    sys.exit(main())