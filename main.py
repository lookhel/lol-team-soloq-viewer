import uvicorn
from src.api.routes import app
from src.db.database import init_db


if __name__ == "__main__":
    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)