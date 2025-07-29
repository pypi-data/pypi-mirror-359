# -*- coding: utf-8 -*-
"""
---------------------------------------------
Copyright (c) 2025 ZhangYundi
Licensed under the MIT License.
Created on 2025/6/25 15:05
Email: yundi.xxii@outlook.com
Description: 主流程控制
---------------------------------------------
"""
from collections.abc import Sequence

import mlflow
import ygo
import ylog
from omegaconf import DictConfig, OmegaConf
from sklearn.base import BaseEstimator
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from .data import DataLoader
from .pipeline import IncrementalPipeline
from .trainer import BaseIncrementalTrainer
from .utils import extract_feature_names, get_timedelta_names, is_notebook, hydra_wrapper


class WorkFlow(BaseEstimator):
    """
    构建 训练工作流: 从数据加载->预处理->增量训练。支持 sklearn式更改配置、从配置文件中加载
    """

    def __init__(self,
                 data: list,
                 trainer: BaseIncrementalTrainer,
                 preprocessor: list | None = None,
                 trainer_params: dict | None = None):
        """
        构造工作流

        Parameters
        ----------
        data: list
            数据加载步骤
        trainer: BaseIncrementalTrainer
            训练器：quda.ml.trainer.BaseIncrementalTrainer 的实现实例
        preprocessor: list
            预处理步骤，默认None: 不做预处理
        trainer_params:
            训练器参数
        """
        # 初始化
        self.data = DataLoader(steps=data)
        self.trainer = trainer
        if isinstance(self.trainer, type):
            self.trainer = self.trainer()
        assert isinstance(self.trainer,
                          BaseIncrementalTrainer), "trainer must be a subclass of `BaseIncrementalTrainer`"
        self.trainer_params = trainer_params
        self.preprocessor = IncrementalPipeline(preprocessor) if preprocessor else None
        self.pipe = Pipeline([
            ("data", self.data.pipe),
            ("trainer", self.trainer)
        ])
        if self.preprocessor:
            self.pipe.steps.insert(1, ("preprocessor", self.preprocessor.pipe))

        self._html_repr = self.pipe._html_repr

    @classmethod
    def initialize(cls, cfg: DictConfig):
        """
        从 解析出来的 初始化 workflow
        """

        from hydra.utils import instantiate

        # 构建 data pipeline
        data_steps = []
        data_steps = instantiate(cfg.data)
        data_steps = [(name, step) for d in data_steps for name, step in d.items()]

        # 构建 preprocessor
        preprocessor_steps = None
        if cfg.get("preprocessor"):
            preprocessor_steps = []
            preprocessor_steps = instantiate(cfg.preprocessor)
            preprocessor_steps = [(name, step) for d in preprocessor_steps for name, step in d.items()]

        # 构建 trainer
        trainer = instantiate(cfg.trainer.trainer)

        # trainer_params
        trainer_params = instantiate(cfg.trainer.trainer_params)
        trainer_params = OmegaConf.to_container(trainer_params, resolve=True)

        wf = cls(data=data_steps,
                 trainer=trainer,
                 preprocessor=preprocessor_steps,
                 trainer_params=trainer_params)
        return wf

    @classmethod
    def from_conf(cls, config_path: str = "conf", config_name: str = "config") -> 'WorkFlow':
        """
        配置驱动:从配置文件中构建工作流


        Examples
        --------
        >>> import quda.ml
        >>> workflow = quda.ml.WorkFlow.from_conf(config_path='conf', config_name="config")
        >>> workflow.set_params(...) # 更改配置
        >>> workflow.fit(...) # 开始训练

        Returns
        -------
        """
        if is_notebook():
            print(f"""Run in notebook, please use hydra to run.
::code::
from hydra import initialize, compose
with initialize(version_base=None, config_path='{config_path}'):
    cfg = compose(config_name='{config_name}')
wf = quda.ml.WorkFlow.initialize(cfg)
""")
            return

        hydra_main = hydra_wrapper(config_path, config_name)
        if hydra_main is not None:
            return hydra_main(cls.initialize)()

    def fit(self,
            iterables: Sequence,
            batch_size: int = -1,
            features: list[str] | None = None,
            valid_size: float = 0.2,
            shuffle: bool = False,
            random_state: int = 42, ):
        """
        通用增量训练流程，支持分批加载数据,预处理，模型训练与保存

        Parameters
        ----------
        iterables: Sequence
            可迭代对象
        batch_size: int
            每次训练的批次，默认 -1: 全量训练
        features: list[str]|None
            特征名, 默认None。会排除date,time,asset,price,以timedelta命名的收益列
        valid_size: float
            验证集比例，默认0.2
        shuffle: bool
            是否打乱 iterables, 默认 False
        random_state: int
            随机数种子，默认 42
        Returns
        -------

        """
        batch_size = batch_size if batch_size > 0 else len(iterables)
        iterables = sorted(iterables)

        mlflow.autolog()
        mlflow.sklearn.autolog(disable=True)

        with mlflow.start_run() as top_run:
            top_run_id = top_run.info.run_id
            ylog.info(f"Started mlflow.run: {top_run_id}")
            params = {
                "data.beg": iterables[0],
                "data.end": iterables[-1],
                "batch_size": batch_size,
                "shuffle": shuffle,
                "random_state": random_state,
            }
            mlflow.log_params(params, run_id=top_run_id)
            train_batch_list = [iterables[i:i + batch_size] for i in range(0, len(iterables), batch_size)]
            for i, train_batch in enumerate(train_batch_list):
                beg, end = train_batch[0], train_batch[-1]
                evals_result = {}
                with mlflow.start_run(nested=True, ) as partial_run:
                    # mlflow.lightgbm.autolog()
                    partial_run_id = partial_run.info.run_id
                    ylog.info(f"Started mlflow.run: {partial_run_id}")
                    ylog.info(f"Preparing on batch_{i + 1}({i + 1}/{len(train_batch_list)}) - {beg} >>> {end}")
                    params["data.beg"] = beg
                    params["data.end"] = end
                    mlflow.log_params(params, run_id=partial_run_id)
                    # 加载训练数据
                    train_list_, valid_list_ = train_test_split(train_batch,
                                                                test_size=valid_size,
                                                                shuffle=shuffle,
                                                                random_state=random_state)
                    train_dl = self.data.fetch(train_list_, batch_size=batch_size, show_progress=False)
                    train_data = next(train_dl)
                    if self.preprocessor:
                        train_data = self.preprocessor.partial_fit_transform(train_data)
                    if valid_list_:
                        valid_dl = self.data.fetch(valid_list_, batch_size=batch_size, show_progress=False)
                        valid_data = next(valid_dl)
                        if self.preprocessor:
                            valid_data = self.preprocessor.fit_transform(valid_data)
                    else:
                        valid_data = None

                    if not features:
                        features = extract_feature_names(train_data.columns)
                    else:
                        features = features
                    if self.trainer.input_example is None:
                        self.trainer.input_example = train_data[features].head().to_pandas()
                    target = get_timedelta_names(train_data.columns)
                    if len(target) >= 1:
                        ylog.info(f"Target column found: {target}, use {target[0]}")
                    else:
                        raise ValueError("Miss target columns in data")

                    target = target[0]

                    ylog.info("Building dataset.train...")
                    train_data = self.trainer.create_dataset(data=train_data,
                                                             features=features,
                                                             target=target, )

                    if valid_data is not None:
                        ylog.info("Building dataset.valid...")
                        valid_data = self.trainer.create_dataset(data=valid_data,
                                                                 features=features,
                                                                 target=target, )

                    ylog.info(f"Training on batch_{i + 1}({i + 1}/{len(train_batch_list)}) - {beg} >>> {end}")

                    # 训练模型
                    self.trainer.fit(train_data=train_data,
                                     valid_data=valid_data,
                                     init_model=self.trainer.model,
                                     evals_result=evals_result,
                                     **self.trainer_params)

                    # 保存模型
                    # model_name = f"checkpoint_{i + 1}"
                    # model_info = self.trainer.save_model(model, model_name, )
                    # self.trainer.model = mlflow.pyfunc.load_model(model_info.model_uri)
                    self.trainer.model = mlflow.pyfunc.load_model(f"runs:/{partial_run_id}/model")

                    model = None

    @classmethod
    def run(cls, cfg: DictConfig) -> 'WorkFlow':
        """
        从解析后的config运行配置
        Returns
        -------
        """
        wf = cls.initialize(cfg)
        sig_params = ygo.fn_signature_params(wf.fit)
        params = {k: v for k, v in cfg.items() if k in sig_params}
        if params:
            from hydra.utils import instantiate
            params = instantiate(params)
        return wf.fit(**params)

    @classmethod
    def run_conf(cls, config_path: str = "conf", config_name: str = "config", ):
        """
        从配置文件中创建 WorkFlow 对象，并且运行 fit
        Returns
        -------

        """

        if is_notebook():
            print(f"""Run in notebook, please use hydra to run.
::code::
from hydra import initialize, compose
with initialize(version_base=None, config_path='{config_path}'):
    cfg = compose(config_name='{config_name}')
quda.ml.WorkFlow.run(cfg)
""")
            return
        hydra_main = hydra_wrapper(config_path, config_name)
        if hydra_main is not None:
            return hydra_main(cls.run)()

