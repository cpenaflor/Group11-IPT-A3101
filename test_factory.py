import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connectly_project.settings')
django.setup()

from factories.task_factory import TaskFactory
from tasks.models import User


user = User.objects.first()
task = TaskFactory.create_task(
    task_type="priority",
    title="Finish API Documentation",
    description="Complete by EOD",
    assigned_to=user,
    metadata={"priority_level": "High"}
)
assert task.task_type == "priority"


if user:
    print("Verified")
else:
    print("No user found.")

