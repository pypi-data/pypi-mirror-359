# HACS Core Module

The `hacs-core` package provides the foundational models and base classes for the Healthcare Agent Communication Standard. It defines the core abstractions for resources, memory, evidence, and actors that all other HACS modules build upon.

## 📦 Package Overview

```
hacs-core/
├── src/hacs_core/
│   ├── __init__.py          # Public API exports
│   ├── base_resource.py     # BaseResource foundation
│   ├── memory.py           # MemoryBlock and memory types
│   ├── evidence.py         # Evidence model and types
│   ├── actor.py            # Actor model and permissions
│   └── py.typed            # Type hints marker
└── pyproject.toml          # Package configuration
```

## 🏗️ Core Models

### BaseResource

The foundation class for all HACS resources, providing common fields and utilities.

```python
from hacs_core import BaseResource
from datetime import datetime

class BaseResource(BaseModel):
    """Base class for all HACS resources with common fields and utilities."""
    
    id: str = Field(description="Unique resource identifier")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resource_type: str = Field(description="Resource type identifier")
```

#### Key Features
- **Timezone-aware timestamps** with automatic UTC handling
- **Utility methods** for age calculation and comparison
- **Update tracking** with automatic timestamp management
- **JSON Schema export** for LLM function specifications

#### Example Usage
```python
from hacs_core import BaseResource
from datetime import datetime, timezone

# Custom resource extending BaseResource
class CustomResource(BaseResource):
    name: str
    description: str
    
    def __init__(self, **data):
        super().__init__(**data)
        self.resource_type = "CustomResource"

# Create and use
resource = CustomResource(
    id="custom-001",
    name="Example Resource",
    description="A custom healthcare resource"
)

print(f"Resource age: {resource.age_seconds:.2f} seconds")
print(f"Resource type: {resource.resource_type}")

# Update timestamp
resource.update_timestamp()
print(f"Updated at: {resource.updated_at}")
```

### MemoryBlock

Implements cognitive science-based memory types for AI agents.

```python
from hacs_core import MemoryBlock, MemoryType

# Create episodic memory (events, experiences)
episodic_memory = MemoryBlock(
    id="memory-encounter-001",
    memory_type=MemoryType.EPISODIC,
    content="Patient presented with chest pain, ruled out MI via ECG and troponins",
    importance_score=0.9,
    metadata={
        "patient_id": "patient-001",
        "encounter_date": "2024-01-15",
        "clinical_significance": "high"
    }
)

# Create procedural memory (skills, procedures)
procedural_memory = MemoryBlock(
    id="memory-procedure-001",
    memory_type=MemoryType.PROCEDURAL,
    content="Protocol for blood pressure measurement: patient seated, cuff properly sized, multiple readings",
    importance_score=0.7,
    metadata={
        "procedure_type": "vital_signs",
        "skill_level": "standard"
    }
)

# Create executive memory (goals, plans)
executive_memory = MemoryBlock(
    id="memory-plan-001",
    memory_type=MemoryType.EXECUTIVE,
    content="Treatment plan: lifestyle modifications for 3 months, then reassess for medication",
    importance_score=0.8,
    metadata={
        "plan_type": "treatment",
        "timeline": "3_months",
        "review_date": "2024-04-15"
    }
)
```

#### Memory Types
- **Episodic**: Events, experiences, specific encounters
- **Procedural**: Skills, protocols, how-to knowledge
- **Executive**: Goals, plans, high-level strategies

#### Key Features
- **Importance scoring** (0.0-1.0) for memory prioritization
- **Access tracking** with count and timestamp
- **Memory linking** for related memories
- **Rich metadata** for context and categorization

### Evidence

Manages clinical evidence with provenance tracking and quality assessment.

```python
from hacs_core import Evidence, EvidenceType

# Create clinical guideline evidence
guideline_evidence = Evidence(
    id="evidence-aha-bp-2024",
    evidence_type=EvidenceType.GUIDELINE,
    citation="2024 AHA/ACC Guideline for the Management of Blood Pressure in Adults",
    content="Stage 1 hypertension (130-139/80-89 mmHg) should be managed with lifestyle modifications as first-line therapy.",
    confidence_score=0.95,
    quality_score=0.9,
    provenance={
        "organization": "American Heart Association",
        "publication_date": "2024-01-01",
        "evidence_level": "A",
        "study_type": "systematic_review"
    }
)

# Create research study evidence
study_evidence = Evidence(
    id="evidence-dash-study",
    evidence_type=EvidenceType.RESEARCH_STUDY,
    citation="DASH Diet and Blood Pressure Reduction: A Randomized Controlled Trial",
    content="DASH diet implementation resulted in average systolic BP reduction of 11.4 mmHg in hypertensive patients.",
    confidence_score=0.85,
    quality_score=0.8,
    vector_id="embedding-dash-001",  # For RAG integration
    tags=["nutrition", "hypertension", "lifestyle"]
)
```

