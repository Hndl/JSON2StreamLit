import logging
import vwlogger
import json
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import numpy as np
import pandas as pd

from plotly.subplots import make_subplots
from abc import ABC, abstractmethod
from typing import Final
from vwlogger import trace
from vwlogger import performance

CONST_VER 			: Final[str]	= '1.0'
CONST_UNDEFINED		: Final[str]	= 'undefined'
BLANK				: Final[str]	= ''




class CanvasPainter (ABC):

	@abstractmethod
	def render(self, df, st_hndl ) -> bool:
		pass
	@abstractmethod
	def prepare(self, df ) :
		pass

	def getOptBool( self,attr : str ) -> bool :
		return (attr in self.configuration)

	def getOptStr ( self,attr : str, default : str = None) -> str :
		return (default if attr not in self.configuration or len(self.configuration[attr])==0 else self.configuration[attr])

	def getOptInt ( self,attr : str, default : int = 0) -> int :
		return (default if attr not in self.configuration else int(self.configuration[attr]))

	def getTitle (self) -> str: 
		return ( self.getOptStr('title',None))

	def getSortColumnName (self) -> str :
		return (self.getOptStr('sortOnCol',None))

	def getSortAscending (self) -> str :
		return (self.getOptBool('sortAscending'))
		
	def getMaxRows(self ) -> int:
		return (self.getOptInt('head',0))

	def getHeight( self) -> int:
		return (self.getOptInt('height',0))

	def getWidth( self) -> int:
		return (self.getOptInt('width',0))

	def getX ( self ) -> str:
		return (self.getOptStr('x',None))

	def getXLabel ( self ) -> str:
		return (self.getOptStr('x-label',"Undefined"))

	def getYLabel ( self ) -> str:
		return (self.getOptStr('y-label',"Undefined"))

	def getY ( self ) -> str:
		return (self.getOptStr('y',None))
	

	@performance
	@trace
	def trimResultset (self, df ) :
		max_rows = self.getMaxRows()
		logging.info(f"trimming resultset, max rows {max_rows}")
		if( max_rows <= 0):
			return df

		return df.head(max_rows)

	def sortResultset ( self, df ) :
		sortCol = self.getSortColumnName ()
		sortAsc = self.getSortAscending()

		logging.info(f"Sort by {sortCol} ascending:{sortAsc}")

		if (sortCol == None):
			return df

		return (df.sort_values(by=[sortCol],ascending=sortAsc))

	def __init__ (self, configuration : dict):
		self.configuration = configuration
	
	def __str__(self) :
		return f'Canvas Painter of Type: {self.__class__}'

	


class BasicGraphPainter( CanvasPainter):
	def render(self, df, st_hndl  ):
		logging.info(self.configuration)
		if 'y' not in self.configuration:
			logging.error(f"canvas id:{self.configuration['id']} - is missing y attribute")
			st_hndl.write(f'<<Error - See Server Log - Error>>')
			return False
	
		figX = px.line(df, y=[self.configuration['y']])
		st_hndl.write(figX)
		return True

	def prepare( self, df ) : 
		return df

class DefaultPainter( CanvasPainter ):
	def render(self, df, st_hndl ):
		st_hndl.write(df)
		return True

	def prepare( self, df):
		return df


