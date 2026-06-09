import os
from joblib import dump, load
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# --- BASE DIRECTORY CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_model_path(mode='email'):
    """Helper function to calculate the explicit path based on mode."""
    filename = "sms_model.joblib" if mode == 'sms' else "email_model.joblib"
    return os.path.join(BASE_DIR, filename)

def model_exists(mode='email'):
    return os.path.exists(get_model_path(mode))

def save_model(vec, model, mode='email'):
    dump((vec, model), get_model_path(mode))

def load_model(mode='email'):
    target_path = get_model_path(mode)
    
    if not os.path.exists(target_path):
        print(f"❌ Model file not found at: {target_path}. Please run the training script first.")
        return None, None

    try:
        # Load the specific model file requested
        data = load(target_path)
        
        # Robust handling matching your original structural verification logic
        if isinstance(data, tuple) and len(data) == 2:
            vec, model = data
            if hasattr(vec, 'transform') and hasattr(model, 'predict'):
                return vec, model
            else:
                print(f"❌ Loaded objects from {target_path} are not valid vectorizer/model structures")
                return None, None
        else:
            print(f"❌ Unexpected model format inside file: {type(data)}")
            return None, None
            
    except Exception as e:
        print(f"❌ Error loading model file: {str(e)}")
        return None, None

def predict(text, mode='email'):
    """
    Accepts raw text content along with an explicit platform mode.
    Returns clean, raw decimal probabilities representing the fraud risk index.
    """
    vec, model = load_model(mode=mode)
    if vec is None or model is None:
        return None, 0.0

    try:
        # Transform the input text using the mode-specific vocabulary map
        X = vec.transform([text])
        
        # Make prediction labels
        pred = model.predict(X)[0]
        
        # Isolate class 1 (Fraudulent) as a pure decimal probability (0.0 to 1.0)
        prob_matrix = model.predict_proba(X)[0]
        prob = float(prob_matrix[1])  
        
        return pred, prob
        
    except Exception as e:
        print(f"❌ Prediction computation error: {str(e)}")
        return None, 0.0

def check_model():
    """Check if standard configurations are functional."""
    for test_mode in ['email', 'sms']:
        print(f"\n🔍 Testing diagnostic state for system category: {test_mode.upper()}")
        if model_exists(test_mode):
            print(f"✅ Binary artifact discovered on disk storage")
            vec, model = load_model(test_mode)
            if vec and model:
                print(f"✅ Struct definitions parsed correctly into application runtime")
                test_result = predict("test verification string", mode=test_mode)
                if test_result[0] is not None:
                    print(f"✅ Prediction inference baseline successfully generated")
            else:
                print(f"❌ Target structural assets corrupted or failing instance check blocks")
        else:
            print(f"⚠️ Notice: Model configuration array is missing for mode type: '{test_mode}'")
    return True