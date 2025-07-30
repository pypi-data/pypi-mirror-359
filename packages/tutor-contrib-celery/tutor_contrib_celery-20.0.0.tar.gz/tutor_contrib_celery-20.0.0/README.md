# Celery plugin for [Tutor](https://docs.tutor.edly.io)

A tutor plugin to extend the default LMS and CMS celery workers included in Tutor.
It adds and configures extra deployments running LMS and CMS celery workers where
every deployment will process async tasks routed to a specific queue. Having this
workers separation per queue can help to define the scaling requirements for the Celery
deployments, since having a single queue (the default one) with a single deployment can
lead to unexpected behaviors when running large-scale sites.

## Installation

```shell
pip install tutor-contrib-celery
```

## Usage

```shell
tutor plugins enable celery
```

## Configuration

### Celery queues

By default, in a standard OpenedX installation with Tutor in Kubernetes, all the LMS/CMS async tasks are executed
by a single celery deployment. This plugin allows to distribute async workload by configuring additional deployments
to execute celery tasks sent to a specific queues. This can help to:

- Achieve a better performance when having high volume of async tasks to process
- Configure different scaling parameters according to the nature of the tasks processed by a queue (I/O bound tasks,
CPU tasks, etc.)

To achieve this, the `CELERY_WORKERS_CONFIG` filter is implemented to add extra queues whose tasks require to be
processed by a separated deployment.

## Recommended multiqueue configuration

From checking the LMS and CMS codebase, the queues for every service are described below:

- **CMS**: default, high, low (taken from CMS settings [here](https://github.com/openedx/edx-platform/blob/open-release/redwood.master/cms/envs/common.py#L1578-L1582))
- **LMS**: default, high, high_mem (taken from LMS settings [here](https://github.com/openedx/edx-platform/blob/open-release/redwood.master/lms/envs/common.py#L2913-L2917))

By default Tutor implements a single deployment to process tasks on all queues in LMS/CMS. The `CELERY_WORKERS_CONFIG` filter
can be used to add the extra queues from LMS/CMS configuration.

```python

from tutorcelery.hooks import CELERY_WORKERS_CONFIG

@CELERY_WORKERS_CONFIG.add()
def _add_celery_workers_config(workers_config):
    # Adding LMS extra queues
    workers_config["lms"]["high"] = {}  # Make sure to match the key with the queue name: edx.lms.core.high
    workers_config["lms"]["high_mem"] = {}

    # Adding CMS extra queues
    workers_config["cms"]["high"] = {}
    workers_config["cms"]["low"] = {}
    return workers_config
```
With this configuration, 4 new deployments will be created (one for every new queue) to process the tasks
separately according to the queue they are sent to. Additionally, the default Tutor LMS/CMS celery deployments
are patched to ONLY process the tasks sent to the "default" queue.

This is the recommended configuration for a multiqueue approach with LMS and CMS given the queues every
service proposes in its settings files by default. However, the usage of the `CELERY_WORKERS_CONFIG` filter
can be adapted for different configuration scenarios.

This plugin also provides a setting to directly route LMS/CMS tasks to an specific queue. It can extends/overrides
the default `EXPLICIT_QUEUES` setting:

```yaml
CELERY_LMS_EXPLICIT_QUEUES:
  lms.djangoapps.grades.tasks.compute_all_grades_for_course:
    queue: edx.lms.core.high_mem
CELERY_CMS_EXPLICIT_QUEUES:
  cms.djangoapps.contentstore.tasks.import_olx:
    queue: edx.cms.core.high
```

### Custom parameters

Each deployment can be configured to run with different paramaters to override the defaults, the setting `extra_param`
is a list that can be used to pass custom parameters to the Celery workers. e.g changing the Celery's pool parameter
for the high_mem lms worker deployment:

```python
@CELERY_WORKERS_CONFIG.add()
def _add_celery_workers_config(workers_config):
    # Adding LMS extra queues
    workers_config["lms"]["high_mem"]["extra_params"] = {
      "--pool=gevent",
      "--concurrency=100",
    }

    return workers_config
```

### Autoscaling

As an alternative to the CPU/memory based autoscaling offered by the plugin [tutor-contrib-pod-autoscaling](https://github.com/eduNEXT/tutor-contrib-pod-autoscaling),
this plugins supports Celery workers autoscaling based on the size of the celery queue of a given worker. We are using
Keda autoscaling for this purposes, check the [Keda documentation](https://keda.sh/docs) to find out more.

To enable autoscaling you need to enable the `enable_keda` key for every queue variant. The defaults parameters are the following:

```python
{
  "min_replicas": 0,
  "max_replicas": 30,
  "list_length": 40,
  "enable_keda": False,
}
```

> [!NOTE]
> You can use the filter `CELERY_WORKERS_CONFIG` as shown above to modify the scaling parameters for every queue.
> This has been test against Keda v2.15.0 and above.

If you are using [tutor-contrib-pod-autoscaling](https://github.com/eduNEXT/tutor-contrib-pod-autoscaling) and want to setup Keda autoscaling, make sure to disable HPA for the `lms-worker` and the `cms-worker` as **using both autoscalers at the same time is not recommended**.

```python
from tutorpod_autoscaling.hooks import AUTOSCALING_CONFIG

@AUTOSCALING_CONFIG.add()
def _add_my_autoscaling(autoscaling_config):
    autoscaling_config["lms-worker"].update({
      "enable_hpa": False,
    })
    autoscaling_config["cms-worker"].update({
      "enable_hpa": False,
    })
    return autoscaling_config
```

### Enable flower

For troubleshooting purposes, you can enable a flower deployment to monitor in realtime the Celery queues
times and performance:

```yaml
CELERY_FLOWER: true
```

#### Enable Flower Prometheus Integration

If you are running grafana you can use the attached [config map](resources/configmap.yaml) to import a custom Grafana dashboard to monitor
celery metrics such as:

- Total Queue Length
- Queue Length by task name
- Celery Worker Status
- Number of Tasks Currently Executing at Worker
- Average Task Runtime at Worker
- Task Prefetch Time at Worker
- Number of Tasks Prefetched at Worker
- Tasks Success Ratio
- Tasks Failure Ratio

If you are using the [Prometheus Operator](https://github.com/prometheus-operator/prometheus-operator) you can enable a ServiceMonitor resource to automatically configure a scrape target for the flower service.

```yaml
CELERY_FLOWER_SERVICE_MONITOR: true
```

License

---

This software is licensed under the terms of the AGPLv3.