class WindGraphPainter( CanvasPainter ):

	def render(self, df, st_hndl ):
		"""Custom Handler of Name: 'g_wind'

    Parameters:
    	canvas  (dict)		: the JSON confguration.
    	df 		(DataFrame) : contains the data records.

    JSON Configurartion:
    	Canvas":
          	"id"				: str 	- unique name
         	"handler"			: str   - the name of the handler to invoke.   -> 'g_wind',
          	"data-source"		: str 	- the name of the data soure to consume. -> '...'
          	"head"				: int 	- The number of records once sorted to use. set to 0 if all records are required. -> 200
          	"windSpeedName" 	: str 	- The name of the field in the data frame containing the Wind Speed values. -> 'Wind Speed (m/s)''
          	"windSpeedLabel"	: str 	- Wind Speed label.	-> 'Wind Speed (m/s)'
          	"timeStampName" 	: str   - The name of the field in the data frame that contains the date time. -> 'Timestamp_UTC'
          	"timeStampLabel"	: str 	- The timestamp label.  ->'Date/Timestamp'
          	"windDirectionName" : str 	- The name of the field in the data frame that contains the Wind Direction_compass points. -> 'Wind Direction_compass points'
          	"windDirectionLabel": str 	- The Wind Direction label. -> 'Wind Direction'
          	"arrowColor" 		: str 	- The color of the arrows.  -> 'green'
          	"arrowSize" 		: int 	- The size of th wind direction arrows. -> 10 
          	"sortOnCol" 		: str 	- The field name to sort by.  -> 'Timestamp_UTC'
          	"width" 			: int 	- The width of the graph in pixles. -> 1200
          	"height"			: int 	- The hight of the graph in pixles. -> 450
          	"title" 			: str 	- The graph title. -> 'Wind Speed/Direction'

    Returns:
    	bool	:	Returning True if graph is rendered without exception, otherwise False.

	"""


		DATA_SET 		: Final[int] = 1
		Y_WIND_SPEED 	: Final[str] = 'windSpeedName'
		Y_WIND_DIR		: Final[str] = 'windDirectionName'
		Y_WIND_SPEEDLAB	: Final[str] = 'windSpeedLabel'
		Y_WIND_DIRLAB	: Final[str] = 'windDirectionLabel'
		X_TIME			: Final[str] = 'timeStampName'
		X_TIMELAB		: Final[str] = 'timeStampLabel'
		LEGEND			: Final[str] = 'legend'
		ARROW_COLOR     : Final[str] = 'arrowColor'
		ARROW_SIZE		: Final[str] = 'arrowSize'
		ARROW_COLOR_DEF : Final[str] = 'red'
		ARROW_ICON_DEF  : Final[str] = 'arrow'
		ARROW_SIZE_DEF	: Final[int] = 15
		
		colName_WindSpeed = self.getOptStr(Y_WIND_SPEED)
		colName_WindSpeedL= self.getOptStr(Y_WIND_SPEEDLAB)
		colName_WindDir   = self.getOptStr(Y_WIND_DIR)
		colName_WindDirL  = self.getOptStr(Y_WIND_DIRLAB)
		colName_Time	  = self.getOptStr(X_TIME)
		colName_TimeL	  = self.getOptStr(X_TIMELAB)
		gOpt_Legend		  = self.getOptBool(LEGEND)
		arrowColor		  = self.getOptStr(ARROW_COLOR,ARROW_COLOR_DEF)
		arrowSize 		  = self.getOptInt(ARROW_SIZE,ARROW_SIZE_DEF)
		

		figX = px.line(df,
						y=colName_WindSpeed, 
						x=colName_Time, 
						markers=True,
						width=self.getWidth() ,
						height=self.getHeight(), 
						labels={colName_WindSpeed:colName_WindSpeedL,
								colName_WindDir:colName_WindDirL, 
								colName_Time:colName_TimeL})

		# Add Arrow head to show wind direction.
		for wind_row in df.iterrows():
			figX.add_trace(
				go.Scatter(
					x=[wind_row[DATA_SET][colName_Time]],
					y=[wind_row[DATA_SET][colName_WindSpeed]],
					showlegend=gOpt_Legend,
					marker=dict(
					color=arrowColor,
						size=arrowSize,
						symbol=ARROW_ICON_DEF,
						angle=[wind_row[DATA_SET][colName_WindDir]],
					)))


		# Add figure title
		figX.update_layout(
		    title_text="                Wind Speed & Direction"
		)


		st_hndl.write(figX)
		return True

	def prepare(self, df) :
	
		try:
			IDX_DT_FORMAT : Final[str] = 'idx-field-date-format'
			X_TIME			: Final[str] = 'timeStampName'

			colName_Time  = self.getOptStr(X_TIME)
			idxDateFormat = self.getOptStr(IDX_DT_FORMAT)
			
			# Apply a format to the date/time field. Otherwise, it will be treated as int64.  Plotty autoformat work so much better
			# if the data type is defined......
			df[colName_Time] = pd.to_datetime(df[colName_Time], format=idxDateFormat)
			return (self.trimResultset(self.sortResultset(df)) )

		except Exception as err:
			logging.error(f'error was invoking Redox_Ph_GraphPainter.prepare method- {err}')
			raise ValueError(f'Redox_Ph_GraphPainter.prepare method failed! - possibly missing {IDX_DT_FORMAT}, {X_TIME} or field format not valid')



