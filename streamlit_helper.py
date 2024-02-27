import json
import logging
import streamlit as st
import vwlogger

from vwlogger import trace
from vwlogger import performance
from typing import Final
from streamlit_handlers import stCanvasHandler

CONST_VER                   	: Final[str]  = '1.5'

CONST_CFG_APP_LANG 				:Final[str] = "en"
CONST_CFG_APP_TITLE 			:Final[str] = "title"
CONST_CFG_APP_SUBTITLE			:Final[str] = "subheader"
CONST_CFG_APP_SITE 				:Final[str] = "Site"
CONST_CFG_APP_CONTAINERS 		:Final[str] = "Containers"
CONST_CFG_APP_CONTAINERS_ID		:Final[str] = "id"
CONST_CFG_APP_CONTAINERS_HEIGHT	:Final[str] = "height"
CONST_CFG_APP_CONTAINERS_BORDER	:Final[str] = "border"
CONST_CFG_APP_CONTAINERS_TXT    :Final[str] = "txt"
CONST_CFG_APP_SIDEBAR    		:Final[str] = "Sidebar"
CONST_CFG_APP_SIDEBAR_CONTENTS  :Final[str] = "Contents"
CONST_CFG_NONE 					:Final[str] = ""
CONST_CFG_APP_IMG				:Final[str] = "img"
CONST_CFG_APP_PAGEICON			:Final[str] = "pageIcon"
CONST_CFG_APP_LAYOUT			:Final[str] = "layout"
CONST_CFG_APP_MI_ABOUT			:Final[str] = "about"
CONST_CFG_APP_MI_REPORT			:Final[str] = "reportUrl"
CONST_CFG_APP_MI_SUPPORT		:Final[str] = "helpUrl"
CONST_CFG_APP_INITIALSIDEBAR    :Final[str] = "initialSidebarState"
CONST_CFG_APP_COLS				:Final[str] = "Columns"
CONST_CFG_APP_ROWS				:Final[str] = "Rows"
CONST_CFG_NOTDEFINED 			:Final[str] = "** NOT DEFINED **"
CONST_CFG_BLANK 				:Final[str] = ""
CONST_CFG_APP_SIDEBAR_DEF		:Final[str] = "expanded"
CONST_ST_MENUITEM_GETHELP		:Final[str] = "Get Help"
CONST_ST_MENUITEM_REPORTBUG		:Final[str] = "Report a Bug"
CONST_ST_MENUITEM_ABOUT			:Final[str] = "About"

CONST_ERROR_STR					:Final[str] = "!!Exception!!"
CONST_WARN_STR					:Final[str] = "--WARNING--"


g_dataSources = {}
g_canvasResource={}

def version() : 
    print(f"{version.__module__}.{version.__name__}:{CONST_VER}")


@performance
@trace
def addDataSource( name : str , val ) -> bool :
	try:
		if name in g_dataSources:
			logging.error(f"duplicate name by {name} in data source dict...")
			return False

		g_dataSources[name] = val
		return True
	except Exception as err:
		logging.error(f"{err} - name:{name}")
		return False



@performance
@trace
def addCanvasResource( name : str , val ) -> bool :
	try:
		if name in g_canvasResource:
			logging.error(f"duplicate name by {name} in canvas resource dict...")
			return False

		g_canvasResource[name] = val
		return True
	except Exception as err:
		logging.error(f"{err} - name:{name}")
		return False


@performance
@trace
def appOptions( configuration : dict, e : str,default=CONST_CFG_NONE, lang : str =  CONST_CFG_APP_LANG) -> str: 
    try:
       return configuration[lang][e]
    except Exception:
        logging.warning(f"lang:{lang} element:{e} default: {default} applied")
        return default

@performance
@trace
def siteOptions( configuration : dict, e : str,default=CONST_CFG_NONE, lang : str =  CONST_CFG_APP_LANG) -> str:
    try:
        return configuration[lang][CONST_CFG_APP_SITE][e]
    except Exception:
        logging.warning(f"lang:{lang} element:{e} default: {default} applied")
        return default

