import time
import redis
from flask import Flask, render_template
import os
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv() 
#print(os.getenv('REDIS_HOST'))

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
df = pd.read_csv('./TitanicTrain.csv') 

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
    filename = 'bar_chart.png'
    plt.savefig('static/' + filename)
    return filename


@app.route('/')
def hello():
    count = get_hit_count()
    return render_template('hello.html', name= "BIPM", count = count)

@app.route('/titanic')
def titanic():
    bar_chart = generate_bar_chart()
    return render_template('titanic.html', name = "titanic", bar_chart = bar_chart, chart_image='bar_chart.png')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)