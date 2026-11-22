"""
REST API server using FastAPI
"""

from typing import List, Dict
from datetime import datetime

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


if FASTAPI_AVAILABLE:
    
    app = FastAPI(title="Datapoint Synthesizer API", version="3.0.0")
    
    class GenerateRequest(BaseModel):
        examples: List[Dict]
        n: int = 10
        strategy: str = "balanced"
    
    class GenerateResponse(BaseModel):
        datapoints: List[Dict]
        count: int
        timestamp: str
    
    @app.post("/generate", response_model=GenerateResponse)
    async def generate_datapoints(request: GenerateRequest):
        try:
            from core.synthesizer import DatapointSynthesizerV3
            from core.strategies import Strategy
            
            synthesizer = DatapointSynthesizerV3(strategy=Strategy[request.strategy.upper()])
            synthesizer.set_examples(request.examples)
            datapoints = synthesizer.synthesize(n=request.n)
            
            return GenerateResponse(
                datapoints=datapoints,
                count=len(datapoints),
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    
    @app.get("/templates")
    async def get_templates():
        return {"templates": ["QA Pairs", "RL SARS", "Classification", "NER", "Image"]}
    
    def start_server(host: str = "0.0.0.0", port: int = 8000):
        print(f"🌐 Starting API server at http://{host}:{port}")
        uvicorn.run(app, host=host, port=port, log_level="info")

else:
    def start_server(host: str = "0.0.0.0", port: int = 8000):
        print("❌ FastAPI not installed. Install with: pip install fastapi uvicorn")
