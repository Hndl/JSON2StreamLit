import logging
import vwlogger
import json
import streamlit as st
import plotly.express as px

from typing import Final
from vwlogger import trace
from vwlogger import performance

CONST_VER 			: Final[str]	= '1.0'


def version() : 
	print(f"{version.__module__}.{version.__name__} {CONST_VER}")

@performance
@trace
def ch_g_voltage( canvas : dict, df ) -> bool:
	figX = px.line(df, y=["Voltage"])
	#figX = px.line(df, y=["Voltage","Relative-Humidity%","Ambient-Temperature(C)"])
	figX.add_hline(y=12.1, line_width=3, line_dash="dot", line_color="red",annotation_text="Min Voltage", annotation_position="bottom right",annotation_font_size=20,
              annotation_font_color="red")
	st.write(figX)
	return True

@performance
@trace
def ch_default_graph( canvas : dict, df ) -> bool:
	figX = px.line(df, y=[canvas['y']])
	st.write(figX)
	return True
@performance
@trace
def ch_default(canvas : dict, df) -> bool:
	st.write(df)
	return False

@performance
@trace
def stCanvasHandler( canvas : dict, df ) ->bool:
	bRet=False
	logging.info(f"determine handler for {canvas}")

	
	try:
		match canvas['handler'] :
			case 'default':
				bRet=ch_default( canvas, df )
			case 'default_graph':
				bRet=ch_default_graph( canvas, df)
			case 'g_voltage':
				bRet=ch_g_voltage( canvas, df )

		return bRet
		
	except Exception as err:
		logging.error(err)
		return bRet

def main():
	pass
# ----------------------------------------------------------------
# ----------------------------------------------------------------
# ----------------------------------------------------------------
version()
if __name__ == '__main__':
	main()
