import time
import redis
from flask import Flask, render_template
import os
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt

load_dotenv() 
cache = redis.Redis(host=os.getenv('REDIS_HOST'), port=6379,  password=os.getenv('REDIS_PASSWORD'))
app = Flask(__name__)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


# read CSV data into a DataFrame
df = pd.read_csv('C:/Users/joana/mydockerfolder/app/TitanicTrain.csv') 
# generate an HTML table from the DataFrame
html_table = df.to_html()

def generate_bar_chart():
    survived = df.groupby(['Sex', 'Survived'])['Survived'].count().unstack()
    survived.plot(kind='bar', stacked=True)
    plt.title('Survival by Gender')
    plt.xlabel('Gender')
    plt.ylabel('Count')
    plt.legend(['Not Survived', 'Survived'])
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('static/bar_chart.png')


@app.route('/')
def hello():
    count = get_hit_count()
    return render_template('hello.html', name= "BIPM", count = count)

@app.route('/titanic')
def titanic():
    generate_bar_chart()
    return render_template('titanic.html', name = "titanic", chart_image='bar_chart.png')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)