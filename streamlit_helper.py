# Change History
# Who	When		What						Version
# ========================================================
# CB 	1/3/2024	See Below					1.7
# 					Ref: 001 : Corrected Containers.  'stuff' was being rendered outside the container
#					Ref: 002 : Added support for IMG tag in containers.
#					Ref: 003 : Added support for gap tag on columns

import json
import logging
import streamlit as st
import vwlogger
import base64

from vwlogger import trace
from vwlogger import performance
from typing import Final
from streamlit_handlers import stCanvasHandler

CONST_VER                   	: Final[str]  = '1.7'

CONST_CFG_APP_LANG 				:Final[str] = "en"
CONST_CFG_APP_CSS 				:Final[str] = "css"
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
CONST_CFG_APP_IMG				:Final[str] = "img"
CONST_CFG_APP_GAP				:Final[str] = "gap"
CONST_CFG_APP_PAGEICON			:Final[str] = "pageIcon"
CONST_CFG_APP_LAYOUT			:Final[str] = "layout"
CONST_CFG_APP_MI_ABOUT			:Final[str] = "about"
CONST_CFG_APP_MI_REPORT			:Final[str] = "reportUrl"
CONST_CFG_APP_MI_SUPPORT		:Final[str] = "helpUrl"
CONST_CFG_APP_INITIALSIDEBAR    :Final[str] = "initialSidebarState"
CONST_CFG_APP_COLS				:Final[str] = "Columns"
CONST_CFG_APP_ROWS				:Final[str] = "Rows"
CONST_CFG_APP_SIDEBAR_DEF		:Final[str] = 'small'
CONST_CFG_APP_GAP_DEF			:Final[str] = 'small'
CONST_CFG_APP_HAMBURGER			:Final[str] = 'hamburger'
CONST_CFG_APP_BGIMG				:Final[str] = 'bg-img'

CONST_CFG_NOTDEFINED 			:Final[str] = "** NOT DEFINED **"
CONST_CFG_BLANK 				:Final[str] = ""

CONST_ST_MENUITEM_GETHELP		:Final[str] = "Get Help"
CONST_ST_MENUITEM_REPORTBUG		:Final[str] = "Report a Bug"
CONST_ST_MENUITEM_ABOUT			:Final[str] = "About"


CONST_CFG_NONE 					:Final[str] = ""
CONST_ERROR_STR					:Final[str] = "!!Exception!!"
CONST_WARN_STR					:Final[str] = "--WARNING--"
CONST_CFG_APP_SIDEBAR_DEF



g_dataSources = {}
g_canvasResource={}
g_init = 0

def version() : 
	print(f"{version.__module__}.{version.__name__}:{CONST_VER}")


import base64

@performance
@trace
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_bg_url( uri ):
    '''
    A function to unpack an image from url and set as bg.
    Returns
    -------
    The background.
    '''
    bin_str = get_base64_of_bin_file(uri)
    st.markdown(
         f"""
         <style>

         .stApp {{
             background: url("data:image/png;base64,{bin_str}");
             background-size: cover;
             background-position: center; /* Center the image */
  			 background-repeat: no-repeat; 
         }}
         </style>
         """,
         unsafe_allow_html=True
     )
 
def hide_header() :
 	st.markdown(
		"""
		<style>
		    #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
		</style>
		"""
		, unsafe_allow_html=True
	)

@performance
@trace
def disable_hamburger() :
	hide_streamlit_style = """
            <style>
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            </style>
            """
	st.markdown(hide_streamlit_style, unsafe_allow_html=True)

@performance
@trace
def addDataSource( name : str , val ) -> bool :
	try:

		if name in g_dataSources:
			logging.warning(f"duplicate name by {name} in data source dict...")
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
			logging.warning(f"duplicate name by {name} in canvas resource dict...")
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
	
	except Exception as err:
		logging.warning(f"lang:{lang} element:{e} default: {default} applied --reason:{err}")
		return default

@performance
@trace
def siteOptions( configuration : dict, e : str,default=CONST_CFG_NONE, lang : str =  CONST_CFG_APP_LANG) -> str:
	try:
	
		return configuration[lang][CONST_CFG_APP_SITE][e]
	
	except Exception as err:
		logging.warning(f"lang:{lang} element:{e} default: {default} applied --reason:{err}")
		return default

@performance
@trace
def columnOptions ( configuration : dict, e : str, idx = 0, default=CONST_CFG_NONE, lang : str = CONST_CFG_APP_LANG) -> str:
	try:
	
		return configuration[lang][CONST_CFG_APP_SITE][CONST_CFG_APP_COLS][idx][e]
	
	except Exception as err:
		logging.warning(f"lang:{lang} idx:{idx} element:{e} default: {default} applied --reason:{err}")
		return default

