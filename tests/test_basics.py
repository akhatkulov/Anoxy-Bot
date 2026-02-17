import pytest
from core.database.models import User
from utils.i18n import _

def test_user_model_creation():
    user = User(
        id=123,
        name="Test User",
        age=25,
        gender="male",
        target_gender="female",
        language="uz"
    )
    assert user.id == 123
    assert user.name == "Test User"
    assert user.is_banned is False

def test_localization_uz():
    text = _('welcome', 'uz')
    assert "xush kelibsiz" in text.lower()

def test_localization_ru():
    text = _('welcome', 'ru')
    assert "добро пожаловать" in text.lower()

def test_localization_tg():
    text = _('welcome', 'tg')
    assert "хуш омадед" in text.lower()

def test_localization_fallback():
    # Should fallback to uz if key or lang is wrong
    text = _('non_existent_key', 'unknown_lang')
    assert text == 'non_existent_key'
