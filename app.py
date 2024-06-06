from typing import Final
from abc import ABC, abstractmethod
from st_files_connection import FilesConnection
from vwlogger import trace
from vwlogger import performance
from streamlit_autorefresh import st_autorefresh


import streamlit as st
import threading


import json
import logging
import vwlogger
import streamlit_helper as stHelper

CONST_VER						:Final[str] = '1.2'


CONST_APP_CFG_ENV				:Final[str] = 'env'
CONST_APP_CFG_PAGES				:Final[str] = 'Pages'
CONST_APP_CFG_PAGES_CFG			:Final[str] = 'cfg'
CONST_APP_CFG					:Final[str] = 'json2st.app.json'
CONST_READ_ONLY_MODE 			:Final[str] = 'r'
CONST_APP_NAME					:Final[str] = 'JSON2StreamLit'
CONST_SESSION_VAR_PAGE			:Final[str] = 'PageNumber'
CONST_APP_CFG_PAGEREFRESH		:Final[str] = 'pageRefresh'
CONST_APP_NEXTMODE				:Final[str] = 'nextMode'

CONST_APP_DEF_INC				:Final[int] = 1
CONST_APP_MAX_PAGES				:Final[int] = 100
CONST_APP_TIMER_LIMIT			:Final[int] = 10000

CONST_DEF_PATH					:Final[str] = './'
CONST_DEF_ENV					:Final[str] = 'dev'
CONST_DEF_AUTO_NEXTMODE			:Final[str] = 'auto'
CONST_DEF_REFRESHKEY			:Final[str] = 'pageRefresh'
CONST_DEF_REFRESHRATE			:Final[int] = 60000
CONST_SOURCEDATA_TTL			:Final[int] = 60000 # 10 mins.



#@st.cache_data
@performance
@trace
def loadConfiguration( f : str, mode : str = CONST_READ_ONLY_MODE ) -> dict:
	with open( f, mode) as fHndl :
		    cfgData = json.load( fHndl )
	
	return (cfgData)

def version():
	print(f"{version.__module__}.{version.__name__} {CONST_VER}")


def secret_datasource_sectionKey( id : str , env : str = CONST_DEF_ENV) -> str :
	return env+"-"+id


@performance
@trace
def persitDataSources( configuration : dict, lang : str =  stHelper.CONST_CFG_APP_LANG) -> bool: 
	
	if 'Resources' not in configuration[lang]:
		logging.warning(f'No Resources section defined. skipping loading of Data sources !')
		return False

	RESOURCES : Final[str] = configuration[lang]['Resources']
	
	try:
		if ( 'DataSources' not in RESOURCES):
			logging.warning('missing DataSources from JSON')
			return False

		DATASOURCES : Final[str]=RESOURCES['DataSources']
		logging.info(f"loading data resources x{len(DATASOURCES)}")

		for i,ds in enumerate(DATASOURCES):
			datasource_section = secret_datasource_sectionKey(ds['id'])
			logging.info(f"Loading data source :{ds['id']} using section {datasource_section} from secret")
			logging.info(f"Secret: {datasource_section} : fs:{st.secrets[datasource_section].fs}")
			logging.info(f"Secret: {datasource_section} : uri:{st.secrets[datasource_section].data_uri}")
			logging.info(f"Secret: {datasource_section} : type:{st.secrets[datasource_section].format}")
			logging.info(f"Secret: {datasource_section} : ttl:{st.secrets[datasource_section].ttl}")

			#conn = st.connection(st.secrets[datasource_section].fs, type=FilesConnection)
			#df = conn.read(st.secrets[datasource_section].data_uri, input_format=st.secrets[datasource_section].format, ttl=st.secrets[datasource_section].ttl)
			df = loadDataSource(st.secrets[datasource_section].data_uri,
								st.secrets[datasource_section].format,
								st.secrets[datasource_section].ttl,
								st.secrets[datasource_section].fs,
								FilesConnection)

			stHelper.addDataSource(ds['id'],df)
				
		return True

	except Exception as err:
		logging.warning(f"Error:{err} - lang:{lang} element:{e} default: {default} applied.... ")
		return default

#@st.cache_data(ttl=CONST_SOURCEDATA_TTL)
@performance
@trace
def loadDataSource ( uri : str, format : str, ttl : int ,fs : str, fileConnection) -> dict:
	conn = st.connection(fs, type=fileConnection)
	df = conn.read(uri, input_format=format, ttl=ttl)
	return df

@performance
@trace
def persitCanvas( configuration : dict, lang : str =  stHelper.CONST_CFG_APP_LANG) -> bool: 
	
	if 'Resources' not in configuration[lang]:
		logging.warning(f'No Resources section defined. skipping loading of Canvas sources !')
		return False

	RESOURCES : Final[str] = configuration[lang]['Resources']

	try:

		if ( 'Canvas' not in RESOURCES):
			logging.warning('missing Canvas from JSON')
			return False

		CANVASSOURCES : Final[str]=RESOURCES['Canvas']
		logging.info(f"loading canvas resources x{len(CANVASSOURCES)}")

		for i,cr in enumerate(CANVASSOURCES):
			logging.info(f'persiting canvas resource {cr}')
			stHelper.addCanvasResource(cr['id'],cr)
		
		return True

	except Exception as err:
		logging.warning(f"Error:{err} - lang:{lang} element:{e} default: {default} applied.... ")
		return default


