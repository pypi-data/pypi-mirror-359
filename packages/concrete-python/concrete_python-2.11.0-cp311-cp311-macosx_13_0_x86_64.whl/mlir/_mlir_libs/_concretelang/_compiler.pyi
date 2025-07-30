import numpy
from typing import ClassVar, overload

AUTO: Encoding
BOOTSTRAP: KeyType
CLEAR_ADDITION: PrimitiveOperation
CLEAR_MULTIPLICATION: PrimitiveOperation
CPU: Backend
CRT: Encoding
DAG_MONO: OptimizerStrategy
DAG_MULTI: OptimizerStrategy
ENCRYPTED_ADDITION: PrimitiveOperation
ENCRYPTED_NEGATION: PrimitiveOperation
GPU: Backend
KEY_SWITCH: KeyType
NATIVE: Encoding
PACKING_KEY_SWITCH: KeyType
PBS: PrimitiveOperation
PRECISION: OptimizerMultiParameterStrategy
PRECISION_AND_NORM2: OptimizerMultiParameterStrategy
SECRET: KeyType
V0: OptimizerStrategy
WOP_PBS: PrimitiveOperation

class Backend:
    __members__: ClassVar[dict] = ...  # read-only
    CPU: ClassVar[Backend] = ...
    GPU: ClassVar[Backend] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: mlir._mlir_libs._concretelang._compiler.Backend, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: mlir._mlir_libs._concretelang._compiler.Backend) -> int"""
    def __int__(self) -> int:
        """__int__(self: mlir._mlir_libs._concretelang._compiler.Backend) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class BootstrapKeyParam:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    def base_log(self) -> int:
        """base_log(self: mlir._mlir_libs._concretelang._compiler.BootstrapKeyParam) -> int

        Return the associated base log.
        """
    def glwe_dimension(self) -> int:
        """glwe_dimension(self: mlir._mlir_libs._concretelang._compiler.BootstrapKeyParam) -> int

        Return the associated GLWE dimension.
        """
    def input_lwe_dimension(self) -> int:
        """input_lwe_dimension(self: mlir._mlir_libs._concretelang._compiler.BootstrapKeyParam) -> int

        Return the associated input lwe dimension.
        """
    def input_secret_key_id(self) -> int:
        """input_secret_key_id(self: mlir._mlir_libs._concretelang._compiler.BootstrapKeyParam) -> int

        Return the key id of the associated input key.
        """
    def level(self) -> int:
        """level(self: mlir._mlir_libs._concretelang._compiler.BootstrapKeyParam) -> int

        Return the associated number of levels.
        """
    def output_secret_key_id(self) -> int:
        """output_secret_key_id(self: mlir._mlir_libs._concretelang._compiler.BootstrapKeyParam) -> int

        Return the key id of the associated output key.
        """
    def polynomial_size(self) -> int:
        """polynomial_size(self: mlir._mlir_libs._concretelang._compiler.BootstrapKeyParam) -> int

        Return the associated polynomial size.
        """
    def variance(self) -> float:
        """variance(self: mlir._mlir_libs._concretelang._compiler.BootstrapKeyParam) -> float

        Return the associated noise variance.
        """
    def __eq__(self, arg0: BootstrapKeyParam) -> bool:
        """__eq__(self: mlir._mlir_libs._concretelang._compiler.BootstrapKeyParam, arg0: mlir._mlir_libs._concretelang._compiler.BootstrapKeyParam) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __ne__(self, arg0: BootstrapKeyParam) -> bool:
        """__ne__(self: mlir._mlir_libs._concretelang._compiler.BootstrapKeyParam, arg0: mlir._mlir_libs._concretelang._compiler.BootstrapKeyParam) -> bool"""

class CircuitCompilationFeedback:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    @property
    def crt_decompositions_of_outputs(self) -> list[list[int]]: ...
    @property
    def memory_usage_per_location(self) -> dict[str, int | None]: ...
    @property
    def name(self) -> str: ...
    @property
    def statistics(self) -> list[Statistic]: ...
    @property
    def total_inputs_size(self) -> int: ...
    @property
    def total_output_size(self) -> int: ...

class CircuitInfo:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    def get_inputs(self) -> list[GateInfo]:
        """get_inputs(self: mlir._mlir_libs._concretelang._compiler.CircuitInfo) -> List[mlir._mlir_libs._concretelang._compiler.GateInfo]

        Return the input gates
        """
    def get_name(self) -> str:
        """get_name(self: mlir._mlir_libs._concretelang._compiler.CircuitInfo) -> str

        Return the name of the circuit
        """
    def get_outputs(self) -> list[GateInfo]:
        """get_outputs(self: mlir._mlir_libs._concretelang._compiler.CircuitInfo) -> List[mlir._mlir_libs._concretelang._compiler.GateInfo]

        Return the output gates
        """

class ClientCircuit:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    def prepare_input(self, arg: Value, pos: int) -> TransportValue:
        """prepare_input(self: mlir._mlir_libs._concretelang._compiler.ClientCircuit, arg: mlir._mlir_libs._concretelang._compiler.Value, pos: int) -> mlir._mlir_libs._concretelang._compiler.TransportValue

        Prepare a `pos` positional arguments `arg` to be sent to server. 
        """
    def process_output(self, result: TransportValue, pos: int) -> Value:
        """process_output(self: mlir._mlir_libs._concretelang._compiler.ClientCircuit, result: mlir._mlir_libs._concretelang._compiler.TransportValue, pos: int) -> mlir._mlir_libs._concretelang._compiler.Value

        Process a `pos` positional result `result` retrieved from server. 
        """
    def simulate_prepare_input(self, arg: Value, pos: int) -> TransportValue:
        """simulate_prepare_input(self: mlir._mlir_libs._concretelang._compiler.ClientCircuit, arg: mlir._mlir_libs._concretelang._compiler.Value, pos: int) -> mlir._mlir_libs._concretelang._compiler.TransportValue

        SIMULATE preparation of `pos` positional argument `arg` to be sent to server. DOES NOT NCRYPT.
        """
    def simulate_process_output(self, result: TransportValue, pos: int) -> Value:
        """simulate_process_output(self: mlir._mlir_libs._concretelang._compiler.ClientCircuit, result: mlir._mlir_libs._concretelang._compiler.TransportValue, pos: int) -> mlir._mlir_libs._concretelang._compiler.Value

        SIMULATE processing of `pos` positional result `result` retrieved from server.
        """

class ClientKeyset:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    def get_secret_keys(self) -> list[LweSecretKey]:
        """get_secret_keys(self: mlir._mlir_libs._concretelang._compiler.ClientKeyset) -> List[mlir._mlir_libs._concretelang._compiler.LweSecretKey]"""

class ClientProgram:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    @staticmethod
    def create_encrypted(program_info: ProgramInfo, keyset: Keyset) -> ClientProgram:
        """create_encrypted(program_info: mlir._mlir_libs._concretelang._compiler.ProgramInfo, keyset: mlir._mlir_libs._concretelang._compiler.Keyset) -> mlir._mlir_libs._concretelang._compiler.ClientProgram

        Create an encrypted (as opposed to simulated) ClientProgram.
        """
    @staticmethod
    def create_simulated(program_info: ProgramInfo) -> ClientProgram:
        """create_simulated(program_info: mlir._mlir_libs._concretelang._compiler.ProgramInfo) -> mlir._mlir_libs._concretelang._compiler.ClientProgram

        Create a simulated (as opposed to encrypted) ClientProgram. DOES NOT PERFORM ENCRYPTION OF VALUES.
        """
    def get_client_circuit(self, circuit: str) -> ClientCircuit:
        """get_client_circuit(self: mlir._mlir_libs._concretelang._compiler.ClientProgram, circuit: str) -> mlir._mlir_libs._concretelang._compiler.ClientCircuit

        Return the `circuit` ClientCircuit.
        """

class CompilationContext:
    def __init__(self) -> None:
        """__init__(self: mlir._mlir_libs._concretelang._compiler.CompilationContext) -> None"""
    def mlir_context(self) -> object:
        """mlir_context(self: mlir._mlir_libs._concretelang._compiler.CompilationContext) -> object"""

class CompilationOptions:
    def __init__(self, backend: Backend) -> None:
        """__init__(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, backend: mlir._mlir_libs._concretelang._compiler.Backend) -> None"""
    def add_composition(self, from_func: str, from_pos: int, to_func: str, to_pos: int) -> None:
        """add_composition(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, from_func: str, from_pos: int, to_func: str, to_pos: int) -> None

        Add a composition rule.
        """
    def force_encoding(self, encoding: Encoding) -> None:
        """force_encoding(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, encoding: mlir._mlir_libs._concretelang._compiler.Encoding) -> None

        Force the compiler to use a specific encoding.
        """
    def set_all_v0_parameter(self, glwe_dimension: int, log_poly_size: int, n_small: int, br_level: int, br_log_base: int, ks_level: int, ks_log_base: int, crt_decomp: list[int], cbs_level: int, cbs_log_base: int, pks_level: int, pks_log_base: int, pks_input_lwe_dim: int, pks_output_poly_size: int) -> None:
        """set_all_v0_parameter(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, glwe_dimension: int, log_poly_size: int, n_small: int, br_level: int, br_log_base: int, ks_level: int, ks_log_base: int, crt_decomp: List[int], cbs_level: int, cbs_log_base: int, pks_level: int, pks_log_base: int, pks_input_lwe_dim: int, pks_output_poly_size: int) -> None

        Set all the V0 parameters.
        """
    def set_auto_parallelize(self, auto_parallelize: bool) -> None:
        """set_auto_parallelize(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, auto_parallelize: bool) -> None

        Set option for auto parallelization.
        """
    def set_batch_tfhe_ops(self, batch_tfhe_ops: bool) -> None:
        """set_batch_tfhe_ops(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, batch_tfhe_ops: bool) -> None

        Set flag that triggers the batching of scalar TFHE operations.
        """
    def set_composable(self, composable: bool) -> None:
        """set_composable(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, composable: bool) -> None

        Set composable flag.
        """
    def set_compress_evaluation_keys(self, compress_evaluation_keys: bool) -> None:
        """set_compress_evaluation_keys(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, compress_evaluation_keys: bool) -> None

        Set option for compression of evaluation keys.
        """
    def set_compress_input_ciphertexts(self, compress_input_ciphertexts: bool) -> None:
        """set_compress_input_ciphertexts(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, compress_input_ciphertexts: bool) -> None

        Set option for compression of input ciphertexts.
        """
    def set_dataflow_parallelize(self, dataflow_parallelize: bool) -> None:
        """set_dataflow_parallelize(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, dataflow_parallelize: bool) -> None

        Set option for dataflow parallelization.
        """
    def set_display_optimizer_choice(self, display: bool) -> None:
        """set_display_optimizer_choice(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, display: bool) -> None

        Set display flag of optimizer choices.
        """
    def set_emit_gpu_ops(self, emit_gpu_ops: bool) -> None:
        """set_emit_gpu_ops(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, emit_gpu_ops: bool) -> None

        Set flag that allows gpu ops to be emitted.
        """
    def set_enable_overflow_detection_in_simulation(self, enable_overflow_detection: bool) -> None:
        """set_enable_overflow_detection_in_simulation(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, enable_overflow_detection: bool) -> None

        Enable or disable overflow detection during simulation.
        """
    def set_enable_tlu_fusing(self, enable_tlu_fusing: bool) -> None:
        """set_enable_tlu_fusing(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, enable_tlu_fusing: bool) -> None

        Enable or disable tlu fusing.
        """
    def set_global_p_error(self, global_p_error: float) -> None:
        """set_global_p_error(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, global_p_error: float) -> None

        Set global error probability for the full circuit.
        """
    def set_keyset_restriction(self, arg0: KeysetRestriction) -> None:
        """set_keyset_restriction(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, arg0: mlir._mlir_libs._concretelang._compiler.KeysetRestriction) -> None"""
    def set_loop_parallelize(self, loop_parallelize: bool) -> None:
        """set_loop_parallelize(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, loop_parallelize: bool) -> None

        Set option for loop parallelization.
        """
    def set_optimize_concrete(self, optimize: bool) -> None:
        """set_optimize_concrete(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, optimize: bool) -> None

        Set flag to enable/disable optimization of concrete intermediate representation.
        """
    def set_optimizer_multi_parameter_strategy(self, strategy: OptimizerMultiParameterStrategy) -> None:
        """set_optimizer_multi_parameter_strategy(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, strategy: mlir._mlir_libs._concretelang._compiler.OptimizerMultiParameterStrategy) -> None

        Set the strategy of the optimizer for multi-parameter.
        """
    def set_optimizer_strategy(self, strategy: OptimizerStrategy) -> None:
        """set_optimizer_strategy(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, strategy: mlir._mlir_libs._concretelang._compiler.OptimizerStrategy) -> None

        Set the strategy of the optimizer.
        """
    def set_p_error(self, p_error: float) -> None:
        """set_p_error(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, p_error: float) -> None

        Set error probability for shared by each pbs.
        """
    def set_print_tlu_fusing(self, print_tlu_fusing: bool) -> None:
        """set_print_tlu_fusing(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, print_tlu_fusing: bool) -> None

        Enable or disable printing tlu fusing.
        """
    def set_range_restriction(self, arg0: RangeRestriction) -> None:
        """set_range_restriction(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, arg0: mlir._mlir_libs._concretelang._compiler.RangeRestriction) -> None"""
    def set_security_level(self, security_level: int) -> None:
        """set_security_level(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, security_level: int) -> None

        Set security level.
        """
    def set_v0_parameter(self, glwe_dimension: int, log_poly_size: int, n_small: int, br_level: int, br_log_base: int, ks_level: int, ks_log_base: int) -> None:
        """set_v0_parameter(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, glwe_dimension: int, log_poly_size: int, n_small: int, br_level: int, br_log_base: int, ks_level: int, ks_log_base: int) -> None

        Set the basic V0 parameters.
        """
    def set_verify_diagnostics(self, verify_diagnostics: bool) -> None:
        """set_verify_diagnostics(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, verify_diagnostics: bool) -> None

        Set option for diagnostics verification.
        """
    def simulation(self, simulate: bool) -> None:
        """simulation(self: mlir._mlir_libs._concretelang._compiler.CompilationOptions, simulate: bool) -> None

        Enable or disable simulation.
        """

class Compiler:
    def __init__(self, output_path: str, runtime_lib_path: str, generate_shared_lib: bool = ..., generate_static_lib: bool = ..., generate_program_info: bool = ..., generate_compilation_feedback: bool = ...) -> None:
        """__init__(self: mlir._mlir_libs._concretelang._compiler.Compiler, output_path: str, runtime_lib_path: str, generate_shared_lib: bool = True, generate_static_lib: bool = True, generate_program_info: bool = True, generate_compilation_feedback: bool = True) -> None"""
    @overload
    def compile(self, mlir_program: str, options: CompilationOptions) -> Library:
        """compile(*args, **kwargs)
        Overloaded function.

        1. compile(self: mlir._mlir_libs._concretelang._compiler.Compiler, mlir_program: str, options: mlir._mlir_libs._concretelang._compiler.CompilationOptions) -> mlir._mlir_libs._concretelang._compiler.Library

        Compile `mlir_program` using the `options` compilation options.

        2. compile(self: mlir._mlir_libs._concretelang._compiler.Compiler, mlir_module: object, options: mlir._mlir_libs._concretelang._compiler.CompilationOptions, context: mlir._mlir_libs._concretelang._compiler.CompilationContext) -> mlir._mlir_libs._concretelang._compiler.Library

        Compile the `mlir_module` module with `options` compilation options, under the `context` compilation context.
        """
    @overload
    def compile(self, mlir_module: object, options: CompilationOptions, context: CompilationContext) -> Library:
        """compile(*args, **kwargs)
        Overloaded function.

        1. compile(self: mlir._mlir_libs._concretelang._compiler.Compiler, mlir_program: str, options: mlir._mlir_libs._concretelang._compiler.CompilationOptions) -> mlir._mlir_libs._concretelang._compiler.Library

        Compile `mlir_program` using the `options` compilation options.

        2. compile(self: mlir._mlir_libs._concretelang._compiler.Compiler, mlir_module: object, options: mlir._mlir_libs._concretelang._compiler.CompilationOptions, context: mlir._mlir_libs._concretelang._compiler.CompilationContext) -> mlir._mlir_libs._concretelang._compiler.Library

        Compile the `mlir_module` module with `options` compilation options, under the `context` compilation context.
        """

class Encoding:
    __members__: ClassVar[dict] = ...  # read-only
    AUTO: ClassVar[Encoding] = ...
    CRT: ClassVar[Encoding] = ...
    NATIVE: ClassVar[Encoding] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: mlir._mlir_libs._concretelang._compiler.Encoding, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: mlir._mlir_libs._concretelang._compiler.Encoding) -> int"""
    def __int__(self) -> int:
        """__int__(self: mlir._mlir_libs._concretelang._compiler.Encoding) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class GateInfo:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    def get_raw_info(self) -> RawInfo:
        """get_raw_info(self: mlir._mlir_libs._concretelang._compiler.GateInfo) -> mlir._mlir_libs._concretelang._compiler.RawInfo

        Return the raw type associated to the gate.
        """
    def get_type_info(self) -> TypeInfo:
        """get_type_info(self: mlir._mlir_libs._concretelang._compiler.GateInfo) -> mlir._mlir_libs._concretelang._compiler.TypeInfo

        Return the type associated to the gate.
        """

class KeyType:
    __members__: ClassVar[dict] = ...  # read-only
    BOOTSTRAP: ClassVar[KeyType] = ...
    KEY_SWITCH: ClassVar[KeyType] = ...
    PACKING_KEY_SWITCH: ClassVar[KeyType] = ...
    SECRET: ClassVar[KeyType] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: mlir._mlir_libs._concretelang._compiler.KeyType, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: mlir._mlir_libs._concretelang._compiler.KeyType) -> int"""
    def __int__(self) -> int:
        """__int__(self: mlir._mlir_libs._concretelang._compiler.KeyType) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class Keyset:
    def __init__(self, program_info: ProgramInfo, keyset_cache: KeysetCache | None, secret_seed_msb: int = ..., secret_seed_lsb: int = ..., encryption_seed_msb: int = ..., encryption_seed_lsb: int = ..., initial_lwe_secret_keys: dict[int, LweSecretKey] | None = ...) -> None:
        """__init__(self: mlir._mlir_libs._concretelang._compiler.Keyset, program_info: mlir._mlir_libs._concretelang._compiler.ProgramInfo, keyset_cache: Optional[mlir._mlir_libs._concretelang._compiler.KeysetCache], secret_seed_msb: int = 0, secret_seed_lsb: int = 0, encryption_seed_msb: int = 0, encryption_seed_lsb: int = 0, initial_lwe_secret_keys: Optional[Dict[int, mlir._mlir_libs._concretelang._compiler.LweSecretKey]] = None) -> None"""
    @staticmethod
    def deserialize(bytes: bytes) -> Keyset:
        """deserialize(bytes: bytes) -> mlir._mlir_libs._concretelang._compiler.Keyset

        Deserialize a Keyset from bytes.
        """
    @staticmethod
    def deserialize_from_file(path: str) -> Keyset:
        """deserialize_from_file(path: str) -> mlir._mlir_libs._concretelang._compiler.Keyset

        Deserialize a Keyset from a file.
        """
    def get_client_keys(self) -> ClientKeyset:
        """get_client_keys(self: mlir._mlir_libs._concretelang._compiler.Keyset) -> mlir._mlir_libs._concretelang._compiler.ClientKeyset

        Return the associated ClientKeyset.
        """
    def get_server_keys(self) -> ServerKeyset:
        """get_server_keys(self: mlir._mlir_libs._concretelang._compiler.Keyset) -> mlir._mlir_libs._concretelang._compiler.ServerKeyset

        Return the associated ServerKeyset.
        """
    def serialize(self) -> bytes:
        """serialize(self: mlir._mlir_libs._concretelang._compiler.Keyset) -> bytes

        Serialize a Keyset to bytes.
        """
    def serialize_lwe_secret_key_as_glwe(self, key_id: int, glwe_dim: int, poly_size: int) -> bytes:
        """serialize_lwe_secret_key_as_glwe(self: mlir._mlir_libs._concretelang._compiler.Keyset, key_id: int, glwe_dim: int, poly_size: int) -> bytes

        Serialize the `key_id` secret key as a tfhe-rs GLWE key with parameters `glwe_dim` and `poly_size`.
        """
    def serialize_to_file(self, arg0: str) -> None:
        """serialize_to_file(self: mlir._mlir_libs._concretelang._compiler.Keyset, arg0: str) -> None

        Serialize a Keyset to bytes.
        """

class KeysetCache:
    def __init__(self, backing_directory_path: str) -> None:
        """__init__(self: mlir._mlir_libs._concretelang._compiler.KeysetCache, backing_directory_path: str) -> None"""

class KeysetInfo:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    def bootstrap_keys(self) -> list[BootstrapKeyParam]:
        """bootstrap_keys(self: mlir._mlir_libs._concretelang._compiler.KeysetInfo) -> List[mlir._mlir_libs._concretelang._compiler.BootstrapKeyParam]

        Return the parameters of the bootstrap keys for this keyset.
        """
    @staticmethod
    def deserialize(bytes: bytes) -> KeysetInfo:
        """deserialize(bytes: bytes) -> mlir._mlir_libs._concretelang._compiler.KeysetInfo

        Deserialize a KeysetInfo from bytes.
        """
    @staticmethod
    def generate_virtual(partition_defs: list[PartitionDefinition], generate_fks: bool, options: OptimizerOptions | None = ...) -> KeysetInfo:
        """generate_virtual(partition_defs: List[mlir._mlir_libs._concretelang._compiler.PartitionDefinition], generate_fks: bool, options: Optional[mlir._mlir_libs._concretelang._compiler.OptimizerOptions] = None) -> mlir._mlir_libs._concretelang._compiler.KeysetInfo

        Generate a generic keyset info for a set of partition definitions
        """
    def get_restriction(self) -> KeysetRestriction:
        """get_restriction(self: mlir._mlir_libs._concretelang._compiler.KeysetInfo) -> mlir._mlir_libs._concretelang._compiler.KeysetRestriction

        Return the search space restriction associated to this keyset info.
        """
    def keyswitch_keys(self) -> list[KeyswitchKeyParam]:
        """keyswitch_keys(self: mlir._mlir_libs._concretelang._compiler.KeysetInfo) -> List[mlir._mlir_libs._concretelang._compiler.KeyswitchKeyParam]

        Return the parameters of the keyswitch keys for this keyset.
        """
    def packing_keyswitch_keys(self) -> list[PackingKeyswitchKeyParam]:
        """packing_keyswitch_keys(self: mlir._mlir_libs._concretelang._compiler.KeysetInfo) -> List[mlir._mlir_libs._concretelang._compiler.PackingKeyswitchKeyParam]

        Return the parameters of the packing keyswitch keys for this keyset.
        """
    def secret_keys(self) -> list[LweSecretKeyParam]:
        """secret_keys(self: mlir._mlir_libs._concretelang._compiler.KeysetInfo) -> List[mlir._mlir_libs._concretelang._compiler.LweSecretKeyParam]

        Return the parameters of the secret keys for this keyset.
        """
    def serialize(self) -> bytes:
        """serialize(self: mlir._mlir_libs._concretelang._compiler.KeysetInfo) -> bytes

        Serialize a KeysetInfo to bytes.
        """
    def __eq__(self, arg0: KeysetInfo) -> bool:
        """__eq__(self: mlir._mlir_libs._concretelang._compiler.KeysetInfo, arg0: mlir._mlir_libs._concretelang._compiler.KeysetInfo) -> bool"""
    def __ne__(self, arg0: KeysetInfo) -> bool:
        """__ne__(self: mlir._mlir_libs._concretelang._compiler.KeysetInfo, arg0: mlir._mlir_libs._concretelang._compiler.KeysetInfo) -> bool"""

class KeysetRestriction:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    def from_json(self) -> KeysetRestriction:
        """from_json(self: str) -> mlir._mlir_libs._concretelang._compiler.KeysetRestriction

        Create a KeysetRestriction from a json string.
        """
    def to_json(self) -> str:
        """to_json(self: mlir._mlir_libs._concretelang._compiler.KeysetRestriction) -> str

        Serialize a KeysetRestriction to a json string.
        """

class KeyswitchKeyParam:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    def base_log(self) -> int:
        """base_log(self: mlir._mlir_libs._concretelang._compiler.KeyswitchKeyParam) -> int

        Return the associated base log.
        """
    def input_secret_key_id(self) -> int:
        """input_secret_key_id(self: mlir._mlir_libs._concretelang._compiler.KeyswitchKeyParam) -> int

        Return the key id of the associated input key.
        """
    def level(self) -> int:
        """level(self: mlir._mlir_libs._concretelang._compiler.KeyswitchKeyParam) -> int

        Return the associated number of levels.
        """
    def output_secret_key_id(self) -> int:
        """output_secret_key_id(self: mlir._mlir_libs._concretelang._compiler.KeyswitchKeyParam) -> int

        Return the key id of the associated output key.
        """
    def variance(self) -> float:
        """variance(self: mlir._mlir_libs._concretelang._compiler.KeyswitchKeyParam) -> float

        Return the associated noise variance.
        """
    def __eq__(self, arg0: KeyswitchKeyParam) -> bool:
        """__eq__(self: mlir._mlir_libs._concretelang._compiler.KeyswitchKeyParam, arg0: mlir._mlir_libs._concretelang._compiler.KeyswitchKeyParam) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __ne__(self, arg0: KeyswitchKeyParam) -> bool:
        """__ne__(self: mlir._mlir_libs._concretelang._compiler.KeyswitchKeyParam, arg0: mlir._mlir_libs._concretelang._compiler.KeyswitchKeyParam) -> bool"""

