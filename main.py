from fastapi import FastAPI
from backend.routes.admin_routes import admin_router
from backend.routes.apple_routes import apple_router

app = FastAPI()

# Include API routers
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(apple_router, prefix="/apple", tags=["Apple"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Apple Information and Admin Management System"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
