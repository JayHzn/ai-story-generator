from __future__ import annotations

import os
import re
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

import click
import requests
from bs4 import BeautifulSoup
from ftfy
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session as SASession

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# DB
Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    source = Column(String(255), nullable=False)
    url = Column(String(2048), nullable=False)
    collected_at = Column(DateTime, default=datetime.utcnow)
    content = Column(Text, nullable=False)

# Collector
class DataCollector:
    def __init__(
        self,
        db_path: str = 'sqlite:///data/db/texts.db',
        user_agent : str = 'Mozilla/5.0 (compatible; IA-TXT-Collector/1.0) Python-requests',
        timeout: int = 10,
    ) -> None:
        self._prepare_sqlite_dir(db_path)
        self.engine = create_engine(db_path, echo=False, future=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, class_=SASession, expire_on_commit=False)

        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})
        self.timeout = timeout
        logger.info("DataCollector prêt (DB=%s, timeout=%ss)", db_path, timeout)