"""
HACS Tools - CRUD Operations, Structured-IO, and Validation

This package provides comprehensive tools for HACS resources including
CRUD operations with Actor permissions, structured-IO for LLM integration,
and validation with business rules.
"""

__version__ = "0.1.0"

# CRUD Operations
from .crud import (
    CreateResource,
    ReadResource,
    UpdateResource,
    DeleteResource,
    ListResources,
    GetAuditLog,
    CreatePatient,
    ReadPatient,
    CreateObservation,
    ReadObservation,
    StorageBackend,
    CRUDOperation,
    CRUDError,
    PermissionError,
    ResourceNotFoundError,
    ConflictError,
    AuditEvent,
    StorageManager,
    PermissionManager,
    set_storage_backend,
    get_storage_manager,
)

# Structured-IO for LLM Integration
from .structured import (
    generate_function_spec,
    validate_llm_output,
    create_tool_executor,
    ToolCallPattern,
    ToolCall,
    ToolCallResult,
    ToolExecutor,
    FunctionSpecError,
    LLMValidationError,
    get_patient_function_specs,
    validate_patient_output,
    validate_observation_output,
)

# Validation System
from .validation import (
    validate_before_create,
    validate_before_update,
    validate_fhir_compliance,
    validate_resource_comprehensive,
    validate_patient,
    validate_observation,
    validate_encounter,
    validate_agent_message,
    ValidationLevel,
    ValidationResult,
    BusinessRuleValidator,
    CrossReferenceValidator,
    PermissionValidator,
)

# Memory Operations
from .memory import (
    store_memory,
    recall_memory,
    link_memories,
    get_memory_manager,
    store_episodic_memory,
    store_procedural_memory,
    recall_episodic_memories,
    MemorySearchResult,
    MemoryLinkType,
    MemoryLink,
    InMemoryAdapter,
)

# Evidence Operations
from .evidence import (
    create_evidence,
    search_evidence,
    link_evidence_to_resource,
    get_evidence_links,
    get_resource_evidence,
    upsert_evidence_embedding,
    get_evidence_stats,
    create_clinical_guideline,
    create_rct_evidence,
    search_high_quality_evidence,
    EvidenceSearchResult,
    EvidenceLevel,
    EvidenceLink,
    VectorEmbedding,
)

# Search Layer
from .search import (
    search_resources,
    search_patients,
    search_observations,
    SearchResult,
    SearchMethod,
    SearchFilter,
)

# Protocol Adapters
from .adapters import (
    # MCP Adapter
    MCPAdapter,
    convert_to_mcp_task,
    convert_from_mcp_result,
    # A2A Adapter
    A2AAdapter,
    create_a2a_envelope,
    extract_from_a2a_envelope,
    # AG-UI Adapter
    AGUIAdapter,
    format_for_ag_ui,
    parse_ag_ui_event,
    # LangGraph Adapter
    LangGraphAdapter,
    create_custom_workflow_state,
    # CrewAI Adapter
    CrewAIAdapter,
    create_agent_binding,
    task_to_crew_format,
)

__all__ = [
    # CRUD Operations
    "CreateResource",
    "ReadResource",
    "UpdateResource",
    "DeleteResource",
    "ListResources",
    "GetAuditLog",
    "CreatePatient",
    "ReadPatient",
    "CreateObservation",
    "ReadObservation",
    "StorageBackend",
    "CRUDOperation",
    "CRUDError",
    "PermissionError",
    "ResourceNotFoundError",
    "ConflictError",
    "AuditEvent",
    "StorageManager",
    "PermissionManager",
    "set_storage_backend",
    "get_storage_manager",
    # Structured-IO
    "generate_function_spec",
    "validate_llm_output",
    "create_tool_executor",
    "ToolCallPattern",
    "ToolCall",
    "ToolCallResult",
    "ToolExecutor",
    "FunctionSpecError",
    "LLMValidationError",
    "get_patient_function_specs",
    "validate_patient_output",
    "validate_observation_output",
    # Validation
    "validate_before_create",
    "validate_before_update",
    "validate_fhir_compliance",
    "validate_resource_comprehensive",
    "validate_patient",
    "validate_observation",
    "validate_encounter",
    "validate_agent_message",
    "ValidationLevel",
    "ValidationResult",
    "BusinessRuleValidator",
    "CrossReferenceValidator",
    "PermissionValidator",
    # Memory Operations
    "store_memory",
    "recall_memory",
    "link_memories",
    "get_memory_manager",
    "store_episodic_memory",
    "store_procedural_memory",
    "recall_episodic_memories",
    "MemorySearchResult",
    "MemoryLinkType",
    "MemoryLink",
    "InMemoryAdapter",
    # Evidence Operations
    "create_evidence",
    "search_evidence",
    "link_evidence_to_resource",
    "get_evidence_links",
    "get_resource_evidence",
    "upsert_evidence_embedding",
    "get_evidence_stats",
    "create_clinical_guideline",
    "create_rct_evidence",
    "search_high_quality_evidence",
    "EvidenceSearchResult",
    "EvidenceLevel",
    "EvidenceLink",
    "VectorEmbedding",
    # Search Layer
    "search_resources",
    "search_patients",
    "search_observations",
    "SearchResult",
    "SearchMethod",
    "SearchFilter",
    # Protocol Adapters
    "MCPAdapter",
    "convert_to_mcp_task",
    "convert_from_mcp_result",
    "A2AAdapter",
    "create_a2a_envelope",
    "extract_from_a2a_envelope",
    "AGUIAdapter",
    "format_for_ag_ui",
    "parse_ag_ui_event",
    "LangGraphAdapter",
    "create_custom_workflow_state",
    "CrewAIAdapter",
    "create_agent_binding",
    "task_to_crew_format",
]


def hello() -> str:
    return "Hello from hacs-tools!"
