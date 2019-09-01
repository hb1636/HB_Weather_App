import requests
from datetime import datetime
from flask import Flask, render_template, request, flash, redirect, url_for
import sqlite3 as sql

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisissecret'

key = "3060a25c9ba504e833216bfb5040f5ed"


def fetch_weather_data(city):
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid={}'
    r = requests.get(url.format(city, "3060a25c9ba504e833216bfb5040f5ed")).json()
    return r

@app.route('/')
def get_data():

    db = sql.connect("cities.db")
    cursor = db.cursor()
    cursor.execute("select * from city")
    city_list = [city[0] for city in cursor.fetchall()]
    print(city_list)
    cursor.close()
    db.close()

    weather_data = []

    for city in city_list:
        r = fetch_weather_data(city)
        print(r)
        d_sunrise = datetime.fromtimestamp(r['sys']['sunrise'])
        d_sunrise = d_sunrise.strftime("%I:%H")
        d_sunset = datetime.fromtimestamp(r['sys']['sunset'])
        d_sunset = d_sunset.strftime("%I:%H")
        temperature = int((r['main']['temp'] -32)* 5//9)
        weather = {
            'city': city,
            'country': r['sys']['country'],
            'sunrise': d_sunrise,
            'sunset': d_sunset,
            'temperature': temperature,
            'pressure': r['main']['pressure'],
            'humidity': r['main']['humidity'],
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon'],
            'cod': r['cod']
        }
        weather_data.append(weather)
        print(weather_data)

    return render_template('weather.html', weather_data=weather_data)


@app.route('/', methods=['POST'])
def index():
    db = sql.connect("cities.db")
    cursor = db.cursor()
    err_msg = ''
    if request.method == 'POST':
        new_city = request.form.get('city')
        cursor.execute("select * from city")
        cities = [city[0] for city in cursor.fetchall()]
        city_data = fetch_weather_data(new_city)

        if new_city and new_city not in cities:

            if city_data['cod'] == 200:
                cursor.execute(f"insert into city values('{new_city}')")
                db.commit()
            else:
                err_msg = "This city does not exist in this World!"
        else:
            err_msg = "This city already exists in the Database!"

    cursor.close()
    db.close()

    print(err_msg)
    if err_msg:
        flash(err_msg, "error")
    else:
        flash("City added successfully!")

    return redirect(url_for('get_data'))

@app.route("/delete/<name>")
def delete_city(name):
    db = sql.connect("cities.db")
    cursor = db.cursor()
    cursor.execute(f'select * from city where name="{name}"')
    cursor.execute(f'delete from city where name="{name}"')
    db.commit()
    cursor.close()
    db.close()

    flash(f"Successfully Deleted {name}!", "success")
    return redirect(url_for("get_data"))

if __name__ == "__main__":
    app.run("localhost", 8088, debug=True)
