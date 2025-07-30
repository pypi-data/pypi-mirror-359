"""TriggerModule extends BaseModule to implement specific module types."""

from abc import ABC

from digitalkin.models.module.module_types import ConfigSetupModelT
from digitalkin.modules._base_module import BaseModule, InputModelT, OutputModelT, SecretModelT, SetupModelT


class TriggerModule(BaseModule[InputModelT, OutputModelT, SetupModelT, SecretModelT,
        ConfigSetupModelT,], ABC):
    """TriggerModule extends BaseModule to implement specific module types."""
