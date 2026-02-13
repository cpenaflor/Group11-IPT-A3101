import logging

class LoggerSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            # Create the instance only if it doesn't exist
            cls._instance = super(LoggerSingleton, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # Configure the logger instance
        self.logger = logging.getLogger("connectly_logger")
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def get_logger(self):
        """Returns the configured logger instance."""
        return self.logger