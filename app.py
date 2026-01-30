import subprocess
import sys
import os

# Auto-install missing dependencies
def install_dependencies():
    """Install missing Flask dependencies"""
    required_packages = ['flask', 'flask-cors']
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"[INFO] Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '-q'])
            print(f"[INFO] {package} installed successfully")

# Install dependencies first
try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS
except ImportError:
    print("[INFO] Installing required packages...")
    install_dependencies()
    from flask import Flask, jsonify, request
    from flask_cors import CORS

import json
from pathlib import Path
import threading
import time

app = Flask(__name__)
CORS(app)

# Track running processes
processes = {
    'gesture': None,
    'voice': None
}

# Get the directory where this script is located
BASE_DIR = Path(__file__).parent

@app.route('/', methods=['GET'])
def index():
    """Serve the frontend"""
    index_path = BASE_DIR / 'index.html'
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html'}
    else:
        return jsonify({
            'success': False,
            'message': f'index.html not found at {index_path}',
            'code': 'FILE_NOT_FOUND'
        }), 404

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get the status of running processes"""
    gesture_running = processes['gesture'] is not None and processes['gesture'].poll() is None
    voice_running = processes['voice'] is not None and processes['voice'].poll() is None
    
    return jsonify({
        'gesture_control': {
            'running': gesture_running,
            'module': 'sparsh_unified.py'
        },
        'voice_control': {
            'running': voice_running,
            'module': 'voice.py'
        }
    })

@app.route('/api/launch/gesture', methods=['POST'])
def launch_gesture():
    """Launch the gesture control module"""
    try:
        # Check if already running
        if processes['gesture'] is not None and processes['gesture'].poll() is None:
            return jsonify({
                'success': False,
                'message': 'Gesture control is already running',
                'code': 'ALREADY_RUNNING'
            }), 400
        
        # Get the path to sparsh_unified.py
        script_path = BASE_DIR / 'sparsh_unified.py'
        
        if not script_path.exists():
            return jsonify({
                'success': False,
                'message': f'sparsh_unified.py not found at {script_path}',
                'code': 'FILE_NOT_FOUND'
            }), 404
        
        # Launch the gesture control script
        process = subprocess.Popen(
            ['python', str(script_path)],
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        processes['gesture'] = process
        
        return jsonify({
            'success': True,
            'message': 'Gesture control launched successfully',
            'pid': process.pid,
            'module': 'sparsh_unified.py'
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error launching gesture control: {str(e)}',
            'code': 'LAUNCH_ERROR'
        }), 500

@app.route('/api/launch/voice', methods=['POST'])
def launch_voice():
    """Launch the voice control module"""
    try:
        # Check if already running
        if processes['voice'] is not None and processes['voice'].poll() is None:
            return jsonify({
                'success': False,
                'message': 'Voice control is already running',
                'code': 'ALREADY_RUNNING'
            }), 400
        
        # Get the path to voice.py
        script_path = BASE_DIR / 'voice.py'
        
        if not script_path.exists():
            return jsonify({
                'success': False,
                'message': f'voice.py not found at {script_path}',
                'code': 'FILE_NOT_FOUND'
            }), 404
        
        # Launch the voice control script
        process = subprocess.Popen(
            ['python', str(script_path)],
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        processes['voice'] = process
        
        return jsonify({
            'success': True,
            'message': 'Voice control launched successfully',
            'pid': process.pid,
            'module': 'voice.py'
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error launching voice control: {str(e)}',
            'code': 'LAUNCH_ERROR'
        }), 500

@app.route('/api/stop/gesture', methods=['POST'])
def stop_gesture():
    """Stop the gesture control module"""
    try:
        if processes['gesture'] is None or processes['gesture'].poll() is not None:
            return jsonify({
                'success': False,
                'message': 'Gesture control is not running',
                'code': 'NOT_RUNNING'
            }), 400
        
        processes['gesture'].terminate()
        
        # Wait for process to terminate
        try:
            processes['gesture'].wait(timeout=5)
        except subprocess.TimeoutExpired:
            processes['gesture'].kill()
        
        processes['gesture'] = None
        
        return jsonify({
            'success': True,
            'message': 'Gesture control stopped successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error stopping gesture control: {str(e)}',
            'code': 'STOP_ERROR'
        }), 500

@app.route('/api/stop/voice', methods=['POST'])
def stop_voice():
    """Stop the voice control module"""
    try:
        if processes['voice'] is None or processes['voice'].poll() is not None:
            return jsonify({
                'success': False,
                'message': 'Voice control is not running',
                'code': 'NOT_RUNNING'
            }), 400
        
        processes['voice'].terminate()
        
        # Wait for process to terminate
        try:
            processes['voice'].wait(timeout=5)
        except subprocess.TimeoutExpired:
            processes['voice'].kill()
        
        processes['voice'] = None
        
        return jsonify({
            'success': True,
            'message': 'Voice control stopped successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error stopping voice control: {str(e)}',
            'code': 'STOP_ERROR'
        }), 500

@app.route('/api/stop/all', methods=['POST'])
def stop_all():
    """Stop all running modules"""
    try:
        results = []
        
        for module_name, process in processes.items():
            if process is not None and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    results.append(f'{module_name}: stopped')
                except subprocess.TimeoutExpired:
                    process.kill()
                    results.append(f'{module_name}: killed')
                except Exception as e:
                    results.append(f'{module_name}: error - {str(e)}')
                finally:
                    processes[module_name] = None
        
        return jsonify({
            'success': True,
            'message': 'All modules stopped',
            'results': results
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error stopping modules: {str(e)}',
            'code': 'STOP_ERROR'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'server': 'SPARSH Backend API',
        'version': '1.0.0'
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'message': 'Endpoint not found',
        'code': 'NOT_FOUND'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'message': 'Internal server error',
        'code': 'INTERNAL_ERROR'
    }), 500

def cleanup_on_exit():
    """Clean up processes on server exit"""
    print("\nCleaning up running processes...")
    for module_name, process in processes.items():
        if process is not None and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"  {module_name}: stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"  {module_name}: killed")
            except Exception as e:
                print(f"  {module_name}: error - {str(e)}")

if __name__ == '__main__':
    try:
        print("="*50)
        print("SPARSH Backend API Server")
        print("="*50)
        print(f"Base directory: {BASE_DIR}")
        print(f"Starting server on http://localhost:5000")
        print("Press Ctrl+C to stop the server")
        print("="*50)
        
        # Run the Flask app
        app.run(
            host='localhost',
            port=5000,
            debug=False,
            use_reloader=False
        )
    except KeyboardInterrupt:
        cleanup_on_exit()
    except Exception as e:
        print(f"Error: {e}")
        cleanup_on_exit()
