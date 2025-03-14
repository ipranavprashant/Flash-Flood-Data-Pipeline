from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import pandas as pd
import os
import asyncio

app = FastAPI()

async def stream_data(websocket: WebSocket, session_id: str):
    await websocket.accept()
    file_path = f"/Users/pranavprashant/Desktop/Shubham/data_{session_id}.csv"
    last_size = 0  
    last_file_size = 0  

    try:
        while True:
            if not os.path.exists(file_path):
                await asyncio.sleep(1)
                continue

            current_file_size = os.path.getsize(file_path)

            if current_file_size > last_file_size:
                df = pd.read_csv(file_path)

                if len(df) > last_size:
                    new_data = df.iloc[last_size:].to_dict(orient="records")
                    await websocket.send_json(new_data)
                    last_size = len(df)

                last_file_size = current_file_size 

            await asyncio.sleep(1)
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for session: {session_id}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print(f"Closing WebSocket connection for session: {session_id}")

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await stream_data(websocket, session_id)
