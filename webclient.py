from flask import Flask, jsonify, render_template
from datetime import datetime
import requests
import urllib.request
from bs4 import BeautifulSoup
import json
import pymysql

app = Flask(__name__)


import logging
from logging.handlers import RotatingFileHandler


app.logger.setLevel(logging.ERROR)


log_file = 'error.log'
handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=1)


formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
)
handler.setFormatter(formatter)


app.logger.addHandler(handler)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_data')
def update_data():
    try:
        web_server_url = "http://192.168.24.250:80"

        response = requests.get(web_server_url)
        response.raise_for_status() 
        data = response.text

        response_dict = json.loads(data)
        ip_address = response_dict.get('ip_address', '')
        temperature_text = f"Temperature: {round(response_dict.get('temperature_celsius', ''), 2)}C ({round(response_dict.get('temperature_fahrenheit', ''), 2)}F)"
        temperature_text_only_value = f"{round(response_dict.get('temperature_celsius', ''), 2)}C ({round(response_dict.get('temperature_fahrenheit', ''), 2)}F)"

        api = 'https://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp'
        urls = urllib.request.urlopen(api).read()
        soup = BeautifulSoup(urls, "html.parser")
        tmin = soup.find_all("tmn")
        tmax = soup.find_all("tmx")
        yyyymmdd = soup.find_all("tmef")

        incheon_temperature_text = f'City: Incheon, Min temp.: {tmin[1 * 13].string}C, Max temp.: {tmax[1 * 13].string}C\nDates (Midterm forecast): {yyyymmdd[1 * 13].string}'

        db_config = {
            'host': '127.0.0.1',
            'user': 'root',
            'password': '895029Qaz!',
            'database': 'soloDB'
        }

        db_connection = pymysql.connect(**db_config)
        db_cursor = db_connection.cursor()

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = "INSERT INTO temperature_data (ip_address, temperature_celsius, temperature_fahrenheit, incheon_min_temp, incheon_max_temp, date) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (ip_address, response_dict.get('temperature_celsius', ''), response_dict.get('temperature_fahrenheit', ''),
                  float(tmin[1 * 13].string), float(tmax[1 * 13].string), current_time)
        db_cursor.execute(query, values)
        db_connection.commit()

        db_cursor.execute("SELECT temperature_celsius, date FROM temperature_data")
        result = db_cursor.fetchall()
        temperatures = [float(row[0]) for row in result]
        dates = [row[1] for row in result]
        db_connection.close()

       
        return jsonify({
            'ip_address': ip_address,
            'temperature_text': temperature_text_only_value,
            'incheon_temperature_text': incheon_temperature_text,
            'temperatures': temperatures,
            'dates': dates
        })
    except Exception as e:
       
        app.logger.error("Error occurred in 'update_data' function: %s", e)
        return jsonify({'error': 'An error occurred while processing the request.'}), 500

if __name__ == '__main__':
    app.debug = True
    app.run()