from django.test import TestCase
from django.contrib.auth.models import User

from posts.singletons.config_manager import ConfigManager
from posts.singletons.logger_singleton import LoggerSingleton
from posts.factories.post_factory import PostFactory


class SingletonTests(TestCase):
    def test_config_singleton(self):
        c1 = ConfigManager()
        c2 = ConfigManager()
        self.assertIs(c1, c2)

        c1.set_setting("DEFAULT_PAGE_SIZE", 50)
        self.assertEqual(c2.get_setting("DEFAULT_PAGE_SIZE"), 50)

    def test_logger_singleton(self):
        l1 = LoggerSingleton()
        l2 = LoggerSingleton()
        self.assertIs(l1, l2)


class FactoryTests(TestCase):
    def test_post_factory_validation(self):
        user = User.objects.create_user(username="tester", password="Pass12345!")
        with self.assertRaises(ValueError):
            PostFactory.create_post(author=user, content="")  # invalid
