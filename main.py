from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import json
from typing import List
from pydantic import BaseModel
import logging


app = FastAPI()
logging.basicConfig(level=logging.INFO)

class SignalPoint(BaseModel):
    latitude: float
    longitude: float
    rsrp: int


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                points = json.loads(data)
                if isinstance(points, list):
                    for point_data in points:
                        point = SignalPoint(**point_data)
                        logging.info(f"Received data: Latitude={point.latitude}, Longitude={point.longitude}, RSRP={point.rsrp}")
                        
                else:
                        point = SignalPoint(**points)
                        logging.info(f"Received data: Latitude={point.latitude}, Longitude={point.longitude}, RSRP={point.rsrp}")
                        
            except json.JSONDecodeError:
                logging.warning(f"Received invalid JSON: {data}")
            except Exception as e:
                logging.error(f"Error processing data: {e}")

    except WebSocketDisconnect:
        logging.info("Client disconnected")
    except Exception as e:
       logging.error(f"Unexpected error: {e}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8181)