@performance
@trace
def resetDashboardPageIdx(nom : str):
	st.session_state[nom] = -1

@performance
@trace
def incrementDashboardPageIdx(nom : str  , n : int , m : int = CONST_APP_MAX_PAGES) -> int:
	
	if nom not in st.session_state:
		st.session_state[nom] = 0

	else : 
		logging.warning(f'result pageIdx:{st.session_state[nom]} + n:{n} % m:{m} = [{(st.session_state[nom]+n)%m}')
		st.session_state[nom] = 0 if (st.session_state[nom]+n) % m == 0 else st.session_state[nom]+n

	logging.info(f'Session Variable: {nom} is set to {st.session_state[nom]}')
	return st.session_state[nom]

def getCfgOptionInt( configuration : dict, nom : str, default : int ) -> int :
	logging.info(configuration)
	if nom not in configuration :
		logging.warning (f'Using default value of {default} for configuration option {nom}')
		return default


	return (default if len(str(configuration[nom]))==0 else configuration[nom])

def getCfgOptionStr( configuration : dict, nom : str, default : int ) -> str :
	if nom not in configuration :
		logging.warning (f'Using default value of {default} for configuration option {nom}')
		return default

	return (default if len(configuration[nom])==0 else configuration[nom])
	

@performance
@trace
def main( *args ) -> None :
	
	AppCfg = loadConfiguration(f'./{CONST_APP_CFG}')

	if CONST_APP_CFG_ENV not in AppCfg[CONST_APP_NAME] :
		logging.warning (f'missing env key, using {CONST_DEF_ENV} ') 
		AppCfg[CONST_APP_NAME][CONST_APP_CFG_ENV] = CONST_DEF_ENV

	appMode = getCfgOptionStr(AppCfg[CONST_APP_NAME],
							  CONST_APP_NEXTMODE, 'manual') # TODO issue constant for manual.

	logging.info(f'{CONST_APP_NAME} operating in {AppCfg[CONST_APP_NAME][CONST_APP_CFG_ENV] } mode')
	maxDefinedPages=len(AppCfg[CONST_APP_NAME][CONST_APP_CFG_PAGES]) # TODO issue if no pages defined..... guess there should be at least 1
	pageIdx=incrementDashboardPageIdx(CONST_SESSION_VAR_PAGE,
									  CONST_APP_DEF_INC,maxDefinedPages)

	if (appMode != CONST_DEF_AUTO_NEXTMODE ):
		resetDashboardPageIdx(CONST_SESSION_VAR_PAGE)

	logging.info(f'Render Page {pageIdx} of {maxDefinedPages}- Started')
	pageCfgFile = AppCfg[CONST_APP_NAME][CONST_APP_CFG_PAGES][pageIdx][CONST_APP_CFG_PAGES_CFG] # TODO issue if no pages defined
	logging.info(f'Loading page configuration {pageIdx} = {pageCfgFile}')
	cfg = loadConfiguration(f'{CONST_DEF_PATH}{pageCfgFile}')
	stHelper.uxInit(cfg)
	persitDataSources(cfg)
	persitCanvas(cfg)
	stHelper.uxSidebar(cfg)
	stHelper.uxContainer(cfg,cfg[stHelper.CONST_CFG_APP_LANG][stHelper.CONST_CFG_APP_SITE])
	stHelper.uxRenderMatrix(cfg);
	
	if (appMode == CONST_DEF_AUTO_NEXTMODE ):
		refreshDelay=AppCfg[CONST_APP_NAME][CONST_APP_CFG_PAGES][pageIdx]['pageRefresh'] # TODO issue if no pages defined or set to 0
		logging.info(f'page auto-loader {pageIdx} - {pageCfgFile} - enabled')
		count = st_autorefresh(interval=refreshDelay, limit=CONST_APP_TIMER_LIMIT, key=CONST_DEF_REFRESHKEY)
		logging.info(f'page auto-loader {pageIdx} - {pageCfgFile}, refresh in {refreshDelay/1000:.0f} seconds, mode:{appMode}')

	else:
		logging.info(f'page manual-loader {pageIdx} - {pageCfgFile} - enabled')
		
	
	
# ----------------------------------------------------------------
# ----------------------------------------------------------------
# ----------------------------------------------------------------
logging.basicConfig(level=vwlogger.CONST_DEF_LOGLEVEL,format=vwlogger.CONST_LOGGING_FMT) # TODO better way to enable logging.... env var.
logging.info(f"{CONST_APP_NAME} {CONST_VER}")
version()
main()

#st.dataframe(cfg)
