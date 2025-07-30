"""BaseModule is the abstract base for all modules in the DigitalKin SDK."""

import asyncio
import contextlib
import json
from abc import ABC, abstractmethod
from collections.abc import Callable, Coroutine
from typing import Any, ClassVar, Generic

from pydantic import BaseModel

from digitalkin.grpc_servers.utils.exceptions import OptionalFeatureNotImplementedError
from digitalkin.logger import logger
from digitalkin.models.module import (
    ConfigSetupModelT,
    InputModelT,
    ModuleStatus,
    OutputModelT,
    SecretModelT,
    SetupModelT,
)
from digitalkin.services.agent.agent_strategy import AgentStrategy
from digitalkin.services.cost.cost_strategy import CostStrategy
from digitalkin.services.filesystem.filesystem_strategy import FilesystemStrategy
from digitalkin.services.identity.identity_strategy import IdentityStrategy
from digitalkin.services.registry.registry_strategy import RegistryStrategy
from digitalkin.services.services_config import ServicesConfig, ServicesStrategy
from digitalkin.services.snapshot.snapshot_strategy import SnapshotStrategy
from digitalkin.services.storage.storage_strategy import StorageStrategy
from digitalkin.utils.llm_ready_schema import llm_ready_schema


class ModuleErrorModel(BaseModel):
    """Typed error/code model."""

    code: str
    exception: str
    short_description: str