class Library:
    def __init__(self, output_dir_path: str) -> None:
        """__init__(self: mlir._mlir_libs._concretelang._compiler.Library, output_dir_path: str) -> None"""
    def get_output_dir_path(self) -> str:
        """get_output_dir_path(self: mlir._mlir_libs._concretelang._compiler.Library) -> str

        Return the path to library output directory.
        """
    def get_program_compilation_feedback(self) -> ProgramCompilationFeedback:
        """get_program_compilation_feedback(self: mlir._mlir_libs._concretelang._compiler.Library) -> mlir._mlir_libs._concretelang._compiler.ProgramCompilationFeedback

        Return the associated program compilation feedback.
        """
    def get_program_info(self) -> ProgramInfo:
        """get_program_info(self: mlir._mlir_libs._concretelang._compiler.Library) -> mlir._mlir_libs._concretelang._compiler.ProgramInfo

        Return the program info associated to the library.
        """
    def get_program_info_path(self) -> str:
        """get_program_info_path(self: mlir._mlir_libs._concretelang._compiler.Library) -> str

        Return the path to the program info file.
        """
    def get_shared_lib_path(self) -> str:
        """get_shared_lib_path(self: mlir._mlir_libs._concretelang._compiler.Library) -> str

        Return the path to the shared library.
        """

