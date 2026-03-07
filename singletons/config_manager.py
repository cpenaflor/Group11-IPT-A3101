class ConfigManager:
    """
    Singleton class for managing centralized configuration settings.

    This ensures that there is only one instance of configuration across the application.
    Any part of the application accessing this class will receive the same shared settings.
    """

    _instance = None  # Class-level attribute to hold the singleton instance

    def __new__(cls, *args, **kwargs):
        """
        Override __new__ to control instance creation.

        If an instance does not exist, create it and initialize settings.
        Otherwise, return the existing instance.
        """
        if not cls._instance:
            # Create the singleton instance
            cls._instance = super(ConfigManager, cls).__new__(cls, *args, **kwargs)
            # Initialize default configuration settings
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Internal method to initialize default configuration settings.

        This is called only once when the singleton instance is first created.
        """
        self.settings = {
            "DEFAULT_PAGE_SIZE": 20,  # Default number of items per page in paginated endpoints
            "ENABLE_ANALYTICS": True, # Flag to enable or disable analytics tracking
            "RATE_LIMIT": 100         # Maximum number of API requests allowed per time window
        }

    def get_setting(self, key):
        """
        Retrieve the value of a configuration setting.

        Args:
            key (str): The name of the configuration setting.

        Returns:
            The value associated with the key, or None if the key does not exist.
        """
        return self.settings.get(key)

    def set_setting(self, key, value):
        """
        Update or add a configuration setting.

        Args:
            key (str): The name of the configuration setting.
            value: The value to assign to the setting.
        """
        self.settings[key] = value
