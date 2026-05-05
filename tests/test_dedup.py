"""Tests del deduplicador LRU."""
import pytest
from app.services.dedup import LRUSet


def test_add_and_contains():
    s = LRUSet(maxsize=100)
    s.add("msg1")
    assert s.contains("msg1")
    assert not s.contains("msg2")


def test_duplicate_not_readded():
    s = LRUSet(maxsize=100)
    s.add("msg1")
    s.add("msg1")  # segunda vez
    assert len(s) == 1


def test_eviction_when_full():
    s = LRUSet(maxsize=3)
    s.add("a")
    s.add("b")
    s.add("c")
    assert len(s) == 3
    # Añadir un cuarto elemento debe desalojar el menos reciente ("a")
    s.add("d")
    assert len(s) == 3
    assert not s.contains("a")
    assert s.contains("b")
    assert s.contains("c")
    assert s.contains("d")


def test_lru_order_updated_on_access():
    s = LRUSet(maxsize=3)
    s.add("a")
    s.add("b")
    s.add("c")
    # Acceder a "a" lo mueve al final (más reciente)
    s.contains("a")
    # Al añadir "d", el menos reciente ahora es "b"
    s.add("d")
    assert s.contains("a")
    assert not s.contains("b")
    assert s.contains("c")
    assert s.contains("d")


def test_global_instance_importable():
    from app.services.dedup import message_dedup
    assert isinstance(message_dedup, LRUSet)