class LweSecretKey:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    @staticmethod
    def deserialize(buffer: bytes, params: LweSecretKeyParam) -> LweSecretKey:
        """deserialize(buffer: bytes, params: mlir._mlir_libs._concretelang._compiler.LweSecretKeyParam) -> mlir._mlir_libs._concretelang._compiler.LweSecretKey

        Deserialize an LweSecretKet from bytes and associated parameters.
        """
    @staticmethod
    def deserialize_from_glwe(buffer: bytes, params: LweSecretKeyParam) -> LweSecretKey:
        """deserialize_from_glwe(buffer: bytes, params: mlir._mlir_libs._concretelang._compiler.LweSecretKeyParam) -> mlir._mlir_libs._concretelang._compiler.LweSecretKey

        Deserialize an LweSecretKey from glwe encoded (tfhe-rs compatible) bytes and associated parameters.
        """
    def serialize(self) -> bytes:
        """serialize(self: mlir._mlir_libs._concretelang._compiler.LweSecretKey) -> bytes

        Serialize an LweSecretKey to bytes.
        """
    def serialize_as_glwe(self, glwe_dimension: int, polynomial_size: int) -> bytes:
        """serialize_as_glwe(self: mlir._mlir_libs._concretelang._compiler.LweSecretKey, glwe_dimension: int, polynomial_size: int) -> bytes

        Serialize an LweSecretKey to glwe encoded (tfhe-rs compatible) bytes and associated parameters.
        """
    @property
    def param(self) -> LweSecretKeyParam: ...

