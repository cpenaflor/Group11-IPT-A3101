from singletons.config_manager import ConfigManager


config1 = ConfigManager()
config2 = ConfigManager()


assert config1 is config2  # Both instances should be identical
config1.set_setting("DEFAULT_TASK_PRIORITY", "High")
assert config2.get_setting("DEFAULT_TASK_PRIORITY") == "High"

print("Verified")