"""
Integration Tests for HACS CRUD Tools

Tests CRUD operations, structured-IO, and validation system with Actor permissions.
"""

import pytest
from datetime import date

from hacs_core import Actor, ActorRole
from hacs_models import Patient, Observation
from hacs_models import AdministrativeGender, ObservationStatus
from hacs_tools import (
    CreateResource,
    ReadResource,
    UpdateResource,
    DeleteResource,
    ListResources,
    GetAuditLog,
    validate_before_create,
    generate_function_spec,
    validate_llm_output,
    create_tool_executor,
    ToolCallPattern,
    ToolCall,
    ValidationLevel,
    StorageBackend,
    set_storage_backend,
)


class TestCRUDOperations:
    """Test CRUD operations with Actor permissions."""

    @pytest.fixture
    def physician_actor(self):
        """Create a physician actor with full permissions."""
        return Actor(
            id="physician-test-001",
            name="Dr. Test Physician",
            role=ActorRole.PHYSICIAN,
            permissions=["*:*"],
            is_active=True,
        )

    @pytest.fixture
    def nurse_actor(self):
        """Create a nurse actor with limited permissions."""
        return Actor(
            id="nurse-test-001",
            name="Test Nurse",
            role=ActorRole.NURSE,
            permissions=["patient:read", "observation:read"],
            is_active=True,
        )

    @pytest.fixture
    def test_patient(self):
        """Create a test patient."""
        return Patient(
            id="patient-test-001",
            given=["John"],
            family="Doe",
            gender=AdministrativeGender.MALE,
            birth_date=date(1980, 5, 15),
            active=True,
        )

    @pytest.fixture
    def test_observation(self):
        """Create a test observation."""
        return Observation(
            id="obs-test-001",
            status=ObservationStatus.FINAL,
            code={
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "8480-6",
                        "display": "Systolic blood pressure",
                    }
                ]
            },
            subject="patient-test-001",
            value_quantity={"value": 120, "unit": "mmHg"},
        )

    def test_create_resource_success(self, physician_actor, test_patient):
        """Test successful resource creation."""
        # Reset storage
        set_storage_backend(StorageBackend.MEMORY)

        resource_id = CreateResource(test_patient, physician_actor)
        assert resource_id == test_patient.id

    def test_create_resource_permission_denied(self, nurse_actor, test_patient):
        """Test resource creation with insufficient permissions."""
        set_storage_backend(StorageBackend.MEMORY)

        with pytest.raises(Exception) as exc_info:
            CreateResource(test_patient, nurse_actor)

        assert "lacks permission" in str(exc_info.value)

    def test_read_resource_success(self, physician_actor, test_patient):
        """Test successful resource reading."""
        set_storage_backend(StorageBackend.MEMORY)

        # Create first
        CreateResource(test_patient, physician_actor)

        # Then read
        retrieved = ReadResource("Patient", test_patient.id, physician_actor)
        assert isinstance(retrieved, Patient)  # Type guard
        assert retrieved.id == test_patient.id
        assert retrieved.family == test_patient.family

    def test_update_resource_success(self, physician_actor, test_patient):
        """Test successful resource update."""
        set_storage_backend(StorageBackend.MEMORY)

        # Create first
        CreateResource(test_patient, physician_actor)

        # Update
        test_patient.family = "Smith"
        updated = UpdateResource(test_patient, physician_actor)
        assert isinstance(updated, Patient)  # Type guard
        assert updated.family == "Smith"

    def test_delete_resource_success(self, physician_actor, test_patient):
        """Test successful resource deletion."""
        set_storage_backend(StorageBackend.MEMORY)

        # Create first
        CreateResource(test_patient, physician_actor)

        # Delete
        result = DeleteResource("Patient", test_patient.id, physician_actor)
        assert result is True

        # Verify deletion
        with pytest.raises(Exception) as exc_info:
            ReadResource("Patient", test_patient.id, physician_actor)
        assert "not found" in str(exc_info.value)

    def test_list_resources(self, physician_actor, test_patient):
        """Test resource listing."""
        set_storage_backend(StorageBackend.MEMORY)

        # Create multiple patients
        CreateResource(test_patient, physician_actor)

        patient2 = Patient(
            id="patient-test-002",
            given=["Jane"],
            family="Smith",
            gender=AdministrativeGender.FEMALE,
            birth_date=date(1990, 8, 20),
            active=True,
        )
        CreateResource(patient2, physician_actor)

        # List patients
        patients = ListResources("Patient", physician_actor, limit=10)
        assert len(patients) == 2
        assert any(p.id == test_patient.id for p in patients)
        assert any(p.id == patient2.id for p in patients)

    def test_audit_logging(self, physician_actor, test_patient):
        """Test audit logging functionality."""
        set_storage_backend(StorageBackend.MEMORY)

        # Perform operations
        CreateResource(test_patient, physician_actor)
        ReadResource("Patient", test_patient.id, physician_actor)

        # Check audit log
        audit_events = GetAuditLog(physician_actor, limit=10)
        assert len(audit_events) >= 2

        # Verify event types
        operations = [event.operation for event in audit_events]
        assert "create" in operations
        assert "read" in operations


