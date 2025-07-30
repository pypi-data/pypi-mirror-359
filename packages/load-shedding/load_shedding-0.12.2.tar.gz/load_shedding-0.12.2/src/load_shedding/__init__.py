from enum import Enum

from .load_shedding import (
    Area, Stage, StageError, ProviderError,
    get_areas, get_area_schedule, get_stage, get_stages, get_stage_forecast, get_area_forecast
)
from .providers import Province, coct, eskom, sepush


class Provider(Enum):
    ESKOM = 1
    COCT = 2
    SE_PUSH = 3

    def __call__(self, *args, **kwargs):
        return {
            Provider.ESKOM: eskom.Eskom,
            Provider.COCT: coct.CoCT,
            Provider.SE_PUSH: sepush.SePush,
        }.get(self, None)(*args, **kwargs)

    def __str__(self):
        return {
            self.ESKOM: eskom.Eskom.name,
            self.COCT: coct.CoCT.name,
            self.SE_PUSH: sepush.SePush.name,
        }.get(self, "Unknown Provider")
