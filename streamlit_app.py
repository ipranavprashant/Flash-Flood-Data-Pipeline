import streamlit as st  
from ultralytics import YOLO  
from PIL import Image  
import numpy as np  
import cv2  
import pandas as pd  
import time  
import plotly.graph_objects as go 
import uuid
import os

st.set_page_config(page_title="Flash Flood Early Warning System", layout="wide")

if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())[:8]  

session_id = st.session_state["session_id"]
data_file = f"/Users/pranavprashant/Desktop/Shubham/data_{session_id}.csv"

if not os.path.exists(data_file) or os.stat(data_file).st_size == 0:
    df = pd.DataFrame(columns=["Flash Flood Confidence", "Normal Flow Confidence", "Not Flash Flood Confidence"])
    df.to_csv(data_file, index=False,float_format="%.10f")

frontend_url = f"http://localhost:5173?session_id={session_id}"
st.markdown(f"[🔗 Open React App](<{frontend_url}>)")

st.title("Flash Flood Early Warning System")


@st.cache_resource
def load_model():
    return YOLO(rf"/Users/pranavprashant/Desktop/Shubham/model.pt")

model = load_model()

upload, camera, live = st.tabs(["Upload", "Camera", "Live"])

df = pd.read_csv(data_file) 

with upload:
    st.subheader("Upload an Image for Processing")
    col1, col2 = st.columns(2)

    with col1:
        uploaded_file = st.file_uploader("Choose an image:", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            campic = Image.open(uploaded_file)
            st.image(campic, caption="Uploaded Image", use_container_width=True)
            results = model.predict(source=campic)

            with col2:
                for result in results:
                    st.image(result.plot(), caption="Processed Image", use_container_width=True, channels="BGR")

with camera:
    st.subheader("Capture Image from Camera")
    col1, col2 = st.columns(2)

    with col1:
        pic = st.camera_input(" ")

        if pic:
            pic = Image.open(pic)
            results = model.predict(source=pic)
            p1, p2, p3 = results[0].probs.data.numpy()[:3]

            with col2:
                for result in results:
                    st.image(result.plot(), caption="Processed Image", use_container_width=True, channels="BGR")
                
                new_row = pd.DataFrame({
                    "Flash Flood Confidence": [p1],
                    "Normal Flow Confidence": [p2],
                    "Not Flash Flood Confidence": [p3]
                })

                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(data_file, index=False,float_format="%.10f") 
                os.utime(data_file, None)
                st.dataframe(df)

with live:
    st.subheader("Live Video Processing")
    col1, col2 = st.columns(2)

    if "video_streaming" not in st.session_state:
        st.session_state.video_streaming = False 

    start_button = st.button("Start Capture")
    stop_button = st.button("Stop Video Capture")

    if start_button:
        st.session_state.video_streaming = True

    if stop_button:
        st.session_state.video_streaming = False

    if st.session_state.video_streaming:
        cap = cv2.VideoCapture(0)
        stframe = st.empty()
        stdframe = st.empty()
        plot_placeholder = st.empty()

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[], y=[], mode="lines", name="Flash Flood"))
        fig.add_trace(go.Scatter(x=[], y=[], mode="lines", name="Normal Flow"))
        fig.add_trace(go.Scatter(x=[], y=[], mode="lines", name="Not Flash Flood"))
        fig.update_layout(title="Confidence Values Over Time", xaxis_title="Time", yaxis_title="Confidence")

        while st.session_state.video_streaming:
            ret, frame = cap.read()
            if not ret:
                st.warning("Failed to capture video!")
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = model.predict(source=frame)

            p1, p2, p3 = results[0].probs.data.numpy()[:3]  

            stframe.image([x.plot() for x in results][0], caption="Processed Image", use_container_width=True, channels="RGB")

            new_row = pd.DataFrame({
                "Flash Flood Confidence": [p1],
                "Normal Flow Confidence": [p2],
                "Not Flash Flood Confidence": [p3]
            })
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(data_file, index=False,float_format="%.10f")  
            os.utime(data_file, None)

            stdframe.dataframe(df, use_container_width=True, height=660)

            fig.data[0].x = list(range(len(df)))
            fig.data[0].y = df["Flash Flood Confidence"]
            fig.data[1].x = list(range(len(df)))
            fig.data[1].y = df["Normal Flow Confidence"]
            fig.data[2].x = list(range(len(df)))
            fig.data[2].y = df["Not Flash Flood Confidence"]

            plot_placeholder.plotly_chart(fig, use_container_width=True)
            time.sleep(0.1)

        cap.release()
