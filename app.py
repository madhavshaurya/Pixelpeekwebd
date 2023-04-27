from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('Index1.html')

@app.route('/script1')
def run_script1():
    subprocess.call(['python', 'script1.py'])
    return 'Script 1 executed successfully!'

@app.route('/script2')
def run_script2():
    subprocess.call(['python', 'script2.py'])
    return 'Script 2 executed successfully!'

@app.route('/script3')
def run_script3():
    subprocess.call(['python', 'script3.py'])
    return 'Script 3 executed successfully!'

@app.route('/script4')
def run_script4():
    subprocess.call(['python', 'script4.py'])
    return 'Script 4 executed successfully!'

if __name__ == '__main__':
    app.run(debug=True)