class LweSecretKeyParam:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    def dimension(self) -> int:
        """dimension(self: mlir._mlir_libs._concretelang._compiler.LweSecretKeyParam) -> int

        Return the associated LWE dimension.
        """
    def __eq__(self, arg0: LweSecretKeyParam) -> bool:
        """__eq__(self: mlir._mlir_libs._concretelang._compiler.LweSecretKeyParam, arg0: mlir._mlir_libs._concretelang._compiler.LweSecretKeyParam) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __ne__(self, arg0: LweSecretKeyParam) -> bool:
        """__ne__(self: mlir._mlir_libs._concretelang._compiler.LweSecretKeyParam, arg0: mlir._mlir_libs._concretelang._compiler.LweSecretKeyParam) -> bool"""

class OptimizerMultiParameterStrategy:
    __members__: ClassVar[dict] = ...  # read-only
    PRECISION: ClassVar[OptimizerMultiParameterStrategy] = ...
    PRECISION_AND_NORM2: ClassVar[OptimizerMultiParameterStrategy] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: mlir._mlir_libs._concretelang._compiler.OptimizerMultiParameterStrategy, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: mlir._mlir_libs._concretelang._compiler.OptimizerMultiParameterStrategy) -> int"""
    def __int__(self) -> int:
        """__int__(self: mlir._mlir_libs._concretelang._compiler.OptimizerMultiParameterStrategy) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class OptimizerOptions:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    def set_cache_on_disk(self, cache_on_disk: bool) -> None:
        """set_cache_on_disk(self: mlir._mlir_libs._concretelang._compiler.OptimizerOptions, cache_on_disk: bool) -> None

        Set option for cache on disk.
        """
    def set_ciphertext_modulus_log(self, ciphertext_modulus_log: int) -> None:
        """set_ciphertext_modulus_log(self: mlir._mlir_libs._concretelang._compiler.OptimizerOptions, ciphertext_modulus_log: int) -> None

        Set option for ciphertext modulus log.
        """
    def set_default_log_norm2_woppbs(self, default_log_norm2_woppbs: float) -> None:
        """set_default_log_norm2_woppbs(self: mlir._mlir_libs._concretelang._compiler.OptimizerOptions, default_log_norm2_woppbs: float) -> None

        Set option for default log norm2 woppbs.
        """
    def set_encoding_to_auto(self) -> None:
        """set_encoding_to_auto(self: mlir._mlir_libs._concretelang._compiler.OptimizerOptions) -> None

        Set option for encoding to auto.
        """
    def set_encoding_to_crt(self) -> None:
        """set_encoding_to_crt(self: mlir._mlir_libs._concretelang._compiler.OptimizerOptions) -> None

        Set option for encoding to crt.
        """
    def set_encoding_to_native(self) -> None:
        """set_encoding_to_native(self: mlir._mlir_libs._concretelang._compiler.OptimizerOptions) -> None

        Set option for encoding to native.
        """
    @overload
    def set_fft_precision(self, fft_precision: int) -> None:
        """set_fft_precision(*args, **kwargs)
        Overloaded function.

        1. set_fft_precision(self: mlir._mlir_libs._concretelang._compiler.OptimizerOptions, fft_precision: int) -> None

        Set option for fft precision.

        2. set_fft_precision(self: mlir._mlir_libs._concretelang._compiler.OptimizerOptions, fft_precision: int) -> None

        Set option for fft precision.
        """
    @overload
    def set_fft_precision(self, fft_precision: int) -> None:
        """set_fft_precision(*args, **kwargs)
        Overloaded function.

        1. set_fft_precision(self: mlir._mlir_libs._concretelang._compiler.OptimizerOptions, fft_precision: int) -> None

        Set option for fft precision.

        2. set_fft_precision(self: mlir._mlir_libs._concretelang._compiler.OptimizerOptions, fft_precision: int) -> None

        Set option for fft precision.
        """
    def set_key_sharing(self, key_sharing: bool) -> None:
        """set_key_sharing(self: mlir._mlir_libs._concretelang._compiler.OptimizerOptions, key_sharing: bool) -> None

        Set option for key sharing.
        """
    def set_keyset_restriction(self, restriction: KeysetRestriction) -> None:
        """set_keyset_restriction(self: mlir._mlir_libs._concretelang._compiler.OptimizerOptions, restriction: mlir._mlir_libs._concretelang._compiler.KeysetRestriction) -> None

        Set option for keyset restriction
        """
    def set_maximum_acceptable_error_probability(self, maximum_acceptable_error_probability: float) -> None:
        """set_maximum_acceptable_error_probability(self: mlir._mlir_libs._concretelang._compiler.OptimizerOptions, maximum_acceptable_error_probability: float) -> None

        Set option for maximum acceptable error probability.
        """
    def set_multi_param_strategy_to_by_precision(self) -> None:
        """set_multi_param_strategy_to_by_precision(self: mlir._mlir_libs._concretelang._compiler.OptimizerOptions) -> None

        Set option for multi param strategy to by-precision.
        """
    def set_multi_param_strategy_to_by_precision_and_norm_2(self) -> None:
        """set_multi_param_strategy_to_by_precision_and_norm_2(self: mlir._mlir_libs._concretelang._compiler.OptimizerOptions) -> None

        Set option for multi param strategy to by-precision-and-norm2.
        """
    def set_range_restriction(self, restriction: RangeRestriction) -> None:
        """set_range_restriction(self: mlir._mlir_libs._concretelang._compiler.OptimizerOptions, restriction: mlir._mlir_libs._concretelang._compiler.RangeRestriction) -> None

        Set option for range restriction
        """
    def set_security_level(self, security_level: int) -> None:
        """set_security_level(self: mlir._mlir_libs._concretelang._compiler.OptimizerOptions, security_level: int) -> None

        Set option for security level.
        """
    def set_use_gpu_constraints(self, use_gpu_constraints: bool) -> None:
        """set_use_gpu_constraints(self: mlir._mlir_libs._concretelang._compiler.OptimizerOptions, use_gpu_constraints: bool) -> None

        Set option for use gpu constrints.
        """

class OptimizerStrategy:
    __members__: ClassVar[dict] = ...  # read-only
    DAG_MONO: ClassVar[OptimizerStrategy] = ...
    DAG_MULTI: ClassVar[OptimizerStrategy] = ...
    V0: ClassVar[OptimizerStrategy] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: mlir._mlir_libs._concretelang._compiler.OptimizerStrategy, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: mlir._mlir_libs._concretelang._compiler.OptimizerStrategy) -> int"""
    def __int__(self) -> int:
        """__int__(self: mlir._mlir_libs._concretelang._compiler.OptimizerStrategy) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class PackingKeyswitchKeyParam:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    def base_log(self) -> int:
        """base_log(self: mlir._mlir_libs._concretelang._compiler.PackingKeyswitchKeyParam) -> int

        Return the associated base log.
        """
    def glwe_dimension(self) -> int:
        """glwe_dimension(self: mlir._mlir_libs._concretelang._compiler.PackingKeyswitchKeyParam) -> int

        Return the associated GLWE dimension.
        """
    def input_lwe_dimension(self) -> int:
        """input_lwe_dimension(self: mlir._mlir_libs._concretelang._compiler.PackingKeyswitchKeyParam) -> int

        Return the associated input LWE dimension.
        """
    def input_secret_key_id(self) -> int:
        """input_secret_key_id(self: mlir._mlir_libs._concretelang._compiler.PackingKeyswitchKeyParam) -> int

        Return the key id of the associated input key.
        """
    def level(self) -> int:
        """level(self: mlir._mlir_libs._concretelang._compiler.PackingKeyswitchKeyParam) -> int

        Return the associated number of levels.
        """
    def output_secret_key_id(self) -> int:
        """output_secret_key_id(self: mlir._mlir_libs._concretelang._compiler.PackingKeyswitchKeyParam) -> int

        Return the key id of the associated output key.
        """
    def polynomial_size(self) -> int:
        """polynomial_size(self: mlir._mlir_libs._concretelang._compiler.PackingKeyswitchKeyParam) -> int

        Return the associated polynomial size.
        """
    def variance(self) -> float:
        """variance(self: mlir._mlir_libs._concretelang._compiler.PackingKeyswitchKeyParam) -> float

        Return the associated noise variance.
        """
    def __eq__(self, arg0: PackingKeyswitchKeyParam) -> bool:
        """__eq__(self: mlir._mlir_libs._concretelang._compiler.PackingKeyswitchKeyParam, arg0: mlir._mlir_libs._concretelang._compiler.PackingKeyswitchKeyParam) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __ne__(self, arg0: PackingKeyswitchKeyParam) -> bool:
        """__ne__(self: mlir._mlir_libs._concretelang._compiler.PackingKeyswitchKeyParam, arg0: mlir._mlir_libs._concretelang._compiler.PackingKeyswitchKeyParam) -> bool"""

