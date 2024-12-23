
from flask import Flask, render_template, request, jsonify, redirect, session, url_for
import joblib
import pandas as pd
from utils.fert import fertilizer_benefits
from utils.fert import disease_classes
import os
import numpy as np
import cv2
import tensorflow as tf
import requests
import datetime
import mysql.connector
import base64


app = Flask(__name__,static_folder='static')
supplement_data = pd.read_csv('Data/supplement_info.csv')
dmodel = tf.keras.models.load_model('models/model.h5')
model = joblib.load('models/crop_recom_nb.pkl')
fmodel = joblib.load('models/Fertclassifier.pkl')


mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Vamsi@18",
    database="test"
)


@app.route('/', methods=['GET', 'POST'])
def login():
    ms = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM user WHERE username = %s AND password = %s', (username, password))
        account = cursor.fetchone()
        cursor.close()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            return redirect(url_for('home'))
        else:
            ms= 'Incorrect username/password!'
    return render_template('login.html',msg = ms)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        phoneno = request.form['phoneno']
        age = request.form['age']
        occupation = request.form['occupation']
        crop_cultivating = request.form['crop']

        cursor = mydb.cursor()
        cursor.execute('INSERT INTO user (username, password, phoneno, age, occupation, crop_cultivating) VALUES (%s, %s, %s, %s, %s, %s)',
                       (username, password, phoneno, age, occupation, crop_cultivating))
        mydb.commit()
        cursor.close()

        session['loggedin'] = True
        session['id'] = cursor.lastrowid
        session['username'] = username
        session['phoneno'] = phoneno  
        session['age'] = age          
        session['occupation'] = occupation  
        session['crop_cultivating'] = crop_cultivating

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect('/')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/cpredict')
def cpredict():
    return render_template('cpredict.html')

@app.route('/fertilizer')
def fertlizer():
    return render_template('fertilizer.html')

@app.route('/disease')
def disease():
    return render_template('disease.html')

@app.route('/weather')
def weather():
    return render_template('weather.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    success_message = ""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        cursor = mydb.cursor()
        cursor.execute('INSERT INTO contact_us (name, email, message) VALUES (%s, %s, %s)', (name, email, message))
        mydb.commit()
        cursor.close()
        success_message = "Your message was successfully submitted! We will get back to you soon."
        return render_template('contact.html', success=success_message)

    return render_template('contact.html')

def get_user_details(username):
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM user WHERE username = %s', (username,))
        user_details = cursor.fetchone()
        cursor.close()
        return user_details
def get_crop_details(c_id):
    cursor = mydb.cursor()
    cursor.execute('SELECT * FROM crop WHERE user_id = %s', (c_id,))
    crop_details = cursor.fetchall()
    cursor.close()
    return crop_details
def get_fertilizer_details(c_id):
    cursor = mydb.cursor()
    cursor.execute('SELECT * FROM fert WHERE user_id = %s', (c_id,))
    fertilizer_details = cursor.fetchall()
    cursor.close()
    return fertilizer_details
def get_disease_details(c_id):
    cursor = mydb.cursor()
    cursor.execute('SELECT * FROM disease WHERE user_id = %s', (c_id,))
    disease_details = cursor.fetchall()
    cursor.close()
    return disease_details


@app.route('/tracker',methods=['GET', 'POST'])
def tracker():
    if request.method == 'POST':

        rating = request.form.get('rating')
        review = request.form.get('review')
        crop_id = request.form.get('crop_id')
        review_type = request.form.get('type')
        if review_type=="crop":
            cursor = mydb.cursor()
            cursor.execute("UPDATE crop SET rating = %s, review = %s WHERE idc = %s", (rating, review, crop_id))
            mydb.commit()
            cursor.close() 
        else:
            cursor = mydb.cursor()
            cursor.execute("UPDATE fert SET rating = %s, review = %s WHERE id = %s", (rating, review, crop_id))
            mydb.commit()
            cursor.close() 


    if 'loggedin' in session and session['loggedin']:
        user_details = get_user_details(session['username'])
        c_id = user_details[0]
        crop_details = get_crop_details(c_id)
        fert_details = get_fertilizer_details(c_id)
        dis_details = get_disease_details(c_id)


        
        return render_template('tracker.html', user_details=user_details, crop_details=crop_details, fert_details=fert_details, dis_details=dis_details)
    else:
        return render_template('tracker.html', user_details=None, crop_details=None, fert_details=None, dis_details=None)



@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            input_data = request.json
            n = input_data.get('n')
            p = input_data.get('p')
            k = input_data.get('k')
            temperature = input_data.get('temperature')
            humidity = input_data.get('humidity')
            ph = input_data.get('ph')
            rainfall = input_data.get('rainfall')
            user_input = [[n, p, k, temperature, humidity, ph, rainfall]]
            prediction = model.predict(user_input)
            
            if 'loggedin' in session and session['loggedin']:
                user_details = get_user_details(session['username'])
                usid = user_details[0]
                cursor = mydb.cursor()
                input_str = f'n: {n}, p: {p}, k: {k}, temperature: {temperature}, humidity: {humidity}, ph: {ph}, rainfall: {rainfall}'
                prediction_str = str(prediction[0])
                cursor.execute('INSERT INTO crop (user_id, date, input, prediction, rating, review) VALUES (%s, %s, %s, %s, %s, %s)', (usid,datetime.datetime.now(),input_str,prediction_str,None,None))
                mydb.commit()
                cursor.close()   

            return jsonify({'prediction': prediction[0]})
        except Exception as e:
            return jsonify({'error': str(e)})

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Vamsi@18",
    database="test"
)

