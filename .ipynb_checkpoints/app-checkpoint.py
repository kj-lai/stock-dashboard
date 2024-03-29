from flask import *
from app_func import show_tables, plot_tables
import io
import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

date = ' [2020-07-17]'

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/')
def mainpage():
	return render_template('mainpage.html')

@app.route('/', methods=['POST'])
def display():
	# code   = request.form['code']
	code   = request.form.get('code')
	ticker = request.form.get('ticker')

	if len(code)!=0 and len(ticker)!=0:
		return render_template('input-error.html')
	elif len(code)!=0:
		value  = code.zfill(4)
		market = 'klse'
	elif len(ticker)!=0:
		value  = ticker.upper()
		market = 'nyse'
	else:
		return render_template('mainpage.html')

	table1_1, table1_2, table1_3, table1_4, table1_5, table2, graph1, graph2, graph3 = show_tables(value, market)

	if type(table1_1) == str:
		return render_template('stock-not-found.html')
	else:
		title1     = 'Stock Details: '+str(value)+' - '+str(table1_1.name.values[0])+date
		title2     = 'Stock Growth'
		title3     = 'Stock Filter'
		title4     = '3G2H Score Breakup'
		title5     = 'Past 10 Years Financials'
		save_file1 = './static/images/graph_'+str(value)+'_01.png'
		save_file2 = './static/images/graph_'+str(value)+'_02.png'
		save_file3 = './static/images/graph_'+str(value)+'_03.png'

		graph1.savefig(save_file1, bbox_inches='tight', pad_inches=0.1)
		graph2.savefig(save_file2, bbox_inches='tight', pad_inches=0.1)
		graph3.savefig(save_file3, bbox_inches='tight', pad_inches=0.1)

		return render_template('dashboard.html',
							   tables=[table1_1.to_html(table_id='table1', index=False),
									   table1_2.iloc[:, :14].to_html(table_id='table2', index=False), 
									   table1_2.iloc[:, 14:].to_html(table_id='table3', index=False),
									   table1_3.to_html(table_id='table4', index=False),
									   table1_4.to_html(table_id='table5', index=False),
									   table1_5.to_html(table_id='table6', index=False),
									   table2.to_html(table_id='table7', index=False)],
							   titles = [title1, title2, title3, title4, title5],
							   images = [save_file1, save_file2, save_file3])
if __name__ == '__main__':
	app.run(debug=True)
