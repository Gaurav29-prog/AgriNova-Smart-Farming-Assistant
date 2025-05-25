from flask import Flask, render_template, request
import requests
from datetime import datetime
import pickle
import numpy as np
import pandas as pd

app = Flask(__name__)

# Load the model
with open('rainfall_prediction_model.pkl', 'rb') as model_file:
    model_1 = pickle.load(model_file)

feature_names = ['pressure', 'dewpoint', 'humidity', 'cloud', 'sunshine', 'winddirection', 'windspeed']

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/crop_recommendation')
def crop_recommendation():
    return render_template('crop_recom.html')



# Load models and scalers once when the application starts
try:
    model_2 = pickle.load(open('crop_recommendation_model.pkl', 'rb'))
    sc = pickle.load(open('standscaler.pkl', 'rb'))
    mx = pickle.load(open('minmaxscaler.pkl', 'rb'))
except Exception as e:
    print(f"Error loading model files: {e}")
    # Handle error appropriately (maybe disable prediction functionality)

crop_dict = {
    1: "Rice", 2: "Maize", 3: "Jute", 4: "Cotton", 5: "Coconut", 
    6: "Papaya", 7: "Orange", 8: "Apple", 9: "Muskmelon", 10: "Watermelon",
    11: "Grapes", 12: "Mango", 13: "Banana", 14: "Pomegranate", 15: "Lentil",
    16: "Blackgram", 17: "Mungbean", 18: "Mothbeans", 19: "Pigeonpeas",
    20: "Kidneybeans", 21: "Chickpea", 22: "Coffee"
}

# Map crop names to PNG image filenames
crop_images = {
    "Rice": "rice.png",
    "Maize": "maize.png",
    "Jute": "jute.png",
    "Cotton": "cotton.png",
    "Coconut": "coconut.png",
    "Papaya": "papaya.png",
    "Orange": "orange.png",
    "Apple": "apple.png",
    "Muskmelon": "muskmelon.png",
    "Watermelon": "watermelon.png",
    "Grapes": "grapes.png",
    "Mango": "mango.png",
    "Banana": "banana.png",
    "Pomegranate": "pomegranate.png",
    "Lentil": "lentil.png",
    "Blackgram": "blackgram.png",
    "Mungbean": "mungbean.png",
    "Mothbeans": "mothbeans.png",
    "Pigeonpeas": "pigeonpeas.png",
    "Kidneybeans": "kidneybeans.png",
    "Chickpea": "chickpea.png",
    "Coffee": "coffee.png"
}

@app.route("/predict_crop", methods=['POST'])
def predict_crop():
    try:
        # Get and validate form data
        features = [
            float(request.form['Nitrogen']),
            float(request.form['Phosphorus']),
            float(request.form['Potassium']),
            float(request.form['Temperature']),
            float(request.form['Humidity']),
            float(request.form['pH']),
            float(request.form['Rainfall'])
        ]
        
        # Transform and predict
        scaled = sc.transform(mx.transform(np.array(features).reshape(1, -1)))
        
        # Get top 3 predictions
        if hasattr(model_2, 'predict_proba'):
            probs = model_2.predict_proba(scaled)[0]
            top3_idx = np.argsort(probs)[-3:][::-1]  # Indices of top 3 crops
            top3_crops = [list(crop_images.keys())[i] for i in top3_idx]
            confidences = [round(probs[i]*100, 1) for i in top3_idx]  # Convert to percentages
        else:
            pred = model_2.predict(scaled)[0]
            top3_crops = [list(crop_images.keys())[pred]]
            confidences = [100]  # Default confidence if no probabilities
        
        # Prepare results with PNG images
        results = []
        for crop, conf in zip(top3_crops, confidences):
            results.append({
                "name": crop,
                "image": crop_images.get(crop, "default_crop.png"),  # PNG fallback
                "confidence": f"{conf}%",
                "conditions": {
                    "Temp": f"{features[3]}°C",
                    "Humidity": f"{features[4]}%",
                    "pH": features[5],
                    "Rainfall": f"{features[6]}mm"
                }
            })
        
        return render_template('crop_recom.html', 
                           recommendations=results,
                           success=True)
    
    except ValueError as e:
        return render_template('crop_recom.html',
                           error=f"Invalid input: {str(e)}",
                           success=False)
    except Exception as e:
        return render_template('crop_recom.html',
                           error=f"Prediction error: {str(e)}",
                           success=False)
    
