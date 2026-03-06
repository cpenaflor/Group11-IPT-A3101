import logging

class LoggerSingleton:
    """
    Singleton class to provide a centralized logging instance.

    Ensures that all parts of the application share a single logger configuration.
    This avoids duplicate loggers and inconsistent formatting across modules.
    """

    _instance = None  # Class-level attribute to hold the singleton instance

    def __new__(cls, *args, **kwargs):
        """
        Override __new__ to control instance creation.

        Creates the singleton instance if it does not exist, otherwise returns the existing one.
        """
        if not cls._instance:
            # Create the singleton instance
            cls._instance = super(LoggerSingleton, cls).__new__(cls, *args, **kwargs)
            # Initialize the logger with formatting and handlers
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Internal method to configure the logger instance.

        Sets up a stream handler, formatter, and default logging level.
        This ensures consistent log formatting across the application.
        """
        self.logger = logging.getLogger("connectly_logger")  # Named logger for the project
        
        # Create a handler that outputs logs to the console
        handler = logging.StreamHandler()
        
        # Define the log message format
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        
        # Attach the handler to the logger
        self.logger.addHandler(handler)
        
        # Set the default logging level
        self.logger.setLevel(logging.INFO)

    def get_logger(self):
        """
        Returns the configured logger instance.

        Returns:
            logging.Logger: The singleton logger configured for the application.
        """
        return self.logger
