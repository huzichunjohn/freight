from __future__ import absolute_import, unicode_literals

from ds.models import App

from .base import Serializer
from .manager import add


@add(App)
class AppSerializer(Serializer):
    def serialize(self, item, attrs):
        return {
            'id': str(item.id),
            'name': item.name,
            'provider': item.provider,
            'provider_config': item.provider_config,
        }
