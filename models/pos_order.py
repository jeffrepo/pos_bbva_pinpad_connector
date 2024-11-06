# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from lxml import etree
from odoo.exceptions import UserError, ValidationError
from lxml.builder import ElementMaker
import xml.etree.ElementTree as ET
import requests
from requests.auth import HTTPBasicAuth
import logging
import xmltodict, json
from datetime import datetime
from urllib.request import urlopen
from odoo import http
from odoo.http import request
import time
_logger = logging.getLogger(__name__)