# raimfall ka landing page 
@app.route('/rainfall')
def rainfall():
    return render_template('rainfall.html')

# rainfall ka result
@app.route('/predict_rainfall', methods=['POST'])
def predict_rainfall():
    try:
        # Get data from the form
        input_data = [
            float(request.form['pressure']),
            float(request.form['dewpoint']),
            float(request.form['humidity']),
            float(request.form['cloudcover']),
            float(request.form['sunshine']),
            float(request.form['winddirection']),
            float(request.form['windspeed']),
        ]

        # Create DataFrame for the input
        input_df = pd.DataFrame([input_data], columns=feature_names)

        # Predict using the loaded model
        prediction = model_1.predict(input_df)

        # Convert prediction to human-readable format
        result = "Rainfall Expected" if prediction[0] == 1 else "No Rainfall Expected"

        return render_template('rainfall.html', prediction_result=result)
    
    except Exception as e:
        error_message = f"Error: Please check your input values - {str(e)}"
        return render_template('rainfall.html', prediction_result=error_message)




# weather ka landing page 

@app.route('/weather')
def weather():
    return render_template('weather.html')

# weather ka result i.e api 

@app.route('/get_weather', methods=['POST'])
def get_weather():
    if request.method == 'POST':
        city_name = request.form.get('city')
        if not city_name:
            return render_template('weather.html', error="Please enter a city name.")

        api_key = "b3a74142dd55447ce59860afc2c3642e"
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}'

        try:
            response = requests.get(url)
            response.raise_for_status()
            json_object = response.json()

            if 'main' not in json_object:
                return render_template('weather.html', error="Invalid city name or API error.")

            # Extract weather data
            temp_kelvin = float(json_object['main']['temp'])
            humidity = float(json_object['main']['humidity'])
            pressure = float(json_object['main']['pressure'])
            dew_point = float(json_object['main']['feels_like'])
            wind_speed = float(json_object['wind']['speed'])*3.6
            wind_direction = int(json_object['wind']['deg'])
            cloud_cover = int(json_object['clouds']['all'])
            country_name = json_object['sys']['country'] if 'sys' in json_object else "N/A"
            weather_icon = json_object['weather'][0]['icon']
            weather_description = json_object['weather'][0]['description']

            # Convert timestamps
            sunrise_time = datetime.fromtimestamp(json_object['sys']['sunrise']).strftime('%H:%M:%S')
            sunset_time = datetime.fromtimestamp(json_object['sys']['sunset']).strftime('%H:%M:%S')
            sunshine_duration = round((json_object['sys']['sunset'] - json_object['sys']['sunrise']) / 3600, 2)

            # Convert temperatures
            temp_celsius = round(temp_kelvin - 273.15, 2)
            dew_point_celsius = round(dew_point - 273.15, 2)

            return render_template('weather.html', 
                                temperature=temp_celsius, 
                                pressure=pressure, 
                                humidity=humidity, 
                                dew_point=dew_point_celsius, 
                                wind_speed=wind_speed, 
                                wind_direction=wind_direction, 
                                cloud_cover=cloud_cover, 
                                sunrise=sunrise_time, 
                                sunset=sunset_time, 
                                sunshine_hours=sunshine_duration,
                                weather_icon=weather_icon,
                                weather_description=weather_description,
                                city_name=city_name, 
                                country_name=country_name)
        
        except requests.exceptions.RequestException as e:
            return render_template('weather.html', error=f"Error fetching weather data: {e}")
        except KeyError as e:
            return render_template('weather.html', error=f"Missing data in API response: {e}")

    return render_template('weather.html')

if __name__ == '__main__':
    app.run(debug=True)