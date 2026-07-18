from xmoney_mindset.config import Settings


def test_settings_defaults():
    settings = Settings()
    assert settings.width == 1920
    assert settings.height == 1080
    assert settings.scene_duration_seconds >= 5
