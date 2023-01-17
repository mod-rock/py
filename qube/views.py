from flask import Blueprint, render_template, request
import json
import os
import pandas as pd
from werkzeug.utils import secure_filename

views = Blueprint(__name__,"views")

@views.route("/")
def home():
    
    return render_template('index.html')


@views.route("/optimise", methods=['POST'])
def optimisation():
    payload = request.form['payload']
    loaded = json.loads(payload)
    def test(contracts):
        df = pd.DataFrame(contracts)
        df['rates'] = df.price / df['duration']
        
        startContract = pd.DataFrame(df.loc[df.loc[df.start == 0]['rates'].idxmax()]).T
        endContract = pd.DataFrame(df.loc[df.loc[df.start == int(startContract.duration)]['rates'].idxmax()]).T
        
        totalProfit = int(startContract.price) + int(endContract.price)
        
        path = pd.concat([startContract, endContract])['name'].values.tolist()
        
        resultDict = {'income': totalProfit, 'path':path}
        
        return resultDict

    
    return test(loaded)
