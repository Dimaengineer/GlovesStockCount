from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def first_window():
    return render_template('first_window.html')

@app.route('/second_window')
def second_window():
    return render_template('second_window.html')

if __name__ == '__main__':
    app.run(debug=True)