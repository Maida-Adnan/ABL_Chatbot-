# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat, health

app = FastAPI(title="Allied Bank Chatbot API")

# Allows a frontend running on a different port/domain to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development; restrict this later for production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(chat.router)