@performance
@trace
def rowOptions ( configuration : dict, e : str, colIdx = 0, idx=0, default=CONST_CFG_NONE, lang : str = CONST_CFG_APP_LANG) -> str:
	try:
	
		return configuration[lang][CONST_CFG_APP_SITE][CONST_CFG_APP_COLS][colIdx][CONST_CFG_APP_ROWS][idx][e]
	
	except Exception as err:
		logging.warning(f"lang:{lang} colIdx:{colIdx} rowIdx:{idx} element:{e} default: {default} applied --reason:{err}")
		return default

@performance
@trace
def containerOptions ( configuration : dict, e : str, colIdx = 0, rIdx=0, idx=0, default=CONST_CFG_NONE, lang : str = CONST_CFG_APP_LANG) -> str:
	try:
	
		return configuration[lang][CONST_CFG_APP_SITE][CONST_CFG_APP_COLS][colIdx][CONST_CFG_APP_ROWS][rIdx][CONST_CFG_APP_CONTAINERS][idx][e]
	
	except Exception as err:
		logging.warning(f"lang:{lang} colIdx:{colIdx} rowIdx:{rIdx} containerIdx:{idx} element:{e} default: {default} applied --reason:{err}")
		return default

@performance
@trace
def uxInit( configuration : dict ) -> bool :
	try:

		options     = {}
		menuItems   = {}
		title 	 	= appOptions(configuration,CONST_CFG_APP_TITLE)
		pageTitle	= appOptions(configuration,'pageTitle') #FIX const ref
		layout   	= appOptions(configuration,CONST_CFG_APP_LAYOUT)
		pgIcon   	= appOptions(configuration,CONST_CFG_APP_PAGEICON)
		sideBarState= appOptions(configuration,CONST_CFG_APP_INITIALSIDEBAR,CONST_CFG_APP_SIDEBAR_DEF)
		hamburger 	= appOptions(configuration,CONST_CFG_APP_HAMBURGER)
		bgImg       = appOptions(configuration,CONST_CFG_APP_BGIMG)
		style    	= appOptions(configuration,CONST_CFG_APP_CSS,CONST_CFG_BLANK)
		
		
		if ( len(pageTitle)>0 ) :
			options['page_title']=pageTitle  #FIX const ref
		
		if ( len(layout)>0):
			options['layout']=layout  #FIX const ref

		if ( len(pgIcon)>0):
			options['page_icon']=pgIcon  #FIX const ref
		
		if ( len(sideBarState)>0):
			options['initial_sidebar_state']=sideBarState  #FIX const ref


		
		#hide_header()
		#if ( hamburger):
		#	disable_hamburger()


		st.set_page_config(**options,
							menu_items={
							 CONST_ST_MENUITEM_GETHELP 	 : appOptions(configuration,CONST_CFG_APP_MI_SUPPORT,CONST_CFG_NOTDEFINED),
							 CONST_ST_MENUITEM_REPORTBUG : appOptions(configuration,CONST_CFG_APP_MI_SUPPORT,CONST_CFG_NOTDEFINED),
							 CONST_ST_MENUITEM_ABOUT 	 : appOptions(configuration,CONST_CFG_APP_MI_ABOUT,CONST_CFG_NOTDEFINED),
						   })
		
		if ( len(title)>0 ) :
			st.title(title)

		if ( len(bgImg)>0) :
			set_bg_url(bgImg)

		if (style != CONST_CFG_BLANK) : 
			logging.warning(f'Appending Custom Style sheet {style} to Streamlit App')
			with open( style ) as css:
				st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)
			logging.infor(f'Style sheet {style} applied')


		subHeader = appOptions(configuration,CONST_CFG_APP_SUBTITLE)
		if ( len(subHeader)>0 ) :
			st.subheader(subHeader)

		logging.info(f'init {title} - {subHeader}')

	except Exception as err:
		logging.error(f'{err}')
		return False

@performance
@trace
def uxSidebar(configuration : dict) -> bool:
	bRet = False
	if ( CONST_CFG_APP_SIDEBAR not in configuration[CONST_CFG_APP_LANG][CONST_CFG_APP_SITE]):
		logging.warning(f'Sidebar configuration not defined, skipping processing of sidebar')
		return bRet

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

		canvas=g_canvasResource[configuration['canvas']];
		logging.info(f"loaded canvas {configuration['canvas']} : {canvas}")

		df=None
		if 'data-source' in canvas and len(canvas['data-source'])>0:  #FIX const ref
			df=g_dataSources[canvas['data-source']]  #FIX const ref
			
		stCanvasHandler(canvas,df)
		return True

	except Exception as err:
		logging.error(err)
		return False



