from fastapi import FastAPI

app = FastAPI(title="PokeBindr API")


@app.get("/health")
def health_check():
    return {"status": "Gotta Catch 'em all!"}