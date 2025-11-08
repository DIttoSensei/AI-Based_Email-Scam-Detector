import os
from joblib import dump, load
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

MODEL_PATH = os.path.join(os.path.dirname(__file__), "email_model.joblib")

def model_exists():
    return os.path.exists(MODEL_PATH)

def save_model(vec, model):
    dump((vec, model), MODEL_PATH)

def load_model():
    if not model_exists():
        print("❌ Model file not found. Please run the training script first.")
        return None, None

    try:
        # Load the model file
        data = load(MODEL_PATH)
        
        # Simple and robust handling - your training script saves (vectorizer, model)
        if isinstance(data, tuple) and len(data) == 2:
            vec, model = data
            # Basic validation
            if hasattr(vec, 'transform') and hasattr(model, 'predict'):
                return vec, model
            else:
                print("❌ Loaded objects are not valid vectorizer/model")
                return None, None
        else:
            print(f"❌ Unexpected model format: {type(data)}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error loading model: {str(e)}")
        return None, None

def predict(text):
    vec, model = load_model()
    if vec is None or model is None:
        return None, 0.0

    try:
        # Transform the input text
        X = vec.transform([text])
        
        # Make prediction
        pred = model.predict(X)[0]
        prob = float(max(model.predict_proba(X)[0]))
        
        return pred, prob
        
    except Exception as e:
        print(f"❌ Prediction error: {str(e)}")
        return None, 0.0

def check_model():
    """Check if model is working properly"""
    if model_exists():
        print("✅ Model file exists")
        vec, model = load_model()
        if vec and model:
            print("✅ Model loaded successfully")
            # Test with a simple prediction
            test_result = predict("test email")
            if test_result[0] is not None:
                print("✅ Model is working correctly")
                return True
        else:
            print("❌ Model file exists but cannot be loaded")
            return False
    else:
        print("❌ Model file does not exist")
        return False