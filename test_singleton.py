from singletons.config_manager import ConfigManager

# 1. Attempt to create two separate instances
config1 = ConfigManager()
config2 = ConfigManager()

# 2. Verify both instances are the exact same object in memory
assert config1 is config2  # This will fail if a new object was created
print("Success: Both variables point to the same instance.")

# 3. Modify a setting using the first variable
config1.set_setting("DEFAULT_PAGE_SIZE", 50)

# 4. Check if the change is reflected when accessed via the second variable
assert config2.get_setting("DEFAULT_PAGE_SIZE") == 50
print(f"Success: Updated value (50) retrieved from config2.")