class PartitionDefinition:
    def __init__(self, precision: int, norm2: float) -> None:
        """__init__(self: mlir._mlir_libs._concretelang._compiler.PartitionDefinition, precision: int, norm2: float) -> None"""

class PrimitiveOperation:
    __members__: ClassVar[dict] = ...  # read-only
    CLEAR_ADDITION: ClassVar[PrimitiveOperation] = ...
    CLEAR_MULTIPLICATION: ClassVar[PrimitiveOperation] = ...
    ENCRYPTED_ADDITION: ClassVar[PrimitiveOperation] = ...
    ENCRYPTED_NEGATION: ClassVar[PrimitiveOperation] = ...
    KEY_SWITCH: ClassVar[PrimitiveOperation] = ...
    PBS: ClassVar[PrimitiveOperation] = ...
    WOP_PBS: ClassVar[PrimitiveOperation] = ...
    __entries: ClassVar[dict] = ...
    def __init__(self, value: int) -> None:
        """__init__(self: mlir._mlir_libs._concretelang._compiler.PrimitiveOperation, value: int) -> None"""
    def __eq__(self, other: object) -> bool:
        """__eq__(self: object, other: object) -> bool"""
    def __hash__(self) -> int:
        """__hash__(self: object) -> int"""
    def __index__(self) -> int:
        """__index__(self: mlir._mlir_libs._concretelang._compiler.PrimitiveOperation) -> int"""
    def __int__(self) -> int:
        """__int__(self: mlir._mlir_libs._concretelang._compiler.PrimitiveOperation) -> int"""
    def __ne__(self, other: object) -> bool:
        """__ne__(self: object, other: object) -> bool"""
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class ProgramCompilationFeedback:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    def get_circuit_feedback(self, function: str) -> CircuitCompilationFeedback:
        """get_circuit_feedback(self: mlir._mlir_libs._concretelang._compiler.ProgramCompilationFeedback, function: str) -> mlir._mlir_libs._concretelang._compiler.CircuitCompilationFeedback

        Return the circuit feedback for `function`.
        """
    @property
    def circuit_feedbacks(self) -> list[CircuitCompilationFeedback]: ...
    @property
    def complexity(self) -> float: ...
    @property
    def global_p_error(self) -> float: ...
    @property
    def p_error(self) -> float: ...
    @property
    def total_bootstrap_keys_size(self) -> int: ...
    @property
    def total_keyswitch_keys_size(self) -> int: ...
    @property
    def total_secret_keys_size(self) -> int: ...

