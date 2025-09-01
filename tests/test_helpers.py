import pytest
import sys
import os

# Añadir el directorio raíz del proyecto al sys.path para permitir importaciones de módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.helpers import truncate_text

def test_truncate_text_shorter_than_max():
    """Prueba que el texto más corto que el máximo no se trunca."""
    assert truncate_text("Hola mundo", 20) == "Hola mundo"

def test_truncate_text_longer_than_max():
    """Prueba que el texto más largo que el máximo se trunca correctamente."""
    assert truncate_text("Este es un texto muy largo para ser truncado", 20) == "Este es un texto..."

def test_truncate_text_with_custom_ellipsis():
    """Prueba el truncado con un ellipsis personalizado."""
    assert truncate_text("Este es un texto muy largo", 20, " (sigue)") == "Este es un t (sigue)"

def test_truncate_text_exact_length():
    """Prueba que el texto con longitud exacta no se modifica."""
    assert truncate_text("12345", 5) == "12345"

def test_truncate_text_empty_string():
    """Prueba que un string vacío devuelve un string vacío."""
    assert truncate_text("", 10) == ""

def test_truncate_text_none_input():
    """Prueba que una entrada None devuelve un string vacío."""
    # En la implementación actual, pd.isna(None) sería verdadero, devolviendo ''
    assert truncate_text(None, 10) == ""