class TestStructuredIO:
    """Test structured-IO for LLM integration."""

    def test_generate_function_spec_openai(self):
        """Test OpenAI function spec generation."""
        spec = generate_function_spec(Patient, ToolCallPattern.OPENAI)

        assert spec["type"] == "function"
        assert "function" in spec
        assert spec["function"]["name"] == "create_patient"
        assert "parameters" in spec["function"]
        assert "properties" in spec["function"]["parameters"]

        # Check for key Patient fields
        properties = spec["function"]["parameters"]["properties"]
        assert "given" in properties
        assert "family" in properties
        assert "gender" in properties

    def test_generate_function_spec_anthropic(self):
        """Test Anthropic function spec generation."""
        spec = generate_function_spec(Patient, ToolCallPattern.ANTHROPIC)

        assert spec["name"] == "create_patient"
        assert "input_schema" in spec
        assert "properties" in spec["input_schema"]

        properties = spec["input_schema"]["properties"]
        assert "given" in properties
        assert "family" in properties

    def test_validate_llm_output_success(self):
        """Test successful LLM output validation."""
        spec = generate_function_spec(Patient, ToolCallPattern.OPENAI)

        llm_output = {
            "id": "patient-llm-001",
            "given": ["Alice"],
            "family": "Johnson",
            "gender": "female",
            "birth_date": "1990-03-20",
            "active": True,
        }

        validated = validate_llm_output(spec, llm_output, Patient)
        assert isinstance(validated, Patient)
        assert validated.given == ["Alice"]
        assert validated.family == "Johnson"
        assert validated.gender == AdministrativeGender.FEMALE

    def test_tool_executor(self):
        """Test tool executor functionality."""
        actor = Actor(
            id="executor-test-001",
            name="Test Executor",
            role=ActorRole.PHYSICIAN,
            permissions=["*:*"],
            is_active=True,
        )

        executor = create_tool_executor(actor)

        # Check available functions
        assert "create_patient" in executor.available_functions
        assert "read_patient" in executor.available_functions
        assert "create_observation" in executor.available_functions

        # Test tool call execution
        tool_call = ToolCall(
            function_name="create_patient",
            arguments={
                "id": "patient-exec-001",
                "given": ["Test"],
                "family": "Patient",
                "gender": "male",
                "active": True,
            },
        )

        result = executor.execute_tool_call(tool_call)
        assert result.success is True
        assert result.result == "patient-exec-001"


class TestValidation:
    """Test validation system."""

    @pytest.fixture
    def test_actor(self):
        """Create test actor for validation."""
        return Actor(
            id="validator-test-001",
            name="Test Validator",
            role=ActorRole.PHYSICIAN,
            permissions=["*:*"],
            is_active=True,
        )

    def test_validate_patient_success(self, test_actor):
        """Test successful patient validation."""
        patient = Patient(
            id="patient-valid-001",
            given=["John"],
            family="Doe",
            gender=AdministrativeGender.MALE,
            birth_date=date(1980, 5, 15),
            active=True,
        )

        result = validate_before_create(patient, test_actor, ValidationLevel.STANDARD)
        assert result.valid is True
        assert len(result.errors) == 0

    def test_validate_patient_business_rules(self, test_actor):
        """Test patient business rule validation."""
        # Test future birth date
        patient = Patient(
            id="patient-invalid-001",
            given=["John"],
            family="Doe",
            gender=AdministrativeGender.MALE,
            birth_date=date(2030, 1, 1),  # Future date
            active=True,
        )

        result = validate_before_create(patient, test_actor, ValidationLevel.STANDARD)
        assert result.valid is False
        assert any("future" in error.lower() for error in result.errors)

    def test_validate_observation_ranges(self, test_actor):
        """Test observation value range validation."""
        # Test invalid blood pressure
        observation = Observation(
            id="obs-invalid-001",
            status=ObservationStatus.FINAL,
            code={
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "8480-6",
                        "display": "Systolic blood pressure",
                    }
                ]
            },
            subject="patient-001",
            value_quantity={"value": 500, "unit": "mmHg"},  # Too high
        )

        result = validate_before_create(
            observation, test_actor, ValidationLevel.STANDARD
        )
        assert result.valid is False
        assert any("reasonable range" in error for error in result.errors)

    def test_validate_permission_denied(self):
        """Test validation with insufficient permissions."""
        limited_actor = Actor(
            id="limited-001",
            name="Limited Actor",
            role=ActorRole.NURSE,
            permissions=["patient:read"],  # No create permission
            is_active=True,
        )

        patient = Patient(
            id="patient-perm-001",
            given=["Test"],
            family="Patient",
            gender=AdministrativeGender.MALE,
            active=True,
        )

        result = validate_before_create(
            patient, limited_actor, ValidationLevel.STANDARD
        )
        assert result.valid is False
        assert any("lacks permission" in error for error in result.errors)


