from typing import Any

from fast_agave.blueprints import RestApiBlueprint
from starlette_context import context


class CustomQueryBlueprint(RestApiBlueprint):
    @property
    def custom(self) -> str:
        return context['custom']

    def property_filter_required(self) -> bool:
        return context.get('custom_filter_required')

    def custom_filter_required(self, query_params: Any, model: any) -> None:
        if self.property_filter_required() and hasattr(model, 'custom'):
            query_params.custom = self.custom

    def user_id_filter_required(self) -> bool:
        return False

    def platform_id_filter_required(self) -> bool:
        return False
