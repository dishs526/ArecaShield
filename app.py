
import streamlit as st
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model # type: ignore
from PIL import Image
# Load the trained model
MODEL_PATH = "my_model.keras"
model = load_model(MODEL_PATH)

# Disease info dictionary
disease_info = {
    'stem cracking': {
        'description': 'Stem cracking is a condition where the stem of the arecanut tree develops visible cracks, leading to structural weakness.',
        'treatment': '''
- Apply organic mulch around the base to maintain soil moisture.
- Use fungicide like Copper Oxychloride paste on cracks.
- Avoid excessive irrigation and mechanical injury.'''
    },
    'Stem_bleeding': {
        'description': 'Stem bleeding is characterized by the oozing of a reddish-brown liquid from the stem, often caused by fungal infections.',
        'treatment': '''
- Clean the wound and apply Bordeaux paste.
- Use systemic fungicides like Tridemorph or Carbendazim.
- Ensure proper drainage around the tree base.'''
    },
    'Healthy_Leaf': {
        'description': 'This indicates a healthy leaf with no signs of disease or nutrient deficiency.',
        'treatment': 'No treatment required.'
    },
    'yellow leaf disease': {
        'description': 'Yellow leaf disease causes the leaves to turn yellow, often due to nutrient deficiencies or infections.',
        'treatment': '''
- Apply balanced NPK fertilizers with magnesium and boron.
- Improve soil drainage and aeration.
- Use Trichoderma biofungicides to manage root health.'''
    },
    'healthy_foot': {
        'description': 'A healthy foot region of the tree without any visible signs of disease.',
        'treatment': 'No treatment required.'
    },
    'Healthy_Trunk': {
        'description': 'A strong and disease-free trunk, ensuring the structural integrity of the tree.',
        'treatment': 'No treatment required.'
    },
    'Mahali_Koleroga': {
        'description': 'Mahali Koleroga is a fungal disease affecting the nuts, leading to rot and reduced yield.',
        'treatment': '''
- Spray 1% Bordeaux mixture before monsoon.
- Repeat sprays at 20-day intervals during rainy season.
- Collect and burn infected nuts.'''
    },
    'bud borer': {
        'description': 'Bud borer is an insect infestation that affects the growing buds, reducing productivity.',
        'treatment': '''
- Spray Neem oil (3%) or Quinalphos (0.05%) during early stages.
- Destroy affected shoots to prevent spread.
- Encourage natural predators like birds.'''
    },
    'Healthy_Nut': {
        'description': 'Indicates a healthy nut without any signs of disease or pest infestation.',
        'treatment': 'No treatment required.'
    }
}

# Preprocessing function
def preprocess_image(image):
    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    image = cv2.resize(image, (150, 150))
    image = image.astype('float32') / 255
    image = np.expand_dims(image, axis=0)
    return image

# Set wide layout but restrict UI width
st.set_page_config(page_title="Arecanut Disease Detection", page_icon="🌿", layout="wide")

# Custom CSS for appearance
st.markdown("""
    <style>
    .stApp {
        background-color: #0b3d0b; 
        color: white;
    }

    .title {
        text-align: center;
        font-size: 32px;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    .upload-box {
        background-color: #ffffff;
        color: black;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
    }

    /* ✅ Force "Choose an image..." label text to white */
    div[data-testid="stFileUploader"] label {
        color: white !important;
        opacity: 1 !important;
        font-weight: bold;
        font-size: 18px;
    }

    /* ✅ Remove default white box around uploader */
    div[data-testid="stFileUploader"] > div:first-child {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* ✅ Make uploaded filename white */
    span[data-testid="stFileUploaderFileName"] {
        color: white !important;
    }

    </style>
""", unsafe_allow_html=True)


# Layout columns to center content
left, center, right = st.columns([1, 2, 1])

with center:
    st.link_button("← Back to Home", url="http://127.0.0.1:5000/", help="Return to dashboard")
    st.markdown("<div class='title'>🌿 Arecanut Disease Detection System</div>", unsafe_allow_html=True)
    st.write("Upload an image to predict the disease.")

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.markdown("<div class='upload-box'>", unsafe_allow_html=True)
        st.image(image, caption="Uploaded Image", width=300)
        st.markdown("</div>", unsafe_allow_html=True)

        processed_image = preprocess_image(image)
        predictions = model.predict(processed_image)
        predicted_class = np.argmax(predictions)
        predicted_disease = list(disease_info.keys())[predicted_class]

        st.markdown(
            f"<h2 style='color: #FFD700;'>🎯 Predicted Disease: {predicted_disease}</h2>",
            unsafe_allow_html=True
        )

        if st.button(f"ℹ️ More about {predicted_disease}"):
            st.markdown(
                f"""
                <div style='background-color: #f0f0f0; padding: 15px; border-radius: 10px; color: black;'>
                    <strong>Description:</strong> {disease_info[predicted_disease]['description']}<br><br>
                    <strong>Treatment:</strong><pre style='white-space: pre-wrap;'>{disease_info[predicted_disease]['treatment']}</pre>
                </div>
                """, unsafe_allow_html=True
            )
