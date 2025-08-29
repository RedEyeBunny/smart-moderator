from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import moderation, analytics


app = FastAPI(title="Smart Content Moderator API", version="1.0.0")

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


app.include_router(moderation.router, prefix="/api/v1/moderate", tags=["moderation"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])


@app.get("/")
def root():
    return {"status": "ok", "service": "Smart Content Moderator API"}
