from typing import Final
from abc import ABC, abstractmethod
from st_files_connection import FilesConnection
from vwlogger import trace
from vwlogger import performance

import streamlit as st
import json
import logging
import vwlogger
import streamlit_helper as stHelper


CONST_ENV						:Final[str] = "dev"
CONST_READ_ONLY_MODE 			:Final[str] = "r"
CONST_VER						:Final[str] = '1.2'
CONST_APP_NAME					:Final[str] = 'lorum'

#@st.cache_data
@performance
@trace
def loadConfiguration( f : str, env : str = CONST_ENV, mode : str = CONST_READ_ONLY_MODE ) -> dict:
	with open( f, mode) as fHndl :
		    cfgData = json.load( fHndl )
	
	return (cfgData)

def version():
	print(f"{version.__module__}.{version.__name__} {CONST_VER}")


def secret_datasource_sectionKey( id : str , env : str = CONST_ENV) -> str :
	return env+"-"+id


@performance
@trace
def persitDataSources( configuration : dict, lang : str =  stHelper.CONST_CFG_APP_LANG) -> bool: 
	#todo get the constants extracted!!! and sort logging messages
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

			conn = st.connection(st.secrets[datasource_section].fs, type=FilesConnection)
			df = conn.read(st.secrets[datasource_section].data_uri, input_format=st.secrets[datasource_section].format, ttl=st.secrets[datasource_section].ttl)
			stHelper.addDataSource(ds['id'],df)
				
			#st.write(df)
		return True

	except Exception as err:
		logging.warning(f"Error:{err} - lang:{lang} element:{e} default: {default} applied.... ")
		return default


@performance
@trace
def persitCanvas( configuration : dict, lang : str =  stHelper.CONST_CFG_APP_LANG) -> bool: 
	#todo get the constants extracted!!! and sort logging messages
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
def main( *args ) -> None :

	dataResources = {}

	cfg = loadConfiguration('./dev.cfg.json')


	stHelper.uxInit(cfg)
	stHelper.uxSidebar(cfg)
	persitDataSources(cfg)
	persitCanvas(cfg)
	stHelper.uxContainer(cfg,cfg[stHelper.CONST_CFG_APP_LANG][stHelper.CONST_CFG_APP_SITE])
	stHelper.uxRenderMatrix(cfg);
	

	
# ----------------------------------------------------------------
# ----------------------------------------------------------------
# ----------------------------------------------------------------
logging.basicConfig(level=vwlogger.CONST_DEF_LOGLEVEL,format=vwlogger.CONST_LOGGING_FMT)
logging.info(f"{CONST_APP_NAME} {CONST_VER}")
version()
main()

#st.dataframe(cfg)