class ProgramInfo:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    @staticmethod
    def deserialize(bytes: bytes) -> ProgramInfo:
        """deserialize(bytes: bytes) -> mlir._mlir_libs._concretelang._compiler.ProgramInfo

        Deserialize a ProgramInfo from bytes.
        """
    def function_list(self) -> list[str]:
        """function_list(self: mlir._mlir_libs._concretelang._compiler.ProgramInfo) -> List[str]"""
    def get_circuit(self, arg0: str) -> CircuitInfo:
        """get_circuit(self: mlir._mlir_libs._concretelang._compiler.ProgramInfo, arg0: str) -> mlir._mlir_libs._concretelang._compiler.CircuitInfo

        Return the circuit associated to the program with given name.
        """
    def get_circuits(self) -> list[CircuitInfo]:
        """get_circuits(self: mlir._mlir_libs._concretelang._compiler.ProgramInfo) -> List[mlir._mlir_libs._concretelang._compiler.CircuitInfo]

        Return the circuits associated to the program.
        """
    def get_keyset_info(self) -> KeysetInfo:
        """get_keyset_info(self: mlir._mlir_libs._concretelang._compiler.ProgramInfo) -> mlir._mlir_libs._concretelang._compiler.KeysetInfo

        Return the keyset info associated to the program.
        """
    def input_keyid_at(self, pos: int, circuit_name: str) -> int:
        """input_keyid_at(self: mlir._mlir_libs._concretelang._compiler.ProgramInfo, pos: int, circuit_name: str) -> int

        Return the key id associated to the argument `pos` of circuit `circuit_name`.
        """
    def input_signs(self) -> list[bool]:
        """input_signs(self: mlir._mlir_libs._concretelang._compiler.ProgramInfo) -> List[bool]

        Return the signedness of the input of the first circuit.
        """
    def input_variance_at(self, pos: int, circuit_name: str) -> float:
        """input_variance_at(self: mlir._mlir_libs._concretelang._compiler.ProgramInfo, pos: int, circuit_name: str) -> float

        Return the noise variance associated to the argument `pos` of circuit `circuit_name`.
        """
    def output_signs(self) -> list[bool]:
        """output_signs(self: mlir._mlir_libs._concretelang._compiler.ProgramInfo) -> List[bool]

        Return the signedness of the output of the first circuit.
        """
    def serialize(self) -> bytes:
        """serialize(self: mlir._mlir_libs._concretelang._compiler.ProgramInfo) -> bytes

        Serialize a ProgramInfo to bytes.
        """

