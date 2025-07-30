from enum import Enum
from typing import Optional, Union

from .base import BaseModel
from .constant import ConstantModel
from .joint import JointModel
from .lme import LMEModel
from .riemanian_manifold import LinearModel, LogisticModel
from .shared_speed_logistic import SharedSpeedLogisticModel

__all__ = [
    "ModelName",
    "model_factory",
]


class ModelName(str, Enum):
    """The available models that users can instantiate in Leaspy."""

    JOINT = "joint"
    LOGISTIC = "logistic"
    LINEAR = "linear"
    SHARED_SPEED_LOGISTIC = "shared_speed_logistic"
    LME = "lme"
    CONSTANT = "constant"


def model_factory(
    name: Union[str, ModelName], instance_name: Optional[str] = None, **kwargs
) -> BaseModel:
    """
    Return the model object corresponding to ``name`` arg with possible ``kwargs``.

    Parameters
    ----------
    name : str or ModelName
        The name of the model class to be instantiated.

    instance_name : str, optional
        The custom name of the instance to be created.
        If not provided, it will be the model class name.

    **kwargs
        Contains model's hyper-parameters.
        Raise an error if the keyword is inappropriate for the given model's name.

    Returns
    -------
    :class:`.BaseModel`
        A child class object of :class:`.models.BaseModel` class object determined by ``name``.
    """
    name = ModelName(name)
    instance_name = instance_name or name.value
    if name == ModelName.JOINT:
        return JointModel(instance_name, **kwargs)
    if name == ModelName.LOGISTIC:
        return LogisticModel(instance_name, **kwargs)
    if name == ModelName.LINEAR:
        return LinearModel(instance_name, **kwargs)
    if name == ModelName.SHARED_SPEED_LOGISTIC:
        return SharedSpeedLogisticModel(instance_name, **kwargs)
    if name == ModelName.LME:
        return LMEModel(instance_name, **kwargs)
    if name == ModelName.CONSTANT:
        return ConstantModel(instance_name, **kwargs)