class X2YGraphPainter( CanvasPainter ):

	def render(self, df, st_hndl ):
		DATA_SET 		: Final[int] = 1
		X_TIME			: Final[str] = 'timeStampName'
		X_TIMELAB		: Final[str] = 'timeStampLabel'
		Y1              : Final[str] = 'y1'
		Y1NAME			: Final[str] = 'y1Name'
		Y2              : Final[str] = 'y2'
		Y2NAME			: Final[str] = 'y2Name'
		LEGEND			: Final[str] = 'legend'
		TITLE           : Final[str] = 'title'
		X               : Final[str] = 'x'
		XNAME			: Final[str] = 'xName'
		LEGEND			: Final[str] = 'legend'
		LEGEND_Y_ANC	: Final[str] = 'legend-y-anchor'
		LEGEND_X_ANC	: Final[str] = 'legend-x-anchor'
		LEGEND_Y		: Final[str] = 'legend-y'
		LEGEND_X		: Final[str] = 'legend-x'
                       

			
		colName_Time	  = self.getOptStr(X_TIME)
		colName_Y1	  	  = self.getOptStr(Y1)
		colName_Y1Name	  = self.getOptStr(Y1NAME)
		colName_Y2	  	  = self.getOptStr(Y2)
		colName_Y2Name	  = self.getOptStr(Y2NAME)
		colName_Title	  = self.getOptStr(TITLE)
		colName_X	 	  = self.getOptStr(X)
		colName_XName	  = self.getOptStr(XNAME)
				
		fig = make_subplots(specs=[[{"secondary_y": True}]])

		# Add traces
		fig.add_trace(
		    go.Scatter(x=df[colName_Time], y=df[colName_Y1], name=colName_Y1Name),
		    secondary_y=False,
		)
		fig.add_trace(
		    go.Scatter(x=df[colName_Time], y=df[colName_Y2], name=colName_Y2Name),
		    secondary_y=True,
		)

		if (colName_Title != BLANK) :
			fig.update_layout(title_text=colName_Title)

		if (colName_XName != BLANK) :
			fig.update_xaxes(title_text=colName_XName)

		# Set y-axes titles
		if (colName_Y1Name != BLANK) :
			fig.update_yaxes(title_text=colName_Y1Name, secondary_y=False)

		if (colName_Y2Name != BLANK) :
			fig.update_yaxes(title_text=colName_Y2Name, secondary_y=True)

		if ( self.getOptBool(LEGEND)==True ) :
			fig.update_layout(legend=dict(
	  			yanchor=self.getOptStr(LEGEND_Y_ANC),
	    		y=-self.getOptInt(LEGEND_Y),
	    		xanchor=self.getOptStr(LEGEND_X_ANC),
	    		x=-self.getOptInt(LEGEND_X)
			))

		# Update layout properties
		fig.update_layout(
    		width=self.getWidth(),
    		height=self.getHeight(),
    	)
		

		st_hndl.write(fig)
		return True
	def prepare(self, df) :

		try:
			IDX_DT_FORMAT : Final[str] = 'idx-field-date-format'
			X_TIME			: Final[str] = 'timeStampName'

			colName_Time  = self.getOptStr(X_TIME)
			idxDateFormat = self.getOptStr(IDX_DT_FORMAT)
			# Apply a format to the date/time field. Otherwise, it will be treated as int64.  Plotty autoformat work so much better
			# if the data type is defined......
			df[colName_Time] = pd.to_datetime(df[colName_Time], format=idxDateFormat)
			return (self.trimResultset(self.sortResultset(df)) )

		except Exception as err:
			logging.error(f'error was invoking X2YGraphPainter.prepare method- {err}')
			raise ValueError(f'X2YGraphPainter.prepare method failed! - possibly missing {IDX_DT_FORMAT}, {X_TIME} or field format not valid')