class RangeRestriction:
    def __init__(self) -> None:
        """__init__(self: mlir._mlir_libs._concretelang._compiler.RangeRestriction) -> None"""
    def add_available_glwe_dimension(self, arg0: int) -> None:
        """add_available_glwe_dimension(self: mlir._mlir_libs._concretelang._compiler.RangeRestriction, arg0: int) -> None

        Add an available glwe dimension to the restriction
        """
    def add_available_glwe_log_polynomial_size(self, arg0: int) -> None:
        """add_available_glwe_log_polynomial_size(self: mlir._mlir_libs._concretelang._compiler.RangeRestriction, arg0: int) -> None

        Add an available glwe log poly size to the restriction
        """
    def add_available_internal_lwe_dimension(self, arg0: int) -> None:
        """add_available_internal_lwe_dimension(self: mlir._mlir_libs._concretelang._compiler.RangeRestriction, arg0: int) -> None

        Add an available internal lwe dimension to the restriction
        """
    def add_available_ks_base_log(self, arg0: int) -> None:
        """add_available_ks_base_log(self: mlir._mlir_libs._concretelang._compiler.RangeRestriction, arg0: int) -> None

        Add an available ks base log to the restriction
        """
    def add_available_ks_level_count(self, arg0: int) -> None:
        """add_available_ks_level_count(self: mlir._mlir_libs._concretelang._compiler.RangeRestriction, arg0: int) -> None

        Add an available ks level count to the restriction
        """
    def add_available_pbs_base_log(self, arg0: int) -> None:
        """add_available_pbs_base_log(self: mlir._mlir_libs._concretelang._compiler.RangeRestriction, arg0: int) -> None

        Add an available pbs base log to the restriction
        """
    def add_available_pbs_level_count(self, arg0: int) -> None:
        """add_available_pbs_level_count(self: mlir._mlir_libs._concretelang._compiler.RangeRestriction, arg0: int) -> None

        Add an available pbs level count to the restriction
        """
    def from_json(self) -> RangeRestriction:
        """from_json(self: str) -> mlir._mlir_libs._concretelang._compiler.RangeRestriction

        Create a RangeRestriction from a json string.
        """
    def to_json(self) -> str:
        """to_json(self: mlir._mlir_libs._concretelang._compiler.RangeRestriction) -> str

        Serialize a RangeRestriction to a json string.
        """

class RawInfo:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    def get_integer_precision(self) -> int:
        """get_integer_precision(self: mlir._mlir_libs._concretelang._compiler.RawInfo) -> int

        Return the integer precision associated to the raw info.
        """
    def get_shape(self) -> list[int]:
        """get_shape(self: mlir._mlir_libs._concretelang._compiler.RawInfo) -> List[int]

        Return the shape associated to the raw info.
        """
    def get_signedness(self) -> bool:
        """get_signedness(self: mlir._mlir_libs._concretelang._compiler.RawInfo) -> bool

        Return the signedness associated to the raw info.
        """

class ServerCircuit:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    def call(self, args: list[TransportValue], keyset: ServerKeyset) -> list[TransportValue]:
        """call(self: mlir._mlir_libs._concretelang._compiler.ServerCircuit, args: List[mlir._mlir_libs._concretelang._compiler.TransportValue], keyset: mlir._mlir_libs._concretelang._compiler.ServerKeyset) -> List[mlir._mlir_libs._concretelang._compiler.TransportValue]

        Perform circuit call with `args` arguments using the `keyset` ServerKeyset.
        """
    def simulate(self, args: list[TransportValue]) -> list[TransportValue]:
        """simulate(self: mlir._mlir_libs._concretelang._compiler.ServerCircuit, args: List[mlir._mlir_libs._concretelang._compiler.TransportValue]) -> List[mlir._mlir_libs._concretelang._compiler.TransportValue]

        Perform circuit simulation with `args` arguments.
        """

class ServerKeyset:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    @staticmethod
    def deserialize(bytes: bytes) -> ServerKeyset:
        """deserialize(bytes: bytes) -> mlir._mlir_libs._concretelang._compiler.ServerKeyset

        Deserialize a ServerKeyset from bytes.
        """
    def serialize(self) -> bytes:
        """serialize(self: mlir._mlir_libs._concretelang._compiler.ServerKeyset) -> bytes

        Serialize a ServerKeyset to bytes.
        """

