# Change History
# Who	When		What						Version
# ========================================================
# CB 	1/3/2024	See Below					1.3
# 					Ref: 001 : time output to be 9.99 seconds. 

import time
from typing import Final
import argparse 
import logging
from functools import wraps

CONST_VER 			: Final[str]	= '1.3'

CONST_DEF_LOGLEVEL	: Final[int]	= logging.DEBUG
CONST_LOGGING_FMT 	: Final[str]	= '[%(levelname)s][%(asctime)s][%(thread)d:%(threadName)s][%(module)s.%(funcName)s]-%(message)s'
CONST_STR_EXEC_MSG 	: Final[str]	= 'execution time '
CONST_STR_STARTED 	: Final[str]	= 'Started'
CONST_STR_END 		: Final[str]	= 'Finished'
CONST_STR_SEP 		: Final[str]	= ':'
CONST_STR_EXEC_TIME : Final[str]	= 'execution Time'
CONST_DEF_TESTMSG	: Final[str]	= 'this is a test message'
CONST_STR_ARROW		: Final[str]	= '>'


def trace(func):
    @wraps(func)
    def trace_wrapper(*args, **kwargs):
        logging.info(f"{CONST_STR_ARROW}[{func.__name__}]{CONST_STR_SEP}{CONST_STR_STARTED} {CONST_STR_SEP} {args.__str__():.60}..")
        ret = func(*args, **kwargs)
        logging.info(f"{CONST_STR_ARROW}[{func.__name__}]{CONST_STR_SEP}{CONST_STR_END}")
        return ret
    return trace_wrapper

def performance(func):
	@wraps(func)
	def perf_wrapper(*args, **kwargs):
		s = time.perf_counter()
		ret = func(*args, **kwargs)
		#Ref 001
		logging.info(f"{CONST_STR_ARROW}[{func.__name__}]{CONST_STR_SEP}{CONST_STR_EXEC_TIME} {CONST_STR_SEP} {(time.perf_counter()-s):.2f} seconds")
		return ret
	return perf_wrapper

def version() : 
	print(f"{version.__module__}.{version.__name__} {CONST_VER}")


@performance
@trace
def main(argv):
	logging.debug(CONST_DEF_TESTMSG)
	logging.info(CONST_DEF_TESTMSG)
	logging.warning(CONST_DEF_TESTMSG)
	logging.error(CONST_DEF_TESTMSG)
	pass
 
# ----------------------------------------------------------------
# ----------------------------------------------------------------
# ----------------------------------------------------------------
version()
if __name__ == '__main__':
	logging.basicConfig(level=CONST_DEF_LOGLEVEL,format=CONST_LOGGING_FMT)
	cmdLineArgs=argparse.ArgumentParser()
	main(cmdLineArgs.parse_args())

	