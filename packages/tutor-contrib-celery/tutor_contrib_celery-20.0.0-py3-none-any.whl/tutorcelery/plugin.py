from __future__ import annotations

import os
from glob import glob

import click
import importlib_resources
import tutor
from tutor import hooks

from .__about__ import __version__
from .hooks import CELERY_WORKERS_CONFIG, CELERY_WORKERS_ATTRS_TYPE

########################################
# CONFIGURATION
########################################

CORE_CELERY_WORKER_CONFIG: dict[str, dict[str, CELERY_WORKERS_ATTRS_TYPE]] = {
    "lms": {
        "default": {
            "min_replicas": 0,
            "max_replicas": 10,
            "list_length": 40,
            "enable_keda": False,
        },
    },
    "cms": {
        "default": {
            "min_replicas": 0,
            "max_replicas": 10,
            "list_length": 40,
            "enable_keda": False,
        },
    },
}


# The core autoscaling configs are added with a high priority, such that other users can override or
# remove them.
@CELERY_WORKERS_CONFIG.add(priority=hooks.priorities.HIGH)
def _add_core_autoscaling_config(
    scaling_config: dict[str, dict[str, CELERY_WORKERS_ATTRS_TYPE]],
) -> dict[str, dict[str, CELERY_WORKERS_ATTRS_TYPE]]:
    scaling_config.update(CORE_CELERY_WORKER_CONFIG)
    return scaling_config


@tutor.hooks.lru_cache
def get_celery_workers_config() -> dict[str, dict[str, CELERY_WORKERS_ATTRS_TYPE]]:
    """
    This function is cached for performance.
    """
    return CELERY_WORKERS_CONFIG.apply({})


def iter_celery_workers_config() -> dict[str, dict[str, CELERY_WORKERS_ATTRS_TYPE]]:
    """
    Yield:

        (name, dict)
    """
    return {name: config for name, config in get_celery_workers_config().items()}


def is_celery_multiqueue(service: str) -> bool:
    """
    This function validates whether celery is configured in multiqueue mode for a given service
    """
    service_celery_config = iter_celery_workers_config().get(service, {})
    service_queue_len = len(service_celery_config.keys())

    # If no queue variants are configured, multiqueue is disabled
    if not service_queue_len:
        return False

    # Multiqueue is not enabled if only the default variant is available
    if service_queue_len == 1 and "default" in service_celery_config:
        return False

    return True


@hooks.Actions.PROJECT_ROOT_READY.add()
def configure_default_workers(root: str) -> None:
    if is_celery_multiqueue("lms"):
        hooks.Filters.LMS_WORKER_COMMAND.add_items(["--queues=edx.lms.core.default"])
    if is_celery_multiqueue("cms"):
        hooks.Filters.CMS_WORKER_COMMAND.add_items(["--queues=edx.cms.core.default"])


hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        # Add your new settings that have default values here.
        # Each new setting is a pair: (setting_name, default_value).
        # Prefix your setting names with 'CELERY_'.
        ("CELERY_VERSION", __version__),
        ("CELERY_LMS_EXPLICIT_QUEUES", {}),
        ("CELERY_CMS_EXPLICIT_QUEUES", {}),
        ("CELERY_FLOWER", False),
        ("CELERY_FLOWER_EXPOSE_SERVICE", False),
        ("CELERY_FLOWER_HOST", "flower.{{LMS_HOST}}"),
        ("CELERY_FLOWER_DOCKER_IMAGE", "docker.io/mher/flower:2.0.1"),
        ("CELERY_FLOWER_SERVICE_MONITOR", False),
    ]
)

hooks.Filters.CONFIG_UNIQUE.add_items(
    [
        # Add settings that don't have a reasonable default for all users here.
        # For instance: passwords, secret keys, etc.
        # Each new setting is a pair: (setting_name, unique_generated_value).
        # Prefix your setting names with 'CELERY_'.
        # For example:
        ### ("CELERY_SECRET_KEY", "{{ 24|random_string }}"),
        ("CELERY_FLOWER_BASIC_AUTH", "flower:{{ 24 |random_string }}")
    ]
)

hooks.Filters.CONFIG_OVERRIDES.add_items(
    [
        # Danger zone!
        # Add values to override settings from Tutor core or other plugins here.
        # Each override is a pair: (setting_name, new_value). For example:
        ### ("PLATFORM_NAME", "My platform"),
    ]
)


########################################
# INITIALIZATION TASKS
########################################

# To add a custom initialization task, create a bash script template under:
# tutorcelery/templates/celery/tasks/
# and then add it to the MY_INIT_TASKS list. Each task is in the format:
# ("<service>", ("<path>", "<to>", "<script>", "<template>"))
MY_INIT_TASKS: list[tuple[str, tuple[str, ...]]] = [
    # For example, to add LMS initialization steps, you could add the script template at:
    # tutorcelery/templates/celery/tasks/lms/init.sh
    # And then add the line:
    ### ("lms", ("celery", "tasks", "lms", "init.sh")),
]


