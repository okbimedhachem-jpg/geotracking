from fastapi import FastAPI

app = FastAPI(title="GeoTracking")


@app.get("/")
def root() -> dict:
    return {"message": "GeoTracking backend"}
