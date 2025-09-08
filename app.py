import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel  
import pickle
from dataCleaning.preprocess import clean_data
import pandas as pd 
import uvicorn


app = FastAPI(title="Recommendation System API", version="1.0")
def load_model():
    model_path = os.path.join(os.path.dirname(__file__), "model", "rf_model.pkl")
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    return model

@app.post("/predict")
def predict(req: str):
    df = pd.DataFrame(req.records)
    df, y = clean_data(df)
    model = load_model()    
    predictions = model.predict(df)
    return {"recommendations": pred}
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)