class ServerProgram:
    def __init__(self, library: Library, use_simulation: bool) -> None:
        """__init__(self: mlir._mlir_libs._concretelang._compiler.ServerProgram, library: mlir._mlir_libs._concretelang._compiler.Library, use_simulation: bool) -> None"""
    def get_server_circuit(self, circuit: str) -> ServerCircuit:
        """get_server_circuit(self: mlir._mlir_libs._concretelang._compiler.ServerProgram, circuit: str) -> mlir._mlir_libs._concretelang._compiler.ServerCircuit

        Return the `circuit` ServerCircuit.
        """

class Statistic:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    @property
    def count(self) -> int | None: ...
    @property
    def keys(self) -> list[tuple[KeyType, int]]: ...
    @property
    def location(self) -> str: ...
    @property
    def operation(self) -> PrimitiveOperation: ...

class TfhersFheIntDescription:
    carry_modulus: int
    degree: int
    is_signed: bool
    ks_first: bool
    lwe_size: int
    message_modulus: int
    n_cts: int
    noise_level: int
    width: int
    def __init__(self, width: int, is_signed: bool, lwe_size: int, n_cts: int, degree: int, noise_level: int, message_modulus: int, carry_modulus: int, ks_first: bool) -> None:
        """__init__(self: mlir._mlir_libs._concretelang._compiler.TfhersFheIntDescription, width: int, is_signed: bool, lwe_size: int, n_cts: int, degree: int, noise_level: int, message_modulus: int, carry_modulus: int, ks_first: bool) -> None"""
    @staticmethod
    def get_unknown_noise_level() -> int:
        """get_unknown_noise_level() -> int"""

class TransportValue:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    @staticmethod
    def deserialize(bytes: bytes) -> TransportValue:
        """deserialize(bytes: bytes) -> mlir._mlir_libs._concretelang._compiler.TransportValue

        Deserialize a TransportValue from bytes.
        """
    def serialize(self) -> bytes:
        """serialize(self: mlir._mlir_libs._concretelang._compiler.TransportValue) -> bytes

        Serialize a TransportValue to bytes
        """

class TypeInfo:
    def __init__(self, *args, **kwargs) -> None:
        """Initialize self.  See help(type(self)) for accurate signature."""
    def is_plaintext(self) -> bool:
        """is_plaintext(self: mlir._mlir_libs._concretelang._compiler.TypeInfo) -> bool

        Return true if the type is plaintext
        """

class Value:
    @overload
    def __init__(self, input: int) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        2. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        3. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        4. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        5. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        6. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        7. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        8. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        9. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: numpy.ndarray) -> None

        10. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: object) -> None
        """
    @overload
    def __init__(self, input: int) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        2. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        3. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        4. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        5. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        6. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        7. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        8. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        9. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: numpy.ndarray) -> None

        10. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: object) -> None
        """
    @overload
    def __init__(self, input: int) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        2. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        3. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        4. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        5. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        6. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        7. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        8. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        9. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: numpy.ndarray) -> None

        10. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: object) -> None
        """
    @overload
    def __init__(self, input: int) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        2. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        3. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        4. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        5. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        6. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        7. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        8. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        9. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: numpy.ndarray) -> None

        10. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: object) -> None
        """
    @overload
    def __init__(self, input: int) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        2. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        3. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        4. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        5. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        6. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        7. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        8. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        9. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: numpy.ndarray) -> None

        10. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: object) -> None
        """
    @overload
    def __init__(self, input: int) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        2. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        3. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        4. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        5. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        6. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        7. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        8. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        9. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: numpy.ndarray) -> None

        10. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: object) -> None
        """
    @overload
    def __init__(self, input: int) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        2. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        3. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        4. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        5. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        6. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        7. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        8. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        9. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: numpy.ndarray) -> None

        10. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: object) -> None
        """
    @overload
    def __init__(self, input: int) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        2. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        3. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        4. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        5. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        6. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        7. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        8. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        9. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: numpy.ndarray) -> None

        10. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: object) -> None
        """
    @overload
    def __init__(self, input: numpy.ndarray) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        2. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        3. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        4. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        5. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        6. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        7. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        8. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        9. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: numpy.ndarray) -> None

        10. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: object) -> None
        """
    @overload
    def __init__(self, input: object) -> None:
        """__init__(*args, **kwargs)
        Overloaded function.

        1. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        2. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        3. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        4. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        5. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        6. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        7. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        8. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: int) -> None

        9. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: numpy.ndarray) -> None

        10. __init__(self: mlir._mlir_libs._concretelang._compiler.Value, input: object) -> None
        """
    def get_shape(self) -> list[int]:
        """get_shape(self: mlir._mlir_libs._concretelang._compiler.Value) -> List[int]

        Return the shape of the value.
        """
    def is_scalar(self) -> bool:
        """is_scalar(self: mlir._mlir_libs._concretelang._compiler.Value) -> bool

        Return whether the value is a scalar.
        """
    def is_tensor(self) -> bool:
        """is_tensor(self: mlir._mlir_libs._concretelang._compiler.Value) -> bool

        Return whether the value is a tensor.
        """
    def to_py_val(self) -> int | int | int | int | int | int | int | int | numpy.ndarray:
        """to_py_val(self: mlir._mlir_libs._concretelang._compiler.Value) -> Union[int, int, int, int, int, int, int, int, numpy.ndarray]

        Return the inner value as a python type.
        """

def check_cuda_device_available() -> bool:
    """check_cuda_device_available() -> bool"""
def check_gpu_runtime_enabled() -> bool:
    """check_gpu_runtime_enabled() -> bool"""
def export_tfhers_int(arg0: TransportValue, arg1: TfhersFheIntDescription) -> list[int]:
    """export_tfhers_int(arg0: mlir._mlir_libs._concretelang._compiler.TransportValue, arg1: mlir._mlir_libs._concretelang._compiler.TfhersFheIntDescription) -> List[int]"""
def import_tfhers_int(arg0: bytes, arg1: TfhersFheIntDescription, arg2: int, arg3: float, arg4: list[int]) -> TransportValue:
    """import_tfhers_int(arg0: bytes, arg1: mlir._mlir_libs._concretelang._compiler.TfhersFheIntDescription, arg2: int, arg3: float, arg4: List[int]) -> mlir._mlir_libs._concretelang._compiler.TransportValue"""
def init_df_parallelization() -> None:
    """init_df_parallelization() -> None"""
def round_trip(arg0: str) -> str:
    """round_trip(arg0: str) -> str"""
def set_compiler_logging(arg0: bool) -> None:
    """set_compiler_logging(arg0: bool) -> None"""
def set_llvm_debug_flag(arg0: bool) -> None:
    """set_llvm_debug_flag(arg0: bool) -> None"""
def terminate_df_parallelization() -> None:
    """terminate_df_parallelization() -> None"""