#### Evidence Types
- **RESEARCH_STUDY**: Peer-reviewed research
- **GUIDELINE**: Clinical practice guidelines
- **EXPERT_OPINION**: Professional consensus
- **CASE_REPORT**: Individual case studies
- **SYSTEMATIC_REVIEW**: Meta-analyses
- **RCT**: Randomized controlled trials
- **OBSERVATIONAL_STUDY**: Cohort/case-control studies
- **CLINICAL_NOTE**: Provider documentation
- **PATIENT_REPORTED**: Patient-generated data
- **SENSOR_DATA**: Device/sensor measurements

#### Key Features
- **Quality assessment** with confidence and quality scores
- **Vector integration** for RAG (Retrieval-Augmented Generation)
- **Provenance tracking** with detailed metadata
- **Tag management** for categorization
- **Review workflow** with status tracking

### Actor

Implements comprehensive security and permission management for healthcare agents.

```python
from hacs_core import Actor, ActorRole

# Create physician actor
physician = Actor(
    id="dr-smith-001",
    name="Dr. Emily Smith",
    role=ActorRole.PHYSICIAN,
    permissions=[
        "patient:*",           # Full patient access
        "observation:read",    # Read observations
        "observation:create",  # Create observations
        "memory:*",           # Full memory access
        "evidence:read"       # Read evidence
    ],
    is_active=True,
    organization="Springfield General Hospital",
    contact_info={
        "email": "e.smith@sgh.org",
        "phone": "+1-555-0123"
    }
)

# Create nurse actor with limited permissions
nurse = Actor(
    id="nurse-johnson-001",
    name="Sarah Johnson, RN",
    role=ActorRole.NURSE,
    permissions=[
        "patient:read",
        "observation:*",
        "memory:read"
    ],
    is_active=True,
    organization="Springfield General Hospital"
)

# Create system actor for automated processes
system_actor = Actor(
    id="system-alerts-001",
    name="Clinical Alert System",
    role=ActorRole.SYSTEM,
    permissions=[
        "observation:read",
        "evidence:read",
        "memory:create"
    ],
    is_active=True
)
```

#### Actor Roles
- **PHYSICIAN**: Medical doctors
- **NURSE**: Registered nurses
- **PATIENT**: Healthcare consumers
- **RESEARCHER**: Clinical researchers
- **ADMINISTRATOR**: System administrators
- **TECHNICIAN**: Medical technicians
- **PHARMACIST**: Pharmacy professionals
- **THERAPIST**: Physical/occupational therapists
- **SOCIAL_WORKER**: Healthcare social workers
- **CASE_MANAGER**: Care coordinators
- **SYSTEM**: Automated systems
- **AGENT**: AI/software agents

#### Permission System
```python
# Check permissions
if physician.has_permission("patient:create"):
    print("✅ Can create patients")

if physician.has_permission("observation:*"):
    print("✅ Full observation access")

# Add permissions
physician.add_permission("evidence:create")

# Session management
physician.start_session()
print(f"Session ID: {physician.session_id}")

# Audit trail
for event in physician.get_audit_events():
    print(f"{event.timestamp}: {event.action} by {event.actor_id}")
```

## 🔧 Utility Functions

### JSON Schema Export
```python
from hacs_core import BaseResource

# Get JSON schema for LLM function specifications
schema = BaseResource.model_json_schema()
print(f"Schema fields: {len(schema['properties'])}")

# Export for specific resource
memory_schema = MemoryBlock.model_json_schema()
print(f"Memory schema: {memory_schema['title']}")
```

### Validation Helpers
```python
from hacs_core import Evidence

# Validate evidence data
try:
    evidence = Evidence(
        citation="Test Citation",
        content="Test content",
        confidence_score=1.5  # Invalid: > 1.0
    )
except ValidationError as e:
    print(f"Validation error: {e}")
```

## 🧪 Testing

The core module includes comprehensive tests covering all functionality:

