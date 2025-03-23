import logging.config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.editor.editor_router import router as editor_router
from app.health.health_router import router as health_router
from app.session.session_model import Base as session_base
from app.session.session_router import router as session_router
from app.app_config import ALLOWED_HOSTS, API_VERSION, DEBUG
from app.user.user_model import Base as user_base
from app.user.user_router import router as user_router
from app.utils.logging_config import logger, get_logging_config

# Configure logging


# Create database tables
user_base.metadata.create_all(bind=engine)
session_base.metadata.create_all(bind=engine)
logger.info("Database tables created successfully")

# Initialize FastAPI app
app = FastAPI(
    title="Collaborative Code Editor API",
    description="Backend API for real-time collaborative code editing",
    version=API_VERSION,
    debug=DEBUG,
    docs_url="/docs",
    openapi_url = "/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Register routers
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(session_router, prefix="/sessions", tags=["Sessions"])
app.include_router(editor_router, prefix="/editor", tags=["Editor"])

logger.info("Application startup complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG,
        log_config=get_logging_config()
    )