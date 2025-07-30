"""
WarpTest1 - Direct Claude Streaming Test

Simple test command to verify real-time Claude output streaming
without any scoreboards or complex monitoring.
"""

import subprocess
import sys
import time
from datetime import datetime


def main():
    """Test direct Claude streaming output in real-time"""
    
    print("🧪 WarpTest1: Direct Claude Streaming Test")
    print("=" * 50)
    print("Testing real-time Claude output capture...")
    print()
    
    # Simple prompt that should generate continuous output
    prompt = """Count from 1 to 10, explaining each number briefly. 
Take your time and be descriptive. 
After each number, pause and think about its mathematical properties."""
    
    print(f"📝 Prompt: {prompt[:60]}...")
    print()
    
    # Show exact command being executed
    cmd = ['claude', '--print', '--dangerously-skip-permissions', prompt]
    print(f"🚀 Command: {' '.join(cmd)}")
    print()
    
    start_time = time.time()
    print(f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}")
    print("📡 Live Claude Output:")
    print("-" * 30)
    
    try:
        # Method 1: Character-by-character streaming
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,  # Unbuffered for real-time
            universal_newlines=True
        )
        
        print(f"🔢 Process PID: {process.pid}")
        
        # Stream output in real-time
        output_chars = 0
        last_update = time.time()
        
        while True:
            # Try to read a character
            char = process.stdout.read(1)
            
            if not char:
                # Check if process is done
                if process.poll() is not None:
                    break
                # Brief sleep to avoid busy waiting
                time.sleep(0.01)
                continue
            
            # Print character immediately
            print(char, end='', flush=True)
            output_chars += 1
            
            # Show periodic stats
            current_time = time.time()
            if current_time - last_update > 5.0:  # Every 5 seconds
                elapsed = current_time - start_time
                print(f"\n[📊 {elapsed:.1f}s, {output_chars} chars]", end='', flush=True)
                last_update = current_time
        
        # Get any remaining output
        remaining_stdout, stderr = process.communicate()
        if remaining_stdout:
            print(remaining_stdout, end='', flush=True)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        print()
        print("-" * 30)
        print(f"✅ Test Complete!")
        print(f"⏱️  Total time: {elapsed:.2f} seconds")
        print(f"📊 Total characters: {output_chars}")
        print(f"🔄 Return code: {process.returncode}")
        
        if stderr:
            print(f"⚠️  Stderr: {stderr}")
        
        # Test conversation continuity
        print()
        print("🔗 Testing conversation continuity...")
        test_conversation_continuity()
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        if 'process' in locals():
            process.terminate()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0


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