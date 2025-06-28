import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercel expects a variable named 'app' to be exposed
application = app

if __name__ == "__main__":
    app.run()
