
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import os
import uvicorn
from pathlib import Path
from citizen_mode.citizen_controller import router as citizen_router
from citizen_mode import citizen_controller
from citizen_mode import chatbot_controller 
from community.community_controller import router as community_router
from datetime import datetime
from citizen_mode.ingredient_day_controller import router as ingredient_day_router
from database.db_connection import Database
from scan import scan_controller
from auth.auth_controller import router as auth_router
from scan.scan_controller import router as scan_router
from citizen_mode import chatbot_controller 
from user import streak_controller  # FIXED: removed the 'z'
from expert_mode.expert_controller import router as expert_router
from expert_mode.analytics_dashboard import router as analytics_dashboard_router
# ===== ADD THESE IMPORTS FOR CHATBOT =====
from citizen_mode.chatbot_controller import router as chatbot_router
# ===========================================
from expert_mode.ingredient_explorer import router as ingredient_explorer_router
from expert_mode.interaction_engine import router as interaction_engine_router
from expert_mode.interaction_graphs import router as interaction_graphs_router
from ml_engine.ml_controller import router as ml_router
from expert_mode.regulatory_intelligence import router as regulatory_router
from expert_mode.dataset_explorer import router as dataset_router
from expert_mode.experimentation_sandbox import router as sandbox_router


# Directories
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# Ensure uploads folder exists
os.makedirs("uploads", exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up Ingredient Safety Intelligence Platform...")
    Database.connect()
    print("✅ Database connected")
    yield
    print("🛑 Shutting down...")
    Database.disconnect()
    print("✅ Database disconnected")

app = FastAPI(
    title="Ingredient Safety Intelligence Platform",
    description="Cross-industry platform for ingredient safety analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS (Safe for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # keep like before since frontend already connected
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static folders
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# IMPORTANT: No prefix added (so frontend keeps working)
app.include_router(auth_router)
app.include_router(scan_router)
app.include_router(citizen_router)
app.include_router(ml_router)
app.include_router(scan_controller.router)
app.include_router(chatbot_controller.router)  # Now this works
app.include_router(ingredient_day_router)
app.include_router(community_router)
app.include_router(expert_router)
app.include_router(analytics_dashboard_router)
app.include_router(ingredient_explorer_router)
app.include_router(interaction_engine_router)
app.include_router(interaction_graphs_router)
app.include_router(regulatory_router)
app.include_router(dataset_router)
app.include_router(sandbox_router)

# ===== ADD CHATBOT ROUTER =====
app.include_router(chatbot_router)  # Add chatbot routes
# ===============================

# ================= LANDING PAGE =================

@app.get("/")
async def serve_landing():
    file_path = FRONTEND_DIR / "LandingPage.html"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return JSONResponse({"error": "LandingPage.html not found"}, status_code=404)

# ================= CITIZEN =================

@app.get("/citizen/{page_name}")
async def serve_citizen_page(page_name: str):

    # SECURITY FIX (properly indented inside function)
    if ".." in page_name or "/" in page_name or "\\" in page_name:
        return JSONResponse({"error": "Invalid page name"}, status_code=400)

    if page_name.endswith(".html"):
        page_name = page_name[:-5]

    file_path = FRONTEND_DIR / "citizen" / f"{page_name}.html"

    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())

    return JSONResponse({"error": f"Citizen page '{page_name}' not found"}, status_code=404)

# ================= EXPERT =================

@app.get("/expert/{page_name}")
async def serve_expert_page(page_name: str):

    if ".." in page_name or "/" in page_name or "\\" in page_name:
        return JSONResponse({"error": "Invalid page name"}, status_code=400)

    if page_name.endswith(".html"):
        page_name = page_name[:-5]

    file_path = FRONTEND_DIR / "expert" / f"{page_name}.html"

    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())

    return JSONResponse({"error": f"Expert page '{page_name}' not found"}, status_code=404)

# ================= HEALTH =================

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# ================= RUN =================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
    



# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import HTMLResponse, JSONResponse
# from contextlib import asynccontextmanager
# import os
# import uvicorn
# from pathlib import Path
# from citizen_mode.citizen_controller import router as citizen_router
# from citizen_mode import citizen_controller
# from citizen_mode import chatbot_controller 
# from datetime import datetime
# from database.db_connection import Database
# from scan import scan_controller
# from auth.auth_controller import router as auth_router
# from scan.scan_controller import router as scan_router
# from citizen_mode import chatbot_controller 
# from user import streak_controllerz
# # Directories
# BASE_DIR = Path(__file__).resolve().parent
# FRONTEND_DIR = BASE_DIR.parent / "frontend"

# # Ensure uploads folder exists
# os.makedirs("uploads", exist_ok=True)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("🚀 Starting up Ingredient Safety Intelligence Platform...")
#     Database.connect()
#     print("✅ Database connected")
#     yield
#     print("🛑 Shutting down...")
#     Database.disconnect()
#     print("✅ Database disconnected")

# app = FastAPI(
#     title="Ingredient Safety Intelligence Platform",
#     description="Cross-industry platform for ingredient safety analysis",
#     version="1.0.0",
#     lifespan=lifespan
# )

# # CORS (Safe for frontend)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],   # keep like before since frontend already connected
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Static folders
# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# # IMPORTANT: No prefix added (so frontend keeps working)
# app.include_router(auth_router)
# app.include_router(scan_router)
# app.include_router(citizen_router)
# app.include_router(scan_controller.router)
# app.include_router(chatbot_controller.router)  # Now this works

# # ================= LANDING PAGE =================

# @app.get("/")
# async def serve_landing():
#     file_path = FRONTEND_DIR / "LandingPage.html"
#     if file_path.exists():
#         with open(file_path, "r", encoding="utf-8") as f:
#             return HTMLResponse(f.read())
#     return JSONResponse({"error": "LandingPage.html not found"}, status_code=404)

# # ================= CITIZEN =================

# @app.get("/citizen/{page_name}")
# async def serve_citizen_page(page_name: str):

#     # SECURITY FIX (properly indented inside function)
#     if ".." in page_name or "/" in page_name or "\\" in page_name:
#         return JSONResponse({"error": "Invalid page name"}, status_code=400)

#     if page_name.endswith(".html"):
#         page_name = page_name[:-5]

#     file_path = FRONTEND_DIR / "citizen" / f"{page_name}.html"

#     if file_path.exists():
#         with open(file_path, "r", encoding="utf-8") as f:
#             return HTMLResponse(f.read())

#     return JSONResponse({"error": f"Citizen page '{page_name}' not found"}, status_code=404)

# # ================= EXPERT =================

# @app.get("/expert/{page_name}")
# async def serve_expert_page(page_name: str):

#     if ".." in page_name or "/" in page_name or "\\" in page_name:
#         return JSONResponse({"error": "Invalid page name"}, status_code=400)

#     if page_name.endswith(".html"):
#         page_name = page_name[:-5]

#     file_path = FRONTEND_DIR / "expert" / f"{page_name}.html"

#     if file_path.exists():
#         with open(file_path, "r", encoding="utf-8") as f:
#             return HTMLResponse(f.read())

#     return JSONResponse({"error": f"Expert page '{page_name}' not found"}, status_code=404)

# # ================= HEALTH =================

# @app.get("/api/health")
# async def health_check():
#     return {"status": "healthy"}

# # ================= RUN =================

# if __name__ == "__main__":
#     import uvicorn

#     print("\n🚀 Server running at http://localhost:8000\n")

#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



