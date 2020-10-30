# covid19-new-cases-time-constant
Quick and dirty script that plots the Covid-19 new cases time constant.
Just `pip install pandas matplotib` and run the script.

Without downloading the script: `curl https://raw.githubusercontent.com/tovam/covid19-new-cases-time-constant/master/covid19-time-constant.py | python -`

The output is the path of the written PNG file.

# Data

By default it uses the France data from https://raw.githubusercontent.com/opencovid19-fr/data/master/dist/chiffres-cles.csv

You can use whatever data you want by changing the `get_formatted_data` argument of the `plot_graph` function.
