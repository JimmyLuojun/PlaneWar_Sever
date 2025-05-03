# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/server/app.py
# This script is primarily used to run the development server easily via poetry script.
# For production, you'll typically point Gunicorn directly to the app factory.

from . import create_app # Import the factory function from __init__.py

# Create the Flask app instance using the factory
app = create_app()

def run_dev_server():
    """Runs the Flask development server."""
    print("Starting Flask development server...")
    # Use host='0.0.0.0' to make it accessible on your network
    # debug=True will be set by DevelopmentConfig via FLASK_ENV=development
    # Use port other than 5000 if it conflicts
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    # This allows running the server directly using `python -m server.app`
    run_dev_server()