class VoltageGraphPainter( CanvasPainter ):

	def render(self, df, st_hndl ):
		"""Custom Handler of Name: 'g_voltage'

    Parameters:
    	df 		(DataFrame) : contains the data records.
		st.     (Streamlit Ref)

    JSON Configurartion:
    	Canvas":
          	"id"				: str 	- unique name
         	"handler"			: str   - the name of the handler to invoke.   -> 'g_wind',
          	"data-source"		: str 	- the name of the data soure to consume. -> '...'
          	"head"				: int 	- The number of records once sorted to use. set to 0 if all records are required. -> 200
          	"width" 			: int 	- The width of the graph in pixles. -> 1200
          	"height"			: int 	- The hight of the graph in pixles. -> 450
          	"title" 			: str 	- The graph title. -> 'Wind Speed/Direction'
          	"x"
          	"x-label"
          	"y"
          	"y-label"
          	"control-line-const-value"	: 4.2,
          	"control-line-width" 		: 2,
          	"control-line-color"		: "red",
          	"control-line-type" 		: "dot",
          	"control-line-txt"  		: "Min Voltage",
          	"control-line-txt-pos"  	: "bottom right",
          	"control-line-txt-size" 	: 10,
          	"control-line-txt-color" 	: "red"

    Returns:
    	bool	:	Returning True if graph is rendered without exception, otherwise False.

	"""
		figX = px.line(df, 
					y=[self.getY()],
					x=self.getX(),
					title=self.getTitle(),
					labels={self.getX():self.getXLabel(), self.getY():self.getYLabel()})

		figX.add_hline(y=self.getOptInt('control-line-const-value'), 
					   line_width=self.getOptInt('control-line-width',5), 
					   line_dash=self.getOptStr('control-line-type','line'), 
					   line_color=self.getOptStr('control-line-color','green'),
					   annotation_text=self.getOptStr("control-line-txt", "control-line-txt not set"),
					   annotation_position=self.getOptStr("control-line-txt-pos","bottom right"),
					   annotation_font_size=self.getOptInt('control-line-txt-size',60),
              			annotation_font_color=self.getOptStr('control-line-txt-color','green'))
	

		st_hndl.write(figX)
		
		return True

	def prepare(self, df) :
		return (self.trimResultset(self.sortResultset(df)) )


class GeoRandomPainter( CanvasPainter ):
	def render(self, df, st_hndl ):
		#54.991221, -2.360183
		chart_data = pd.DataFrame(
						np.random.randn(1000, 2) / [50, 50] + [54.991221, 2.360183],
						columns=['lat', 'lon'])

		st_hndl.pydeck_chart(pdk.Deck(
    		map_style=None,
    		initial_view_state=pdk.ViewState(
        							latitude=-54.991221,
        							longitude=-2.360183,
        							zoom=11,
        							pitch=50),
    		layers=[
       			pdk.Layer(
           			'HexagonLayer',
           			data=chart_data,
           			get_position='[lon, lat]',
           			radius=200,
           			elevation_scale=4,
           			elevation_range=[0, 1000],
           			pickable=True,
           			extruded=True,
        		),
        		pdk.Layer(
            		'ScatterplotLayer',
            		data=chart_data,
            		get_position='[lon, lat]',
            		get_color='[200, 30, 0, 160]',
            		get_radius=200,
        		),
    		],
		))


		return True

	def prepare( self, df):
		return df


class GeoSampleRandomPainter( CanvasPainter ):
	def render(self, df, st_hndl ):
		#54.991221, -2.360183
		#ignore the data frame passed in, just generate random data
		df = pd.DataFrame(
    	np.random.randn(1000, 2) / [50, 50] + [54.991221, -2.360183],
    	columns=['lat', 'lon'])
		st_hndl.map(df,size=20, color='#0044ff')

		return True

	def prepare( self, df):
		return df


