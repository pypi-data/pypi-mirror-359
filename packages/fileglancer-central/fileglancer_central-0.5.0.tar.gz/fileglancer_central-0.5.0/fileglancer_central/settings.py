from typing import List, Dict, Optional
from functools import cache
import sys

from pathlib import Path
from pydantic import HttpUrl, BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource
)
from loguru import logger
    

class Settings(BaseSettings):
    """ Settings can be read from a settings.yaml file, 
        or from the environment, with environment variables prepended 
        with "fgc_" (case insensitive). The environment variables can
        be passed in the environment or in a .env file. 
    """

    log_level: str = 'DEBUG'
    db_url: str = 'sqlite:///fileglancer.db'

    # If true, use seteuid/setegid for file access
    use_access_flags: bool = False

    # Confluence settings for getting the institutional file share paths
    confluence_url: Optional[HttpUrl] = None
    confluence_token: Optional[str] = None

    # If confluence settings are not provided, use a static list of paths to mount as file shares
    # This can specify the home directory using a ~/ prefix.
    file_share_mounts: List[str] = []
    
    # JIRA settings for managing tickets
    jira_url: Optional[HttpUrl] = None
    jira_token: Optional[str] = None

    # The external URL of the proxy server for accessing proxied paths.
    # Maps to the /files/ end points of the fileglancer-central app.
    external_proxy_url: Optional[HttpUrl] = None

    model_config = SettingsConfigDict(
        yaml_file="config.yaml",
        env_file='.env',
        env_prefix='fgc_',
        env_nested_delimiter="__",
        env_file_encoding='utf-8'
    )
  
    @classmethod
    def settings_customise_sources(  # noqa: PLR0913
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            YamlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )


@cache
def get_settings():
    return Settings()