# For each task added to MY_INIT_TASKS, we load the task template
# and add it to the CLI_DO_INIT_TASKS filter, which tells Tutor to
# run it as part of the `init` job.
for service, template_path in MY_INIT_TASKS:
    full_path: str = str(
        importlib_resources.files("tutorcelery")
        / os.path.join("templates", *template_path)
    )
    with open(full_path, encoding="utf-8") as init_task_file:
        init_task: str = init_task_file.read()
    hooks.Filters.CLI_DO_INIT_TASKS.add_item((service, init_task))


########################################
# DOCKER IMAGE MANAGEMENT
########################################


# Images to be built by `tutor images build`.
# Each item is a quadruple in the form:
#     ("<tutor_image_name>", ("path", "to", "build", "dir"), "<docker_image_tag>", "<build_args>")
hooks.Filters.IMAGES_BUILD.add_items(
    [
        # To build `myimage` with `tutor images build myimage`,
        # you would add a Dockerfile to templates/celery/build/myimage,
        # and then write:
        ### (
        ###     "myimage",
        ###     ("plugins", "celery", "build", "myimage"),
        ###     "docker.io/myimage:{{ CELERY_VERSION }}",
        ###     (),
        ### ),
    ]
)


# Images to be pulled as part of `tutor images pull`.
# Each item is a pair in the form:
#     ("<tutor_image_name>", "<docker_image_tag>")
hooks.Filters.IMAGES_PULL.add_items(
    [
        # To pull `myimage` with `tutor images pull myimage`, you would write:
        ### (
        ###     "myimage",
        ###     "docker.io/myimage:{{ CELERY_VERSION }}",
        ### ),
    ]
)


# Images to be pushed as part of `tutor images push`.
# Each item is a pair in the form:
#     ("<tutor_image_name>", "<docker_image_tag>")
hooks.Filters.IMAGES_PUSH.add_items(
    [
        # To push `myimage` with `tutor images push myimage`, you would write:
        ### (
        ###     "myimage",
        ###     "docker.io/myimage:{{ CELERY_VERSION }}",
        ### ),
    ]
)


########################################
# TEMPLATE RENDERING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

hooks.Filters.ENV_TEMPLATE_ROOTS.add_items(
    # Root paths for template files, relative to the project root.
    [
        str(importlib_resources.files("tutorcelery") / "templates"),
    ]
)

hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    # For each pair (source_path, destination_path):
    # templates at ``source_path`` (relative to your ENV_TEMPLATE_ROOTS) will be
    # rendered to ``source_path/destination_path`` (relative to your Tutor environment).
    # For example, ``tutorcelery/templates/celery/build``
    # will be rendered to ``$(tutor config printroot)/env/plugins/celery/build``.
    [
        ("celery/build", "plugins"),
        ("celery/apps", "plugins"),
        ("celery/k8s", "plugins"),
    ],
)


# Make the pod-autoscaling hook functions available within templates
hooks.Filters.ENV_TEMPLATE_VARIABLES.add_items(
    [
        ("iter_celery_workers_config", iter_celery_workers_config),
        ("is_celery_multiqueue", is_celery_multiqueue),
    ]
)
########################################
# PATCH LOADING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

# For each file in tutorcelery/patches,
# apply a patch based on the file's name and contents.
for path in glob(str(importlib_resources.files("tutorcelery") / "patches" / "*")):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))


########################################
# CUSTOM JOBS (a.k.a. "do-commands")
########################################

# A job is a set of tasks, each of which run inside a certain container.
# Jobs are invoked using the `do` command, for example: `tutor local do importdemocourse`.
# A few jobs are built in to Tutor, such as `init` and `createuser`.
# You can also add your own custom jobs:


# To add a custom job, define a Click command that returns a list of tasks,
# where each task is a pair in the form ("<service>", "<shell_command>").
# For example:
### @click.command()
### @click.option("-n", "--name", default="plugin developer")
### def say_hi(name: str) -> list[tuple[str, str]]:
###     """
###     An example job that just prints 'hello' from within both LMS and CMS.
###     """
###     return [
###         ("lms", f"echo 'Hello from LMS, {name}!'"),
###         ("cms", f"echo 'Hello from CMS, {name}!'"),
###     ]


# Then, add the command function to CLI_DO_COMMANDS:
## hooks.Filters.CLI_DO_COMMANDS.add_item(say_hi)

# Now, you can run your job like this:
#   $ tutor local do say-hi --name="edunext"


#######################################
# CUSTOM CLI COMMANDS
#######################################

# Your plugin can also add custom commands directly to the Tutor CLI.
# These commands are run directly on the user's host computer
# (unlike jobs, which are run in containers).

# To define a command group for your plugin, you would define a Click
# group and then add it to CLI_COMMANDS:


### @click.group()
### def celery() -> None:
###     pass


### hooks.Filters.CLI_COMMANDS.add_item(celery)


# Then, you would add subcommands directly to the Click group, for example:


### @celery.command()
### def example_command() -> None:
###     """
###     This is helptext for an example command.
###     """
###     print("You've run an example command.")


# This would allow you to run:
#   $ tutor celery example-command
