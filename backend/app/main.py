from fastapi import FastAPI

from app.api.routes import applications, emails, health, job_ads, matching


def create_app() -> FastAPI:
    app = FastAPI(title="Job Applications Dashboard API", version="0.1.0")

    app.include_router(health.router)
    app.include_router(job_ads.router, prefix="/job-ads", tags=["job ads"])
    app.include_router(emails.router, prefix="/emails", tags=["emails"])
    app.include_router(applications.router, prefix="/applications", tags=["applications"])
    app.include_router(matching.router, prefix="/matching", tags=["matching"])

    return app


app = create_app()

