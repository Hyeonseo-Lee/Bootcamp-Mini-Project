import requests
import tkinter as tk
import urllib.request
from bs4 import BeautifulSoup
import json
import pymysql
import matplotlib.pyplot as plt
from datetime import datetime

def update_labels():
    web_server_url = "http://192.168.0.9:80"

    response = requests.get(web_server_url)
    data = response.text

    response_dict = json.loads(data)
    ip_address = response_dict.get('ip_address', '')
    lbl_ip.config(text=f"IP address: {ip_address}")
    lbl_temperature.config(
        text=f"Temperature : {round(response_dict.get('temperature_celsius', ''), 2)}C ({round(response_dict.get('temperature_fahrenheit', ''), 2)}F)")

    api = 'https://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp'
    urls = urllib.request.urlopen(api).read()
    soup = BeautifulSoup(urls, "html.parser")
    tmin = soup.find_all("tmn")
    tmax = soup.find_all("tmx")
    yyyymmdd = soup.find_all("tmef")

    lbl_incheon_temperature.config(
        text=f'City : Incheon, Min temp. : {tmin[1 * 13].string}C, Max temp. : {tmax[1 * 13].string}C\nDates(Midterm forecast) : {yyyymmdd[1 * 13].string}')

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

    db_cursor.execute("SELECT * FROM temperature_data")
    result = db_cursor.fetchall()
    for row in result:
        print(row)

    db_connection.close()

def show_temperature_graph():
    db_config = {
        'host': '127.0.0.1',
        'user': 'root',
        'password': '895029Qaz!',
        'database': 'soloDB'
    }

    db_connection = pymysql.connect(**db_config)
    db_cursor = db_connection.cursor()

    db_cursor.execute("SELECT temperature_celsius, date FROM temperature_data")
    result = db_cursor.fetchall()

    temperatures = [float(row[0]) for row in result]
    dates = [row[1] for row in result]

    plt.figure()
    plt.plot(dates, temperatures, marker='o')
    plt.xlabel("Date")
    plt.ylabel("Temperature (Celsius)")
    plt.title("Temperature Data")
    plt.xticks(rotation=45)  
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    db_connection.close()

def update_datetime():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lbl_datetime.config(text=f"Current Time: {current_time}")
    current_temperature_condition.after(1000, update_datetime)

current_temperature_condition = tk.Tk()
current_temperature_condition.title("Inha Smart Factory!")
current_temperature_condition.geometry("400x200")

lbl_ip = tk.Label(current_temperature_condition, text="IP address: ")
lbl_temperature = tk.Label(current_temperature_condition, text="")
lbl_incheon_temperature = tk.Label(
    current_temperature_condition, text="city/min/max")
lbl_datetime = tk.Label(current_temperature_condition, text="Current Time: ")

btn_check_temperature = tk.Button(
    current_temperature_condition, text="Check Temperature!", command=update_labels)

btn_show_graph = tk.Button(
    current_temperature_condition, text="Show Temperature Graph!", command=show_temperature_graph)

lbl_ip.grid(row=0, column=0)
lbl_temperature.grid(row=0, column=1)
lbl_incheon_temperature.grid(row=1, column=0, columnspan=2, sticky=tk.EW)
lbl_datetime.grid(row=2, column=0, columnspan=2, sticky=tk.EW)
btn_check_temperature.grid(row=3, column=0, columnspan=2, sticky=tk.EW)
btn_show_graph.grid(row=4, column=0, columnspan=2, sticky=tk.EW)

update_datetime()
current_temperature_condition.mainloop()
