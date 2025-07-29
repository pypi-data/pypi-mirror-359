
from hequate_common.models import (
        CompilerTaskResult,
        QPUTaskResult)
from .client import QciConnectClient
from .utils import timestamp_to_datetime
from .exceptions import ResultException

import json
import numpy as np

class CompilerResult:
    """
    Result of a compile job.

    Attributes:
        _compiler_task_result: Result as it is returned by the platform parsed by pydantic.
        compiled_circuits: Workaround - we want to return the circuits as a list.
    """
    _compiler_task_result: CompilerTaskResult
    compiled_circuits: list

    def __getattr__(self, attribute):
        """
        Redirects getting of attributes to _compiler_task_result (except for compiled_circuits)
        and at the same time hides all the pydantic attributes from the user.

        Args:
            attribute: Name of attribute to get.

        Returns: attribute.
        """
        if attribute != "compiled_circuits":
            return getattr(self._compiler_task_result, attribute)
        else:
            return self.compiled_circuits

    def __dir__(self):
        """Fixes autocompletion and hides pydantic noise."""
        dir_output = list(self._compiler_task_result.model_fields_set)
        dir_output.append('compiled_circuits')
        dir_output.remove('compiled_circuit')
        return dir_output

    @classmethod
    def from_compiler_task_result(cls, result: CompilerTaskResult):
        """
        Creates CompilerResult from CompilerTaskResult.

        Args:
            result: compiler task result to create compiler result from.

        Returns: Compiler result
        """
        compiler_result = cls()
        compiler_result._compiler_task_result = result
        if isinstance(result.compiled_circuit, list):
            compiler_result.compiled_circuits = result.compiled_circuit
        else:
            compiler_result.compiled_circuits = [result.compiled_circuit]
        return compiler_result

class BackendResult:
    """
    Result of a qpu job.

    Attributes:
        _qpu_task_result: Result as it is returned by the platform parsed by pydantic.
    """
    _qpu_task_result: QPUTaskResult

    def __getattr__(self, attribute):
        """
        Redirects getting of attributes to _qpu_task_result and hides pydantic noise from the user.

        Args:
            attribute: Name of attribute to get.

        Returns: attribute.
        """
        return getattr(self._qpu_task_result, attribute)

    def __dir__(self):
        """Fixes autocompletion and hides pydantic noise."""
        return list(self._qpu_task_result.model_fields_set)

    @classmethod
    def from_qpu_task_result(cls, result: QPUTaskResult):
        """
        Creates BackendResult from QPUTaskResult.

        Args:
            result: QPU task result to create backend result from.

        Returns: backend result
        """
        backend_result = cls()
        backend_result._qpu_task_result = result

        if isinstance(backend_result._qpu_task_result.data, str):
            backend_result._qpu_task_result.data = json.loads(backend_result._qpu_task_result.data)
    
        if type(backend_result._qpu_task_result.data) == dict:
            
            # See whether the data is a dictionary of real valued numpy arrays (e.g. for sampling primitive)
            try:
                backend_result._qpu_task_result.data = {key: np.ndarray(value) for key, value in backend_result._qpu_task_result.data.items()}
            except Exception as e:
                pass

            # Otherwise, try to convert to complex numbers (e.g. necessary for quantum state vectors)
            try:
                backend_result._qpu_task_result.data = {key: complex(value) for key, value in backend_result._qpu_task_result.data.items()}
            except Exception as e:
                pass

        elif type(backend_result._qpu_task_result.data) == list:
            try:
                backend_result._qpu_task_result.data = np.ndarray(backend_result._qpu_task_result.data)
            except:
                pass

        else:
            raise ResultException(f"Unexpected data type of backend_result._qpu_task_result.data: {type(backend_result._qpu_task_result.data)}")

        try:
            backend_result._qpu_task_result.start_date_time = timestamp_to_datetime(backend_result._qpu_task_result.start_date_time)
            backend_result._qpu_task_result.end_date_time = timestamp_to_datetime(backend_result._qpu_task_result.end_date_time)
        except:
            pass
        
        return backend_result

class FutureResult:
    """
    Object that can be used to poll/retrieve the result of an job.

    Attributes:
        status: status of the job.
        result: Result as it is returned by the platform parsed by pydantic.
    """
    def __init__(self, job_id: str, client: QciConnectClient):
        self._client = client
        self._job_id = job_id
        self._result = None
        self.update()

    @property
    def job_id(self) -> str:
        return self._job_id

    @property
    def status(self) -> str:
        if not self._result:
            self.update()
        return self._status

    def update(self):
        """
        Updates status of the job and retrieves result if job has finished.
        """
        self._status = self._client.get_job_status(self._job_id)
        self._result = self._client.retrieve_result(self._job_id)

class FutureBackendResult(FutureResult):
    @property
    def result(self) -> BackendResult | None:
        """
        Updates future and returns BackendResult if ready.

        Returns: BackendResult object.
        """
        if not self._result:
            self.update()
        if self._result:
            return BackendResult.from_qpu_task_result(self._result.last_qpu_result)
        return None

class FutureCompilerResult(FutureResult):
    @property
    def result(self) -> CompilerResult | None:
        """
        Updates future and returns CompilerResult if ready.

        Returns: BackendResult object.
        """
        if not self._result:
            self.update()
        if self._result:
            return CompilerResult.from_compiler_task_result(self._result.last_compiler_result)
        return None


class Results(dict):
    def __init__(self, client: QciConnectClient):
        self._client = client

    def __dir__(self):
        self._update_results()
        return super().__dir__()

    def _update_results(self):
        super().clear()
        jobs = self._client.get_jobs()
        for job in jobs:
            self._update_result(job)

    def _update_result(self, job):
        if job['status'] == "SUCCESS":
            job_id = job['job_id']
            if job['last_compiler_task'] is not None:
                super().__setitem__(job_id, CompilerResult)
            if job['last_qpu_task'] is not None:
                super().__setitem__(job_id, BackendResult)

    def __getitem__(self, key: str) -> BackendResult | CompilerResult | None:

        if key not in self:
            job = self._client.get_job(key)
            job['job_id'] = key
            self._update_result(job)
        if key not in self:
            return None

        if super().__getitem__(key) == BackendResult:
            super().__setitem__(key, BackendResult.from_qpu_task_result(self._client.retrieve_result(key).last_qpu_result))
        elif super().__getitem__(key) == CompilerResult:
            super().__setitem__(key, CompilerResult.from_compiler_task_result(self._client.retrieve_result(key).last_compiler_result))
        return super().__getitem__(key)

    def get_status(self, job_id: str):
        pass

    def refresh(self):
        self._update_results()