class GuageSampleRandomPainter( CanvasPainter ):
	#https://plotly.com/python/reference/indicator/
	def render(self, df, st_hndl ):
		fig = go.Figure(go.Indicator(
		    mode = "gauge+number+delta",
		    value = 420,
		    domain = {'x': [0, 1], 'y': [0, 1]},
		    title = {'text': "Speed", 'font': {'size': 24}},
		    delta = {'reference': 400, 'increasing': {'color': "RebeccaPurple"}},
		    gauge = {
		        'axis': {'range': [None, 500], 'tickwidth': 1, 'tickcolor': "darkblue"},
		        'bar': {'color': "darkblue"},
		        'bgcolor': "white",
		        'borderwidth': 2,
		        'bordercolor': "gray",
		        'steps': [
		            {'range': [0, 250], 'color': 'cyan'},
		            {'range': [250, 400], 'color': 'royalblue'}],
		        'threshold': {
		            'line': {'color': "red", 'width': 4},
		            'thickness': 0.75,
		            'value': 490}}))
		

		fig.update_layout(paper_bgcolor = "lavender", height=220,width=150,font = {'color': "darkblue", 'family': "Arial"})
		
		fig2 = go.Figure(go.Indicator(
    		domain = {'x': [0, 1], 'y': [0, 1]},
		    value = 450,
		    mode = "gauge+number+delta",
		    title = {'text': "Speed"},
		    delta = {'reference': 380},
		    gauge = {'axis': {'range': [None, 500]},
		             'steps' : [
		                 {'range': [0, 250], 'color': "lightgray"},
		                 {'range': [250, 400], 'color': "gray"}],
		             'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 490}}))

		fig3 = go.Figure(go.Indicator(
		    mode = "gauge+number",
		    value = 270,
		    domain = {'x': [0, 1], 'y': [0, 1]},
		    title = {'text': "Speed"}))

		st_hndl.write(fig)
		#st_hndl.write(fig2)
		#st_hndl.write(fig3)
		return True

	def prepare( self, df):
		return df

@performance
@trace
def canvasPainterFactory ( painterName : str, configuration : dict ) -> CanvasPainter:

	availablePainters = {
		'default': DefaultPainter(configuration),
		'default_graph' : BasicGraphPainter(configuration),
		'g_voltage' : VoltageGraphPainter(configuration),
		'g_wind' : WindGraphPainter(configuration),
		'georandom' : GeoRandomPainter(configuration),
		'geosimplerando' : GeoSampleRandomPainter(configuration),
		'guageSamplerando' : GuageSampleRandomPainter(configuration),
		'x2y_graph' : X2YGraphPainter(configuration),
	}

	if painterName in availablePainters:
		logging.info(f"Painter of type {painterName} located in list of availablePainters")
		return availablePainters[painterName]

	logging.warning(f"Painter Class not found in list of availablePainters, default choosen")
	return availablePainters['default']


def version() : 
	print(f"{version.__module__}.{version.__name__} {CONST_VER}")

@performance
@trace
def stCanvasHandler( canvas : dict, df ) ->bool:
	
	logging.info(f"NEW Factory {canvas}")

	try:
		painter = canvasPainterFactory( canvas['handler'],canvas )
		logging.info(str(painter))
		df = painter.prepare(df)
		logging.info(df.dtypes)
		logging.info(df)
		painter.render(df, st)
		return True
	except Exception as err:
		logging.error(f'error was invoking canvas handler - {err}')
		return False

def main() -> int:
	logging.basicConfig(level=vwlogger.CONST_DEF_LOGLEVEL,format=vwlogger.CONST_LOGGING_FMT)
	painter = canvasPainterFactory('default', None)
	logging.info(f'{str(painter)}')
	painter = canvasPainterFactory('default_graph', None)
	logging.info(f'{str(painter)}')
	painter = canvasPainterFactory('g_voltage',None)
	logging.info(f'{str(painter)}')
	painter = canvasPainterFactory('g_wind',None)
	logging.info(f'{str(painter)}')

	return 0
# ----------------------------------------------------------------
# ----------------------------------------------------------------
# ----------------------------------------------------------------
version()
if __name__ == '__main__':
	main()
