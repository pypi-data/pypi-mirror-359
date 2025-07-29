from abc import ABC
from typing import List, Optional

from pydantic import Field
from ibm_agent_analytics_core.interfaces.elements import Element
from abc import ABCMeta


class RelatableElement(Element,metaclass=ABCMeta):
    related_to_ids: List[str] = Field(
        default_factory=list, description="Elements related to this object"
    )
    