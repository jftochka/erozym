from flask import Flask, render_template, request
from flask_assets import Environment, Bundle

# from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
assets = Environment(app)

js = Bundle('jquery.js', 'base.js', 'widgets.js',
            filters='jsmin', output='gen/packed.js')
assets.register('js_all', js)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contacts')
def about():
    return render_template('contacts.html')

@app.route('/e-pidtrymka')
def epidtr():
    return render_template('e-pidtrymka.html')

@app.route('/vacancy')
def vacancy():
    return render_template('vacancy.html')

@app.route('/ukrainska-mova-i-literatura')
def ukrmovlit():
    return render_template('ukrainska-mova-i-literatura.html')

@app.route('/angliyska-mova')
def english():
    return render_template('angliyska-mova.html')

@app.route('/mathematika')
def mathematia():
    return render_template('mathematika.html')

@app.route('/istoriya-ukrainy')
def ukrhistory():
    return render_template('istoriya-ukrainy.html')

@app.route('/fizika')
def physics():
    return render_template('fizika.html')

@app.route('/himiya')
def chemistry():
    return render_template('himiya.html')

@app.route('/biologia')
def biology():
    return render_template('biologia.html')

@app.route('/geografia')
def geography():
    return render_template('geografia.html')

@app.route('/404')
def notfound():
    return render_template('/404.html')

@app.route('/tarifs')
def tarifs():
    return render_template('/tarifs.html')
    
if __name__ == "__main__":
    app.run()