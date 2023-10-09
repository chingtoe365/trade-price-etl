import json
import logging
import os
import sys
from typing import Optional, Union, Dict, Any

from pydantic import FilePath, model_validator
from pydantic_settings import BaseSettings
from pythonjsonlogger import jsonlogger

import logging.config as log_conf

logger = logging.getLogger(__name__)


class LoggingSettings(BaseSettings):
    LEVEL: str = "INFO"
    CAPTURE_WARNINGS: bool = True
    IGNORE_WARNINGS: bool = True
    USE_JSON: bool = False
    CONFIG: Optional[Union[FilePath, Dict]] = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "log_config.json"
    )

    @model_validator(mode="after")
    def logging_dict_config(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # v = values.get("CONFIG", None)
        v = None if not values.CONFIG else values.CONFIG
        # print(f">> Going through logging config validation {v}")
        if v is not None:
            # print(f">> Config value is not none")
            conf_dict = {}
            if isinstance(v, dict):
                conf_dict = v
            else:
                try:
                    with open(v) as lf:
                        conf_dict = json.load(lf)
                except Exception:
                    logger.exception("Failed to load logging configuration from %d", v)
            if len(conf_dict) > 0:
                try:
                    # logging.basicConfig(conf_dict=conf_dict)
                    # print(conf_dict)
                    log_conf.dictConfig(conf_dict)
                except Exception:
                    logging.basicConfig(level=logging.INFO)
                    logger.exception("Failed to configure logging with %d", conf_dict)
            else:
                logging.basicConfig(level=logging.INFO)
                logger.warning("Failed to configure logging")

            root_logger = logging.getLogger()
            if values.LEVEL is not None:
                try:
                    root_logger.setLevel(values.LEVEL)
                except ValueError:
                    root_logger.setLevel("WARNING")
                    logger.exception(
                        "Failed to set logging level to %d, using WARNING",
                        values["LEVEL"],
                    )
            if values.USE_JSON:
                formatter = jsonlogger.JsonFormatter(
                    fmt="%(asctime)s %(levelname)s %(name)s %(funcName)s %(lineno)d %(process)d %(thread)d %(message)s"
                )
                handler = logging.StreamHandler(stream=sys.stdout)
                handler.setLevel(logging.DEBUG)
                handler.setFormatter(formatter)
                for _ in root_logger.handlers:
                    root_logger.removeHandler(_)
                root_logger.addHandler(handler)

            if values.CAPTURE_WARNINGS:
                logging.captureWarnings(True)
                logging.getLogger("py.warnings").setLevel(
                    logging.CRITICAL
                    if values.IGNORE_WARNINGS
                    else logging.WARNING
                )
        return values
    #
    # class Config:
    #     case_sensitive = True
    #     env_prefix = "ETL_LOGGING_"
