import os
import sys
from pathlib import Path
import logging

def check_file_permissions(file_path):
    try:
        perms = oct(os.stat(file_path).st_mode)[-3:]
        owner = os.stat(file_path).st_uid
        group = os.stat(file_path).st_gid
        return {
            'permissions': perms,
            'owner': owner,
            'group': group,
            'readable': os.access(file_path, os.R_OK),
            'writable': os.access(file_path, os.W_OK),
            'executable': os.access(file_path, os.X_OK)
        }
    except Exception as e:
        return f"Error checking permissions: {str(e)}"

def test_flask_static(app, results):
    with app.app_context():
        try:
            test_file = 'index.html'
            resolved_path = app.send_static_file(test_file)
            results['info'].append(f"Static file resolution test passed for {test_file}")
        except Exception as e:
            results['errors'].append(f"Static file resolution failed: {str(e)}")

def run_diagnostics():
    results = {
        'critical': [],
        'errors': [],
        'warnings': [],
        'info': []
    }
    
    # Check environment
    results['info'].append(f"Python version: {sys.version}")
    results['info'].append(f"Current working directory: {os.getcwd()}")
    
    # Check project structure
    project_root = os.path.dirname(os.path.abspath(__file__))
    results['info'].append(f"Project root: {project_root}")
    
    # Check static directory
    static_dir = os.path.join(project_root, 'static')
    if not os.path.exists(static_dir):
        results['critical'].append(f"Static directory missing: {static_dir}")
    else:
        results['info'].append(f"Static directory found: {static_dir}")
        static_files = os.listdir(static_dir)
        results['info'].append(f"Static files found: {static_files}")
        
        # Check required files
        required_files = ['index.html', 'recorder.js']
        for file in required_files:
            file_path = os.path.join(static_dir, file)
            if not os.path.exists(file_path):
                results['critical'].append(f"Required file missing: {file}")
            else:
                perms = check_file_permissions(file_path)
                results['info'].append(f"File {file} permissions: {perms}")
    
    # Check Flask configuration
    try:
        from app.init import create_app
        app = create_app()
        results['info'].append(f"Flask static folder: {app.static_folder}")
        results['info'].append(f"Flask static url path: {app.static_url_path}")
        test_flask_static(app, results)
    except Exception as e:
        results['critical'].append(f"Failed to create Flask app: {str(e)}")
    
    # Print results
    print("\n=== Diagnostic Results ===")
    for category in ['critical', 'errors', 'warnings', 'info']:
        if results[category]:
            print(f"\n{category.upper()}:")
            for item in results[category]:
                print(f"- {item}")

    return results

if __name__ == '__main__':
    run_diagnostics()