```bash
# Run core module tests
uv run --package hacs-core pytest

# Run with coverage
uv run --package hacs-core pytest --cov=hacs_core

# Run specific test categories
uv run --package hacs-core pytest -k "test_memory"
uv run --package hacs-core pytest -k "test_evidence"
uv run --package hacs-core pytest -k "test_actor"
```

## 📊 Performance Characteristics

The core module is optimized for agent workloads:

- **Model Creation**: <1ms for all core models
- **Validation**: <1ms for complex models with 20+ fields
- **JSON Schema Generation**: <5ms for all models
- **Memory Operations**: <1ms for store/retrieve operations
- **Permission Checks**: <0.1ms for ACL evaluation

## 🔗 Integration Patterns

### With Agent Frameworks
```python
# LangGraph integration
from hacs_core import MemoryBlock

def create_langgraph_memory(state_data: dict) -> MemoryBlock:
    return MemoryBlock(
        memory_type="procedural",
        content=f"LangGraph state: {state_data}",
        metadata={"framework": "langgraph", "state": state_data}
    )

# CrewAI integration
def create_crewai_evidence(task_result: str) -> Evidence:
    return Evidence(
        evidence_type="expert_opinion",
        citation="CrewAI Task Result",
        content=task_result,
        metadata={"framework": "crewai", "task_type": "analysis"}
    )
```

### With Vector Databases
```python
# Prepare for vector storage
evidence = Evidence(
    citation="Clinical Study",
    content="Long clinical text content...",
    vector_id="embedding-001"  # Reference to vector DB
)

# Extract for embedding
embedding_text = f"{evidence.citation}\n{evidence.content}"
# Store embedding_text in your vector database
```

## 🚀 Best Practices

### Resource Identification
```python
# Use meaningful, hierarchical IDs
patient_id = "patient-sgh-12345"
memory_id = f"memory-{patient_id}-encounter-001"
evidence_id = "evidence-aha-bp-guidelines-2024"
```

### Memory Management
```python
# Set appropriate importance scores
critical_memory = MemoryBlock(
    importance_score=0.9,  # High importance for critical events
    content="Patient allergic to penicillin - anaphylaxis risk"
)

routine_memory = MemoryBlock(
    importance_score=0.3,  # Low importance for routine observations
    content="Patient prefers morning appointments"
)
```

### Evidence Quality
```python
# Include comprehensive provenance
evidence = Evidence(
    confidence_score=0.95,  # High confidence for peer-reviewed studies
    quality_score=0.9,      # High quality for systematic reviews
    provenance={
        "study_design": "randomized_controlled_trial",
        "sample_size": 1000,
        "follow_up_duration": "12_months",
        "peer_reviewed": True
    }
)
```

### Actor Security
```python
# Use principle of least privilege
nurse_actor = Actor(
    permissions=[
        "patient:read",        # Can read patient data
        "observation:create",  # Can create observations
        "observation:read"     # Can read observations
        # No delete or admin permissions
    ]
)

# Always check permissions before operations
if actor.has_permission("patient:create"):
    # Proceed with patient creation
    pass
else:
    raise PermissionError("Insufficient permissions")
```

## 📚 API Reference

### BaseResource
- `update_timestamp()`: Update the updated_at field
- `age_seconds`: Property returning resource age in seconds
- `model_json_schema()`: Generate JSON schema

### MemoryBlock
- `record_access()`: Record memory access and update statistics
- `link_memory(memory_id)`: Link to another memory
- `update_importance(score)`: Update importance score

### Evidence
- `add_tag(tag)`: Add a tag for categorization
- `remove_tag(tag)`: Remove a tag
- `update_quality_score(score)`: Update quality assessment
- `link_to_resource(resource_id)`: Link evidence to a resource

### Actor
- `has_permission(permission)`: Check if actor has specific permission
- `add_permission(permission)`: Add a permission
- `start_session()`: Start a new session
- `end_session()`: End current session
- `get_audit_events()`: Retrieve audit trail

## 🔄 Version History

- **v0.1.0**: Initial release with core models and functionality
- **v0.1.1**: Enhanced validation and error handling
- **v0.1.2**: Performance optimizations and bug fixes

## 🤝 Contributing

See the [Contributing Guidelines](../contributing/guidelines.md) for information on how to contribute to the hacs-core module.

---

The `hacs-core` module provides the solid foundation that all other HACS packages build upon. Its robust models and security features enable sophisticated healthcare AI applications while maintaining clinical safety and compliance standards. 