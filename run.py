"""Application entry point"""
import os
from app import create_app

if __name__ == '__main__':
    config = os.getenv('FLASK_ENV', 'development')
    app = create_app(config)
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=(config == 'development')
    )