class TestIntegrationWorkflows:
    """Test end-to-end integration workflows."""

    def test_complete_patient_workflow(self):
        """Test complete patient management workflow."""
        set_storage_backend(StorageBackend.MEMORY)

        # Create physician
        physician = Actor(
            id="workflow-physician-001",
            name="Dr. Workflow",
            role=ActorRole.PHYSICIAN,
            permissions=["*:*"],
            is_active=True,
        )

        # 1. Create patient
        patient = Patient(
            id="workflow-patient-001",
            given=["Workflow"],
            family="Test",
            gender=AdministrativeGender.FEMALE,
            birth_date=date(1985, 6, 10),
            active=True,
        )

        # Validate before creation
        validation = validate_before_create(
            patient, physician, ValidationLevel.STANDARD
        )
        assert validation.valid is True

        # Create patient
        patient_id = CreateResource(patient, physician)
        assert patient_id == patient.id

        # 2. Create observation for patient
        observation = Observation(
            id="workflow-obs-001",
            status=ObservationStatus.FINAL,
            code={
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "8867-4",
                        "display": "Heart rate",
                    }
                ]
            },
            subject=patient.id,
            value_quantity={"value": 72, "unit": "/min"},
        )

        obs_id = CreateResource(observation, physician)
        assert obs_id == observation.id

        # 3. Read resources
        retrieved_patient = ReadResource("Patient", patient.id, physician)
        retrieved_obs = ReadResource("Observation", observation.id, physician)

        assert isinstance(retrieved_patient, Patient)  # Type guard
        assert isinstance(retrieved_obs, Observation)  # Type guard
        assert retrieved_patient.family == "Test"
        assert retrieved_obs.get_numeric_value() == 72

        # 4. Update patient
        patient.family = "Updated"
        updated_patient = UpdateResource(patient, physician)
        assert isinstance(updated_patient, Patient)  # Type guard
        assert updated_patient.family == "Updated"

        # 5. Check audit trail
        audit_events = GetAuditLog(physician, limit=10)
        assert len(audit_events) >= 4  # create, create, read, read, update

        operations = [event.operation for event in audit_events]
        assert "create" in operations
        assert "read" in operations
        assert "update" in operations

    def test_llm_integration_workflow(self):
        """Test LLM integration workflow."""
        # Create actor
        actor = Actor(
            id="llm-actor-001",
            name="LLM Actor",
            role=ActorRole.SYSTEM,
            permissions=["*:*"],
            is_active=True,
        )

        # 1. Generate function specs
        patient_spec = generate_function_spec(Patient, ToolCallPattern.OPENAI)
        obs_spec = generate_function_spec(Observation, ToolCallPattern.OPENAI)

        assert patient_spec["function"]["name"] == "create_patient"
        assert obs_spec["function"]["name"] == "create_observation"

        # 2. Simulate LLM output
        llm_patient_data = {
            "id": "llm-patient-001",
            "given": ["AI"],
            "family": "Generated",
            "gender": "other",
            "birth_date": "1995-01-01",
            "active": True,
        }

        # 3. Validate and create from LLM output
        validated_patient = validate_llm_output(patient_spec, llm_patient_data, Patient)
        assert isinstance(validated_patient, Patient)

        # 4. Create via tool executor
        executor = create_tool_executor(actor)
        tool_call = ToolCall(function_name="create_patient", arguments=llm_patient_data)

        result = executor.execute_tool_call(tool_call)
        assert result.success is True
        assert result.result == "llm-patient-001"


if __name__ == "__main__":
    # Run basic tests
    print("Running CRUD Tools Integration Tests...")

    # Test basic CRUD
    physician = Actor(
        id="test-physician",
        name="Test Doctor",
        role=ActorRole.PHYSICIAN,
        permissions=["*:*"],
        is_active=True,
    )

    patient = Patient(
        id="test-patient",
        given=["Test"],
        family="Patient",
        gender=AdministrativeGender.MALE,
        active=True,
    )

    set_storage_backend(StorageBackend.MEMORY)

    # Test CRUD operations
    patient_id = CreateResource(patient, physician)
    print(f"✅ Created patient: {patient_id}")

    retrieved = ReadResource("Patient", patient_id, physician)
    assert isinstance(retrieved, Patient)  # Type guard
    print(f"✅ Retrieved patient: {retrieved.display_name}")

    # Test function spec generation
    spec = generate_function_spec(Patient, ToolCallPattern.OPENAI)
    print(f"✅ Generated function spec: {spec['function']['name']}")

    # Test validation
    validation = validate_before_create(patient, physician)
    print(f"✅ Validation result: {validation.valid}")

    print("✅ All basic tests passed!")
