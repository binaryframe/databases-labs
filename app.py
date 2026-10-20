import os
from dotenv import load_dotenv
from app.my_project.factory import create_app

load_dotenv()
application = create_app()

if __name__ == "__main__":
    application.run(
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "1") == "1",
    )
