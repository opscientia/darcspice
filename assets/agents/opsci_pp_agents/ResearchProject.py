import logging
log = logging.getLogger('agents')

from enforce_typing import enforce_types
from typing import List, Dict
import random

from util.constants import S_PER_MONTH

@enforce_types
class ResearchProject():
    '''
    Represents a funded research project. Created by Researchers, used for tracking community engagement, academic lineage, impact, etc.
    '''
    def __init__(self, name: str, creator: str, value: int, impact: float, integration: float, novelty: float, engagement: float = 0.0):

        self.name = name
        self.creator = creator
        self.value = value
        self.impact = impact
        self.integration = integration
        self.novelty = novelty
        self.engagement = engagement