import logging
import time

from bunch_py3 import Bunch, bunchify

from causalbench.commons.hwinfo import hwinfo
from causalbench.commons.utils import parse_arguments, package_module, causal_bench_path
from causalbench.modules.scenario import Scenario
from causalbench.modules.dataset import Dataset
from causalbench.modules.metric import Metric
from causalbench.modules.model import Model
from causalbench.modules.module import Module
from causalbench.modules.run import Run
from causalbench.modules.task import Task
from causalbench.services.requests import save_module, fetch_module


class Context(Module):

    def __init__(self, module_id: int = None, version: int = None, zip_file: str = None):
        super().__init__(module_id, version, zip_file)

    def __getstate__(self):
        state = super().__getstate__()

        if 'datasets' in state:
            for dataset in state.datasets:
                if 'object' in dataset:
                    del dataset.object

        if 'models' in state:
            for model in state.models:
                if 'object' in model:
                    del model.object

        if 'metrics' in state:
            for metric in state.metrics:
                if 'object' in metric:
                    del metric.object

        return state

    def validate(self):
        # TODO: To be implemented
        pass

    def fetch(self):
        return fetch_module(self.type,
                            self.module_id,
                            self.version,
                            'pipelines',
                            'downloaded_context.zip')

    def save(self, state, public: bool = False) -> bool:
        for dataset in state.datasets:
            if dataset.id is None:
                logging.error('Cannot publish context as it contains unpublished dataset')
                return False

        for model in state.models:
            if model.id is None:
                logging.error('Cannot publish context as it contains unpublished model')
                return False

        for metric in state.metrics:
            if metric.id is None:
                logging.error('Cannot publish context as it contains unpublished metric')
                return False

        zip_file = package_module(state, self.package_path)
        self.module_id, self.version = save_module(self.type,
                                                   self.module_id,
                                                   self.version,
                                                   public,
                                                   zip_file,
                                                   'pipelines',
                                                   'context.zip')
        return self.module_id is not None

    def execute(self) -> Run | None:
        # execution start time
        start_time = time.time_ns()

        # load the task
        task: Task = Task(module_id=self.task)

        # load the datasets
        datasets = []
        for dataset in self.datasets:
            if 'object' not in dataset:
                dataset.object = Dataset(module_id=dataset.id, version=dataset.version)
            datasets.append((dataset.object, dataset.mapping))

        # load the models
        models = []
        for model in self.models:
            if 'object' not in model:
                model.object = Model(module_id=model.id, version=model.version)
            models.append((model.object, model.hyperparameters))

        # load the metrics
        metrics = []
        for metric in self.metrics:
            if 'object' not in metric:
                metric.object = Metric(module_id=metric.id, version=metric.version)
            metrics.append((metric.object, metric.hyperparameters))

        # create the scenarios
        scenarios = []
        for dataset in datasets:
            for model in models:
                scenario = Scenario(task, dataset, model, metrics)
                scenarios.append(scenario)

        # execute the scenarios
        results = []
        for scenario in scenarios:
            results.append(scenario.execute())

        # execution end time
        end_time = time.time_ns()

        # create run
        run: Run = Run()

        # context
        run.context = Bunch()
        run.context.id = self.module_id
        run.context.version = self.version
        run.context.name = self.name

        # task
        run.task = self.task

        # results
        run.results = results

        # timing
        run.time = Bunch()
        run.time.start = start_time
        run.time.end = end_time
        run.time.duration = end_time - start_time

        # hardware
        run.profiling = hwinfo()

        # convert results to string for human readability
        for result in run.results:
            for output, value in result.model.output.items():
                result.model.output[output] = str(value)

            for metric in result.metrics:
                for output, value in metric.output.items():
                    metric.output[output] = str(value)

        return run

    def __instantiate(self, arguments: Bunch):
        # module ID
        if 'module_id' in arguments:
            self.module_id = arguments.module_id

        # version
        if 'version' in arguments:
            self.version = arguments.version

        # metadata
        self.name = arguments.name
        self.description = arguments.description
        self.task = arguments.task

        # convert datasets to config format
        self.datasets = []
        if isinstance(arguments.datasets, list):
            for dataset in arguments.datasets:
                self_dataset = Bunch()
                self.datasets.append(self_dataset)

                if isinstance(dataset, tuple):
                    # dataset
                    if isinstance(dataset[0], Dataset):
                        self_dataset.id = dataset[0].module_id
                        self_dataset.version = dataset[0].version
                        self_dataset.object = dataset[0]
                    else:
                        raise ValueError('Invalid dataset instance')

                    # data mapping
                    if isinstance(dataset[1], Bunch):
                        self_dataset.mapping = dataset[1]
                    elif isinstance(dataset[1], dict):
                        self_dataset.mapping = bunchify(dataset[1])
                    else:
                        raise ValueError('Invalid data mapping')
                else:
                    raise ValueError('Invalid dataset definition')
        else:
            raise ValueError('Invalid dataset definition')

        # convert models to config format
        self.models = []
        if isinstance(arguments.models, list):
            for model in arguments.models:
                self_model = Bunch()
                self.models.append(self_model)

                if isinstance(model, tuple):
                    # model
                    if isinstance(model[0], Model):
                        self_model.id = model[0].module_id
                        self_model.version = model[0].version
                        self_model.object = model[0]

                        self_model.hyperparameters = Bunch()
                        if hasattr(model[0], 'hyperparameters'):
                            for hyperparameter, defaults in model[0].hyperparameters.items():
                                self_model.hyperparameters[hyperparameter] = defaults.value
                    else:
                        raise ValueError('Invalid model instance')

                    # hyperparameter mapping
                    if isinstance(model[1], dict):
                        for hyperparameter, value in model[1].items():
                            if hyperparameter in self_model.hyperparameters:
                                self_model.hyperparameters[hyperparameter] = value
                            else:
                                raise ValueError(f'Unknown model hyperparameter {hyperparameter}')
                    else:
                        raise ValueError('Invalid model hyperparameter mapping')
                else:
                    raise ValueError('Invalid model definition')
        else:
            raise ValueError('Invalid model definition')

        # convert metrics to config format
        self.metrics = []
        if isinstance(arguments.metrics, list):
            for metric in arguments.metrics:
                self_metric = Bunch()
                self.metrics.append(self_metric)

                if isinstance(metric, tuple):
                    # metric
                    if isinstance(metric[0], Metric):
                        self_metric.id = metric[0].module_id
                        self_metric.version = metric[0].version
                        self_metric.object = metric[0]

                        self_metric.hyperparameters = Bunch()
                        if hasattr(metric[0], 'hyperparameters'):
                            for hyperparameter, defaults in metric[0].hyperparameters.items():
                                self_metric.hyperparameters[hyperparameter] = defaults.value
                    else:
                        raise ValueError('Invalid metric instance')

                    # hyperparameter mapping
                    if isinstance(metric[1], dict):
                        for hyperparameter, value in metric[1].items():
                            if hyperparameter in self_metric.hyperparameters:
                                self_metric.hyperparameters[hyperparameter] = value
                            else:
                                raise ValueError(f'Unknown metric hyperparameter {hyperparameter}')
                    else:
                        raise ValueError('Invalid metric hyperparameter mapping')
                else:
                    raise ValueError('Invalid metric definition')
        else:
            raise ValueError('Invalid metric definition')

        # form the directory path
        self.package_path = causal_bench_path(self.type, self.name)

    @staticmethod
    def create(*args, **keywords):
        # parse arguments
        arguments = parse_arguments(args, keywords)

        # create the instance
        context = Context()
        context.__instantiate(arguments)
        return context