@app.route('/fpredict', methods=['POST'])
def fpredict():
    print("hi")
    if request.method == 'POST':
        try:
            input_data = request.json
            temperature = input_data.get('temperature')
            humidity = input_data.get('humidity')
            moisture = input_data.get('moisture')
            nitrogen = input_data.get('nitrogen')
            potassium = input_data.get('potassium')
            phosphorous = input_data.get('phosphorous')
            soil_num = input_data.get('Soil_Num')
            crop_num = input_data.get('Crop_Num') 
            user_input = [temperature, humidity, moisture, nitrogen, potassium, phosphorous, soil_num, crop_num]
            # Assuming fmodel is a valid model with a predict method
            prediction = fmodel.predict([user_input])
            mydb1 = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Vamsi@18",
                database="test"
            )

            fertilizer_name = prediction[0]
            benefits = fertilizer_benefits.get(fertilizer_name, ["No information available"])
                
                
            if 'loggedin' in session and session['loggedin']:
                user_details = get_user_details(session['username'])
                usid = user_details[0]
                input_str = f'Temperature: {temperature}, Humidity: {humidity}, Moisture: {moisture}, Nitrogen: {nitrogen}, Potassium: {potassium}, Phosphorous: {phosphorous}, Soil Number: {soil_num}, Crop Number: {crop_num}'
                prediction_str = fertilizer_name
                cursor = mydb1.cursor()
                cursor.execute('INSERT INTO fert (user_id, date, input, prediction, rating, review) VALUES (%s, %s, %s, %s, %s, %s)', (usid,datetime.datetime.now(),input_str,prediction_str,None,None))
                mydb1.commit()
                cursor.close()  

                return jsonify({'prediction': fertilizer_name, 'benefits': benefits})
            else:
                return jsonify({'error': 'Invalid prediction result'})
        except Exception as e:
            print(e)
            return jsonify({'error': str(e)})




@app.route('/detect', methods=['POST'])
def detect():
    if 'plant-image' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['plant-image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file:
        try:
            img = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
            img_resize = cv2.resize(img, (200, 200))
            img_array = np.array(img_resize) / 255.0
            img_array = img_array.reshape((1, 200, 200, 3)) 
            prediction = dmodel.predict(img_array)
            predicted_class_index = np.argmax(prediction)
            predicted_class_name = disease_classes[predicted_class_index]
            supplement_info = supplement_data[supplement_data['disease_name'].str.lower() == predicted_class_name.lower()]
            if not supplement_info.empty:
                supplement_name = supplement_info['supplement name'].iloc[0]
                description = supplement_info['description'].iloc[0]
                possible_steps = supplement_info['Possible Steps'].iloc[0]
                response = {
                    'diseaseName': predicted_class_name,
                    'supplementName': supplement_name,
                    'description': description,
                    'possibleSteps': possible_steps
                }
            else:
                response = {
                    'diseaseName': predicted_class_name,
                    'supplementName': 'Not found',
                    'description': 'No description available',
                    'possibleSteps': 'No steps available'
                }

            if 'loggedin' in session and session['loggedin']:
                user_details = get_user_details(session['username'])
                usid = user_details[0]
                cursor = mydb.cursor()
                input = file.read()
                print(input)
                prediction_str = predicted_class_name
                supplement_str = supplement_name
                cursor.execute('INSERT INTO disease (user_id, date, image, prediction, supplement, rating, review) VALUES (%s, %s, %s, %s, %s, %s, %s)', (usid,datetime.datetime.now(),input,prediction_str,supplement_str,None,None))
                mydb.commit()
                cursor.close()  

            return jsonify(response)  
        except Exception as e:
            response = {'error': str(e)}
            return jsonify(response)  
    else:
        return jsonify({'error': 'File processing error'})  

API_KEY = '70ba8ab48c1ba884626a740954b8258b'

@app.route('/get-weather', methods=['GET'])
def get_weather():
    city = request.args.get('city', 'London')  # Default to London if no city is provided
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric'
    response = requests.get(url)
    if response.ok:
        data = response.json()
        today_weather = data['list'][0]
        tomorrow_weather = data['list'][8]

        weather_info = {
            'today': {
                'temperature': today_weather['main']['temp'],
                'rainfall': today_weather.get('rain', {}).get('3h', 0),
                'humidity': today_weather['main']['humidity'],
                'pressure': today_weather['main']['pressure']
            },
            'tomorrow': {
                'temperature': tomorrow_weather['main']['temp'],
                'rainfall': tomorrow_weather.get('rain', {}).get('3h', 0),
                'humidity': tomorrow_weather['main']['humidity'],
                'pressure': tomorrow_weather['main']['pressure']
            }
        }
        return jsonify(weather_info)
    else:
        return jsonify({'error': 'Failed to fetch weather data'})

@app.route('/get-weather-by-coords', methods=['GET'])
def get_weather_by_coords():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    if lat and lon:
        url = f'http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
        response = requests.get(url)
        if response.ok:
            data = response.json()
            today_weather = data['list'][0]
            tomorrow_weather = data['list'][8]

            weather_info = {
                'today': {
                    'temperature': today_weather['main']['temp'],
                    'rainfall': today_weather.get('rain', {}).get('3h', 0),
                    'humidity': today_weather['main']['humidity'],
                    'pressure': today_weather['main']['pressure']
                },
                'tomorrow': {
                    'temperature': tomorrow_weather['main']['temp'],
                    'rainfall': tomorrow_weather.get('rain', {}).get('3h', 0),
                    'humidity': tomorrow_weather['main']['humidity'],
                    'pressure': tomorrow_weather['main']['pressure']
                }
            }
            return jsonify(weather_info)
        else:
            return jsonify({'error': 'Failed to fetch weather data'})
    else:
        return jsonify({'error': 'Latitude and longitude required'})


if __name__ == '__main__':
    app.secret_key = 'super'
    app.run(debug=True)

