"""
Deduplicación de mensajes con un caché LRU en memoria.

En producción se recomienda reemplazar esto por Redis
(e.g. SET message:{id} 1 EX 86400 NX) para que el estado
sobreviva reinicios del proceso y funcione en múltiples réplicas.
"""
from collections import OrderedDict


class LRUSet:
    """Conjunto con capacidad máxima que descarta los elementos menos recientes."""

    def __init__(self, maxsize: int = 10_000):
        self._cache: OrderedDict[str, None] = OrderedDict()
        self._maxsize = maxsize

    def contains(self, key: str) -> bool:
        if key in self._cache:
            self._cache.move_to_end(key)
            return True
        return False

    def add(self, key: str) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            self._cache[key] = None
            if len(self._cache) > self._maxsize:
                self._cache.popitem(last=False)

    def __len__(self) -> int:
        return len(self._cache)


# Instancia global para reutilizar en toda la aplicación
message_dedup = LRUSet(maxsize=10_000)
