"""This is the main module for the axmp-ai-agent-studio project."""

import logging
import logging.config

from axmp_ai_agent_studio.setting import logger_settings

logging.config.fileConfig(logger_settings.config_file, disable_existing_loggers=False)
logging.getLogger("appLogger").setLevel(logger_settings.level)

logging.getLogger("pymongo").setLevel(logging.INFO)
logging.getLogger("motor").setLevel(logging.INFO)
logging.getLogger("sse_starlette.sse").setLevel(logging.INFO)