@performance
@trace
def columnOptions ( configuration : dict, e : str, idx = 0, default=CONST_CFG_NONE, lang : str = CONST_CFG_APP_LANG) -> str:
    try:
        return configuration[lang][CONST_CFG_APP_SITE][CONST_CFG_APP_COLS][idx][e]
    except Exception:
        logging.warning(f"lang:{lang} idx:{idx} element:{e} default: {default} applied")
        return default

@performance
@trace
def rowOptions ( configuration : dict, e : str, colIdx = 0, idx=0, default=CONST_CFG_NONE, lang : str = CONST_CFG_APP_LANG) -> str:
    try:
        return configuration[lang][CONST_CFG_APP_SITE][CONST_CFG_APP_COLS][colIdx][CONST_CFG_APP_ROWS][idx][e]
    except Exception:
        logging.warning(f"lang:{lang} colIdx:{colIdx} rowIdx:{idx} element:{e} default: {default} applied")
        return default

@performance
@trace
def containerOptions ( configuration : dict, e : str, colIdx = 0, rIdx=0, idx=0, default=CONST_CFG_NONE, lang : str = CONST_CFG_APP_LANG) -> str:
    try:
        return configuration[lang][CONST_CFG_APP_SITE][CONST_CFG_APP_COLS][colIdx][CONST_CFG_APP_ROWS][rIdx][CONST_CFG_APP_CONTAINERS][idx][e]
    except Exception:
        logging.warning(f"lang:{lang} colIdx:{colIdx} rowIdx:{rIdx} containerIdx:{idx} element:{e} default: {default} applied")
        return default

@performance
@trace
def uxInit( configuration : dict ) -> bool :
    try:
        st.set_page_config(page_title=appOptions(configuration,CONST_CFG_APP_TITLE),
        	               layout=appOptions(configuration,CONST_CFG_APP_LAYOUT), 
        	               page_icon=appOptions(configuration,CONST_CFG_APP_PAGEICON),
        	               initial_sidebar_state=appOptions(configuration,CONST_CFG_APP_INITIALSIDEBAR,CONST_CFG_APP_SIDEBAR_DEF),
        	               menu_items={
        	                 CONST_ST_MENUITEM_GETHELP : appOptions(configuration,CONST_CFG_APP_MI_SUPPORT,CONST_CFG_NOTDEFINED),
        	                 CONST_ST_MENUITEM_REPORTBUG : appOptions(configuration,CONST_CFG_APP_MI_SUPPORT,CONST_CFG_NOTDEFINED),
        	                 CONST_ST_MENUITEM_ABOUT : appOptions(configuration,CONST_CFG_APP_MI_ABOUT,CONST_CFG_NOTDEFINED),
        	               })
        st.title(appOptions(configuration,CONST_CFG_APP_TITLE))
        st.subheader(appOptions(configuration,CONST_CFG_APP_SUBTITLE))
    except Exception as err:
	    logging.error(err)
	    return False

@performance
@trace
def uxSidebar(configuration : dict) -> bool:
	bRet = False
	try:
		with st.sidebar:
			st.sidebar.header(siteOptions(configuration,CONST_CFG_APP_SIDEBAR,CONST_CFG_NOTDEFINED)[CONST_CFG_APP_TITLE])
			for sbContent in siteOptions(configuration,CONST_CFG_APP_SIDEBAR)[CONST_CFG_APP_SIDEBAR_CONTENTS]:
				st.write(sbContent[CONST_CFG_APP_CONTAINERS_TXT])

		bRet = True
	except Exception as err:
		logging.error(err)
	finally:
		return bRet


