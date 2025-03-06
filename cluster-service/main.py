import logging
from flask import Flask
from src.controller.routes import routes_bp

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.register_blueprint(routes_bp)
    return app

app = create_app()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logging.info("Starting the Flask application...")
    # Run the app
    app.run(port=8082, host="0.0.0.0")