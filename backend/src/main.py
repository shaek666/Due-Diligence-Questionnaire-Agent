from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.router import api_router
from .core.config import settings
from .storage.db import Base, engine, db_session
from .utils.logging import configure_logging
from .services.config_state import check_and_update_signature


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)

    @app.on_event("startup")
    def _create_tables() -> None:
        configure_logging()
        Base.metadata.create_all(bind=engine)
        try:
            with db_session() as db:
                changed, previous, current = check_and_update_signature(db)
            if changed:
                from .workers.tasks import handle_config_change_task

                handle_config_change_task.delay(previous, current)
        except Exception:
            # Avoid blocking startup if config tracking fails.
            pass

    return app


app = create_app()