@performance
@trace
def uxCanvas( configuration : dict) -> bool:
	try:
		if ( 'canvas' not in configuration):
			logging.warning(f"skipping the canvas render for container id: {configuration['id']}")
			return False

		logging.info(f"render canvas as per configuration for container id: {configuration['id']}")
		canvas=g_canvasResource[configuration['canvas']];
		logging.info(f"loaded canvas {configuration['canvas']} : {canvas}")

		#
		# TODO - depending on the handler we want to call a func/strategy passing both the canvas and datasource
		# for now, we have implemented a very simple 'default
		df=None
		if 'data-source' in canvas :
			df=g_dataSources[canvas['data-source']]
			
		stCanvasHandler(canvas,df)
		return True
		
	except Exception as err:
		logging.error(err)
		return False


#hack - we want to reuse the def' for any container so we pass in the json relitive to the 'Containers'
# but we now want each container to reference a resource which are stored under 'Site. So, bit of a hack, but
# we get both passed in :( 
@performance
@trace
def uxContainer( fullConfiguration : dict, configuration : dict) -> dict :
	ux_containers = {}
	try:
		if (CONST_CFG_APP_CONTAINERS not in configuration):
			return ux_containers

		for container in configuration[CONST_CFG_APP_CONTAINERS]:	
			stContainer = st.container(border=container[CONST_CFG_APP_CONTAINERS_BORDER],height=container[CONST_CFG_APP_CONTAINERS_HEIGHT] )
			stContainer.write(container[CONST_CFG_APP_CONTAINERS_TXT])
			ux_containers[container[CONST_CFG_APP_CONTAINERS_ID]]=container
			uxCanvas(container)

	except Exception as err:
		logging.error(err)
	finally:
		return ux_containers

@performance
@trace
def uxRenderMatrix( configuration : dict) -> dict:
	ux_matrix={}
	try:
		ux_cols=st.columns(len(siteOptions(configuration,CONST_CFG_APP_COLS)))
		#DRY!!
		#TODO make this tidy 
		for i,c in enumerate(ux_cols):
			with c:
				st.header(columnOptions(configuration,CONST_CFG_APP_TITLE,i,CONST_CFG_BLANK))
				st.subheader(columnOptions(configuration,CONST_CFG_APP_SUBTITLE,i,CONST_CFG_BLANK))
				if (columnOptions(configuration,CONST_CFG_APP_IMG,i,CONST_CFG_BLANK)) != CONST_CFG_BLANK:
					st.image(columnOptions(configuration,CONST_CFG_APP_IMG,i,CONST_CFG_BLANK))
				c.write(columnOptions(configuration,CONST_CFG_APP_CONTAINERS_TXT,i,CONST_CFG_BLANK))
				uxContainer(configuration,configuration[CONST_CFG_APP_LANG][CONST_CFG_APP_SITE][CONST_CFG_APP_COLS][i])
				ux_rows=st.columns(len(siteOptions(configuration,CONST_CFG_APP_COLS)[i][CONST_CFG_APP_ROWS]))
				
				for j,r in enumerate(ux_rows):
					with r:
						st.header(rowOptions(configuration,CONST_CFG_APP_TITLE,i,j,CONST_CFG_BLANK))
						st.subheader(rowOptions(configuration,CONST_CFG_APP_SUBTITLE,i,j,CONST_CFG_BLANK))
						if (rowOptions(configuration,CONST_CFG_APP_IMG,i,j,CONST_CFG_BLANK)) != CONST_CFG_BLANK:
							st.image(rowOptions(configuration,CONST_CFG_APP_IMG,i,j,CONST_CFG_BLANK))
						r.write(rowOptions(configuration,CONST_CFG_APP_CONTAINERS_TXT,i,j,CONST_CFG_BLANK))
						uxContainer(configuration,configuration[CONST_CFG_APP_LANG][CONST_CFG_APP_SITE][CONST_CFG_APP_COLS][i][CONST_CFG_APP_ROWS][j]) 
					
			
	except Exception as err:
		logging.error(err)
	finally:
		return ux_matrix


# ----------------------------------------------------------------
# ----------------------------------------------------------------
# ----------------------------------------------------------------
version()
