"""Test that all imports work correctly."""

import traceback
import sys

def test_imports():
    """Test all module imports."""
    
    tests = [
        ("Config Manager", lambda: __import__('config.config', fromlist=['ConfigManager'])),
        ("Audio Player", lambda: __import__('core.audio_player', fromlist=['AudioPlayer'])),
        ("Output Manager", lambda: __import__('core.output_manager', fromlist=['OutputManager'])),
        ("DSL Parser", lambda: __import__('dsl.parser', fromlist=['DSLParser'])),
        ("Torrent Manager", lambda: __import__('torrenting.torrent_manager', fromlist=['TorrentManager'])),
        ("Hardware Button Handler", lambda: __import__('hardware.button_handler', fromlist=['ButtonHandler'])),
        ("Library Manager", lambda: __import__('library.library_manager', fromlist=['LibraryManager'])),
        ("Web App", lambda: __import__('web.app', fromlist=['create_app'])),
        ("Main Module", lambda: __import__('main', fromlist=['AudioStream'])),
    ]
    
    passed = 0
    failed = 0
    
    print("\n" + "="*50)
    print("AudioStream - Import Test")
    print("="*50)
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"✓ {name:40} PASSED")
            passed += 1
        except Exception as e:
            print(f"✗ {name:40} FAILED")
            print(f"  Error: {str(e)[:60]}")
            failed += 1
    
    print("="*50)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*50)
    
    return failed == 0

if __name__ == '__main__':
    success = test_imports()
    sys.exit(0 if success else 1)