#hack - we want to reuse the func' for any container so we pass in the json relitive to the 'Containers'
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
			contId = ('undefined' if 'id' not in container else container['id'])
			logging.info(f'container "{contId}"" render - started')
			stContainer = st.container(border=container[CONST_CFG_APP_CONTAINERS_BORDER],height=container[CONST_CFG_APP_CONTAINERS_HEIGHT] )
			with stContainer:	# ver 1.7 - ref:0001
				if (CONST_CFG_APP_CONTAINERS_TXT in container and len(container[CONST_CFG_APP_CONTAINERS_TXT])>0):
					st.write(container[CONST_CFG_APP_CONTAINERS_TXT])	
				else:
					logging.warning(f'container {contId}): no txt rendered')
				if ( CONST_CFG_APP_IMG in container): # ver 1.7 - ref:0002 
					st.image(container[CONST_CFG_APP_IMG])
				ux_containers[container[CONST_CFG_APP_CONTAINERS_ID]]=container
				uxCanvas(container)

	except Exception as err:
		logging.error(f'{err}, "check elements: {CONST_CFG_APP_CONTAINERS_BORDER},{CONST_CFG_APP_CONTAINERS_HEIGHT},{CONST_CFG_APP_CONTAINERS_TXT},{CONST_CFG_APP_IMG}')

	finally:
		return ux_containers

@performance
@trace
def uxRenderMatrix( configuration : dict) -> dict:
	ux_matrix={}
	
	try:
		if CONST_CFG_APP_COLS not in siteOptions(configuration,CONST_CFG_APP_COLS) :
			logging.warning(f'No Columns defined under Site. skipping column render!')

		# ver 1.7 - ref:0003
		ux_cols=st.columns(len(siteOptions(configuration,CONST_CFG_APP_COLS)),gap=siteOptions(configuration,CONST_CFG_APP_GAP,CONST_CFG_APP_GAP_DEF))
		
		#DRY!!
		#TODO make this tidy 
		for i,c in enumerate(ux_cols):

			with c:
				headerTxt = columnOptions(configuration,CONST_CFG_APP_TITLE,i,CONST_CFG_BLANK)
				subheaderTxt = columnOptions(configuration,CONST_CFG_APP_SUBTITLE,i,CONST_CFG_BLANK)
				txt = columnOptions(configuration,CONST_CFG_APP_CONTAINERS_TXT,i,CONST_CFG_BLANK)

				id = columnOptions(configuration,'id',i,'undefined')
				if ( headerTxt != CONST_CFG_BLANK ) :		
					st.header(headerTxt)

				if ( subheaderTxt != CONST_CFG_BLANK ) :
					st.subheader(subheaderTxt)
				
				if (columnOptions(configuration,CONST_CFG_APP_IMG,i,CONST_CFG_BLANK)) != CONST_CFG_BLANK:
					st.image(columnOptions(configuration,CONST_CFG_APP_IMG,i,CONST_CFG_BLANK))

				if (txt != CONST_CFG_BLANK) : 
					c.write(txt)

				uxContainer(configuration,configuration[CONST_CFG_APP_LANG][CONST_CFG_APP_SITE][CONST_CFG_APP_COLS][i])
				
				if CONST_CFG_APP_ROWS not in siteOptions(configuration,CONST_CFG_APP_COLS)[i] :
					logging.warning(f'No Rows defined under Column:{id}')
				
				else:
					ux_rows=st.columns(len(siteOptions(configuration,CONST_CFG_APP_COLS)[i][CONST_CFG_APP_ROWS]))
				
					for j,r in enumerate(ux_rows):
						with r:
							rowHeaderTxt = rowOptions(configuration,CONST_CFG_APP_TITLE,i,j,CONST_CFG_BLANK)
							rowSubHeaderTxt = rowOptions(configuration,CONST_CFG_APP_SUBTITLE,i,j,CONST_CFG_BLANK)
							rowTxt = rowOptions(configuration,CONST_CFG_APP_CONTAINERS_TXT,i,j,CONST_CFG_BLANK)

							if ( rowHeaderTxt != CONST_CFG_BLANK) :	
								st.header(rowHeaderTxt)

							if ( rowSubHeaderTxt != CONST_CFG_BLANK) :	
								st.subheader(rowSubHeaderTxt)

							if (rowOptions(configuration,CONST_CFG_APP_IMG,i,j,CONST_CFG_BLANK)) != CONST_CFG_BLANK:
								st.image(rowOptions(configuration,CONST_CFG_APP_IMG,i,j,CONST_CFG_BLANK))
							
							if ( rowTxt != CONST_CFG_BLANK ) :
								r.write(rowTxt)

							uxContainer(configuration,configuration[CONST_CFG_APP_LANG][CONST_CFG_APP_SITE][CONST_CFG_APP_COLS][i][CONST_CFG_APP_ROWS][j]) 
						
	except Exception as err:
		logging.error(err)

	finally:
		return ux_matrix


def main():
	pass
# ----------------------------------------------------------------
# ----------------------------------------------------------------
# ----------------------------------------------------------------
version()
if __name__ == '__main__':
	main()