class BaseModule(
    ABC,
    Generic[
        InputModelT,
        OutputModelT,
        SetupModelT,
        SecretModelT,
        ConfigSetupModelT,
    ],
):
    """BaseModule is the abstract base for all modules in the DigitalKin SDK."""

    name: str
    description: str

    config_setup_format: type[ConfigSetupModelT]
    input_format: type[InputModelT]
    output_format: type[OutputModelT]
    setup_format: type[SetupModelT]
    secret_format: type[SecretModelT]
    metadata: ClassVar[dict[str, Any]]

    # service config params
    services_config_strategies: ClassVar[dict[str, ServicesStrategy | None]]
    services_config_params: ClassVar[dict[str, dict[str, Any | None] | None]]
    services_config: ServicesConfig

    # services list
    agent: AgentStrategy
    cost: CostStrategy
    filesystem: FilesystemStrategy
    identity: IdentityStrategy
    registry: RegistryStrategy
    snapshot: SnapshotStrategy
    storage: StorageStrategy

    def _init_strategies(self) -> None:
        """Initialize the services configuration."""
        for service_name in self.services_config.valid_strategy_names():
            service = self.services_config.init_strategy(service_name, self.mission_id, self.setup_version_id)
            setattr(self, service_name, service)

    def __init__(
        self,
        job_id: str,
        mission_id: str,
        setup_version_id: str,
    ) -> None:
        """Initialize the module."""
        self.job_id: str = job_id
        self.mission_id: str = mission_id
        self.setup_version_id: str = setup_version_id
        self._status = ModuleStatus.CREATED
        self._task: asyncio.Task | None = None
        # Initialize services configuration
        self._init_strategies()

    @property
    def status(self) -> ModuleStatus:
        """Get the module status.

        Returns:
            The module status
        """
        return self._status

    @classmethod
    def get_secret_format(cls, *, llm_format: bool) -> str:
        """Get the JSON schema of the secret format model.

        Raises:
            NotImplementedError: If the `secret_format` is not defined.

        Returns:
            The JSON schema of the secret format as a string.
        """
        if cls.secret_format is not None:
            if llm_format:
                return json.dumps(llm_ready_schema(cls.secret_format), indent=2)
            return json.dumps(cls.secret_format.model_json_schema(), indent=2)
        msg = f"{cls.__name__}' class does not define a 'secret_format'."
        raise NotImplementedError(msg)

    @classmethod
    def get_input_format(cls, *, llm_format: bool) -> str:
        """Get the JSON schema of the input format model.

        Raises:
            NotImplementedError: If the `input_format` is not defined.

        Returns:
            The JSON schema of the input format as a string.
        """
        if cls.input_format is not None:
            if llm_format:
                return json.dumps(llm_ready_schema(cls.input_format), indent=2)
            return json.dumps(cls.input_format.model_json_schema(), indent=2)
        msg = f"{cls.__name__}' class does not define an 'input_format'."
        raise NotImplementedError(msg)

    @classmethod
    def get_output_format(cls, *, llm_format: bool) -> str:
        """Get the JSON schema of the output format model.

        Raises:
            NotImplementedError: If the `output_format` is not defined.

        Returns:
            The JSON schema of the output format as a string.
        """
        if cls.output_format is not None:
            if llm_format:
                return json.dumps(llm_ready_schema(cls.output_format), indent=2)
            return json.dumps(cls.output_format.model_json_schema(), indent=2)
        msg = "'%s' class does not define an 'output_format'."
        raise NotImplementedError(msg)

    @classmethod
    def get_config_setup_format(cls, *, llm_format: bool) -> str:
        """Gets the JSON schema of the config setup format model.

        Raises:
            OptionalFeatureNotImplementedError: If the `config_setup_format` is not defined.

        Returns:
            The JSON schema of the config setup format as a string.
        """
        if cls.config_setup_format is not None:
            if llm_format:
                return json.dumps(llm_ready_schema(cls.config_setup_format), indent=2)
            return json.dumps(cls.config_setup_format.model_json_schema(), indent=2)
        msg = "'%s' class does not define an 'config_setup_format'."
        raise OptionalFeatureNotImplementedError(msg)

    @classmethod
    def get_setup_format(cls, *, llm_format: bool) -> str:
        """Gets the JSON schema of the setup format model.

        Raises:
            NotImplementedError: If the `setup_format` is not defined.

        Returns:
            The JSON schema of the setup format as a string.
        """
        if cls.setup_format is not None:
            if llm_format:
                return json.dumps(llm_ready_schema(cls.setup_format), indent=2)
            return json.dumps(cls.setup_format.model_json_schema(), indent=2)
        msg = "'%s' class does not define an 'setup_format'."
        raise NotImplementedError(msg)

    @classmethod
    def create_config_setup_model(cls, config_setup_data: dict[str, Any]) -> ConfigSetupModelT:
        """Create the setup model from the setup data.

        Args:
            config_setup_data: The setup data to create the model from.

        Returns:
            The setup model.
        """
        return cls.config_setup_format(**config_setup_data)

    @classmethod
    def create_input_model(cls, input_data: dict[str, Any]) -> InputModelT:
        """Create the input model from the input data.

        Args:
            input_data: The input data to create the model from.

        Returns:
            The input model.
        """
        return cls.input_format(**input_data)

    @classmethod
    def create_setup_model(cls, setup_data: dict[str, Any]) -> SetupModelT:
        """Create the setup model from the setup data.

        Args:
            setup_data: The setup data to create the model from.

        Returns:
            The setup model.
        """
        return cls.setup_format(**setup_data)

    @classmethod
    def create_secret_model(cls, secret_data: dict[str, Any]) -> SecretModelT:
        """Create the secret model from the secret data.

        Args:
            secret_data: The secret data to create the model from.

        Returns:
            The secret model.
        """
        return cls.secret_format(**secret_data)

    @classmethod
    def create_output_model(cls, output_data: dict[str, Any]) -> OutputModelT:
        """Create the output model from the output data.

        Args:
            output_data: The output data to create the model from.

        Returns:
            The output model.
        """
        return cls.output_format(**output_data)

    @abstractmethod
    async def run_config_setup(
        self,
        config_setup_data: ConfigSetupModelT,
        setup_data: SetupModelT,
        callback: Callable,
    ) -> None:
        """Run config setup the module.

        Raises:
            OptionalFeatureNotImplementedError: If the config setup feature is not implemented.
        """
        msg = f"'{self}' class does not define an optional 'run_config_setup' attribute."
        raise OptionalFeatureNotImplementedError(msg)

    @abstractmethod
    async def initialize(self, setup_data: SetupModelT) -> None:
        """Initialize the module."""
        raise NotImplementedError

    @abstractmethod
    async def run(
        self,
        input_data: InputModelT,
        setup_data: SetupModelT,
        callback: Callable[[OutputModelT], Coroutine[Any, Any, None]],
    ) -> None:
        """Run the module."""
        raise NotImplementedError

    @abstractmethod
    async def cleanup(self) -> None:
        """Run the module."""
        raise NotImplementedError

    async def _run_lifecycle(
        self,
        input_data: InputModelT,
        setup_data: SetupModelT,
        callback: Callable[[OutputModelT], Coroutine[Any, Any, None]],
    ) -> None:
        """Run the module lifecycle.

        Raises:
            asyncio.CancelledError: If the module is cancelled
        """
        try:
            logger.warning("Starting module %s", self.name)
            await self.run(input_data, setup_data, callback)
            logger.warning("Module %s finished", self.name)
        except asyncio.CancelledError:
            self._status = ModuleStatus.CANCELLED
            logger.error(f"Module {self.name} cancelled")
        except Exception:
            self._status = ModuleStatus.FAILED
            logger.exception("Error inside module %s", self.name)
        else:
            self._status = ModuleStatus.STOPPED
        finally:
            await self.stop()

    async def start(
        self,
        input_data: InputModelT,
        setup_data: SetupModelT,
        callback: Callable[[OutputModelT | ModuleErrorModel], Coroutine[Any, Any, None]],
        done_callback: Callable | None = None,
    ) -> None:
        """Start the module."""
        try:
            logger.info("Inititalize module")
            await self.initialize(setup_data=setup_data)
        except Exception as e:
            self._status = ModuleStatus.FAILED
            short_description = "Error initializing module"
            logger.exception("%s: %s", short_description, e)
            await callback(
                ModuleErrorModel(
                    code=str(self._status),
                    short_description=short_description,
                    exception=str(e),
                )
            )
            if done_callback is not None:
                await done_callback(None)
            await self.stop()
            return

        try:
            logger.info("Run lifecycle")
            self._status = ModuleStatus.RUNNING
            self._task = asyncio.create_task(
                self._run_lifecycle(input_data, setup_data, callback),
                name="module_lifecycle",
            )
            if done_callback is not None:
                self._task.add_done_callback(done_callback)
        except Exception:
            self._status = ModuleStatus.FAILED
            logger.exception("Error during module lifecyle")

    async def stop(self) -> None:
        """Stop the module."""
        if self._status != ModuleStatus.RUNNING:
            return

        try:
            self._status = ModuleStatus.STOPPING
            if self._task and not self._task.done():
                self._task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self._task
            await self.cleanup()
        except Exception:
            self._status = ModuleStatus.FAILED
            logger.exception("Error stopping module")

    async def start_config_setup(
        self,
        config_setup_data: ConfigSetupModelT,
        setup_data: SetupModelT,
        callback: Callable[[OutputModelT | ModuleErrorModel], Coroutine[Any, Any, None]],
    ) -> None:
        """Start the module."""
        try:
            logger.info("Run Config Setup lifecycle")
            self._status = ModuleStatus.RUNNING
            await self.run_config_setup(config_setup_data, setup_data, callback)
        except Exception:
            self._status = ModuleStatus.FAILED
            logger.exception("Error during module lifecyle")
