from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests


def unique_list(lst: list) -> list:
    unique = []
    for i in lst:
        if i not in unique:
            unique.append(i)
    return unique


# ************************ Configurations ******************************

# Creating Flask instance
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = '132knj12jb34b3k495uhfnfwjbr3ub532'

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app=app)


# **************************** Models ***********************************

class City(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255), nullable=False)


# *********************** Route / Endpoint *****************************

@app.route('/', methods=['GET', 'POST'])
def index():  # put application's code here
    cities = City.query.all()

    if request.method == 'POST':
        if request.form.get('city'):
            new_city = City(name=request.form.get('city'))
            if new_city not in cities:
                db.session.add(new_city)
                db.session.commit()
        else:
            flash('Enter the city!')
    weather_data = []

    for city in cities:
        r = requests.get(
            url=f'https://api.weatherapi.com/v1/current.json?key=e49bd23d074d4f79917143408231002&q={city.name}&aqi=yes')
        content = r.json()
        weather = {
            'city': city.name,
            'temp_c': content['current']['temp_c'],
            'temp_f': content['current']['temp_f'],
            'text': content['current']['condition']['text'],
            'icon': content['current']['condition']['icon'],
            'country': content['location']['country']
        }
        weather_data.append(weather)

    weather_data = unique_list(weather_data)
    return render_template('weather.html', weather_data=weather_data)


@app.route('/delete/<name>', methods=['GET', 'POST'])
def delete_city(name):
    City.query.filter_by(name=name).delete()
    db.session.commit()

    return redirect(url_for('index'))


# *************************** Run App **********************************

if __name__ == '__main__':
    app.run()
