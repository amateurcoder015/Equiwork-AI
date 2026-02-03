from fastapi import FastAPI
from .api import endpoints
from .seed.demo_data import seed_data

app = FastAPI(title="EquiWork AI")

# Initialize Data
seed_data()

# Register Routes
app.include_router(endpoints.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)