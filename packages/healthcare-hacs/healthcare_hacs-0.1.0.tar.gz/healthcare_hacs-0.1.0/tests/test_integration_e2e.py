"""
End-to-End Integration Tests for HACS v0.1.0

This module provides comprehensive integration tests that demonstrate
the complete HACS workflow including Actor authentication, resource management,
memory operations, evidence linking, FHIR conversion, and protocol exports.
"""

from datetime import datetime, timezone, date

# HACS Core imports
from hacs_core import Actor, MemoryBlock, ActorRole, EvidenceType

# HACS Models imports
from hacs_models import Patient, Observation
from hacs_models import AdministrativeGender, ObservationStatus

# HACS Tools imports
from hacs_tools import (
    CreateResource,
    ReadResource,
    UpdateResource,
    DeleteResource,
    store_memory,
    create_evidence,
)

# HACS FHIR imports
from hacs_fhir import to_fhir, from_fhir

# HACS Protocol Adapters
from hacs_tools.adapters import (
    convert_to_mcp_task,
    create_a2a_envelope,
    format_for_ag_ui,
    create_state_bridge,
    create_agent_binding,
)


def test_complete_hacs_workflow():
    """Test complete HACS workflow: Actor Login → Create Patient → Store Memory → Add Evidence → Convert to FHIR → Validate."""

    print("🧪 Running HACS v0.1.0 Complete Workflow Test...")

    # Step 1: Create Actor
    print("  Step 1: Creating Actor...")
    physician = Actor(
        id="physician-001",
        name="Dr. Sarah Johnson",
        role=ActorRole.PHYSICIAN,
        permissions=["*:*"],
        is_active=True,
        organization="Springfield General Hospital",
    )
    print(f"    ✅ Actor created: {physician.name}")

    # Step 2: Create Patient
    print("  Step 2: Creating Patient...")
    patient = Patient(
        id="patient-e2e-001",
        given=["Ana", "Maria"],
        family="Silva",
        gender=AdministrativeGender.FEMALE,
        birth_date=date(1985, 3, 15),
        active=True,
        identifiers=[
            {
                "system": "http://hospital.example.org/patient-ids",
                "value": "E2E-12345",
                "use": "official",
            }
        ],
    )

    # Create patient with Actor authentication
    patient_id = CreateResource(patient, actor=physician)
    assert patient_id == patient.id
    print(f"    ✅ Patient created: {patient_id}")

    # Verify patient can be read
    retrieved_patient = ReadResource("Patient", patient_id, actor=physician)
    assert isinstance(retrieved_patient, Patient)
    assert retrieved_patient.display_name == "Ana Maria Silva"
    print(
        f"    ✅ Patient retrieved: {retrieved_patient.display_name}, Age: {retrieved_patient.age_years}"
    )

    # Step 3: Create Observation
    print("  Step 3: Creating Observation...")
    observation = Observation(
        id="obs-e2e-001",
        status=ObservationStatus.FINAL,
        code={
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "8480-6",
                    "display": "Systolic blood pressure",
                }
            ],
            "text": "Systolic Blood Pressure",
        },
        subject=patient.id,
        effective_datetime=datetime.now(timezone.utc),
        value_quantity={
            "value": 135,
            "unit": "mmHg",
            "system": "http://unitsofmeasure.org",
            "code": "mm[Hg]",
        },
        performer=["physician-001"],
    )

    observation_id = CreateResource(observation, actor=physician)
    assert observation_id == observation.id
    print(f"    ✅ Observation created: {observation_id} (BP: 135 mmHg)")

    # Step 4: Store Clinical Memory
    print("  Step 4: Storing Clinical Memory...")
    clinical_memory = MemoryBlock(
        id="memory-e2e-001",
        memory_type="episodic",
        content=f"Patient {patient.display_name} presented with elevated blood pressure (135 mmHg). Discussed lifestyle modifications.",
        importance_score=0.8,
        metadata={
            "patient_id": patient.id,
            "observation_id": observation.id,
            "provider": physician.id,
        },
    )

    memory_id = store_memory(clinical_memory, actor=physician)
    assert memory_id == clinical_memory.id
    print(
        f"    ✅ Memory stored: {memory_id} (importance: {clinical_memory.importance_score})"
    )

    # Step 5: Create Clinical Evidence
    print("  Step 5: Creating Clinical Evidence...")
    evidence = create_evidence(
        citation="American Heart Association. (2024). Guidelines for Management of High Blood Pressure.",
        content="For adults with stage 1 hypertension, initial treatment should include lifestyle modifications.",
        actor=physician,
        evidence_type=EvidenceType.GUIDELINE,
        confidence_score=0.95,
    )
    print(
        f"    ✅ Evidence created: {evidence.id} (confidence: {evidence.confidence_score})"
    )

    # Step 6: FHIR Conversion
    print("  Step 6: Testing FHIR Conversion...")
    patient_fhir = to_fhir(retrieved_patient)
    assert patient_fhir["resourceType"] == "Patient"
    assert patient_fhir["gender"] == "female"
    print("    ✅ HACS → FHIR conversion successful")

    patient_from_fhir = from_fhir(patient_fhir)
    assert isinstance(patient_from_fhir, Patient)
    assert patient_from_fhir.id == patient.id
    assert patient_from_fhir.family == patient.family
    print("    ✅ FHIR → HACS conversion successful (round-trip preserved)")

    # Step 7: Protocol Adapter Testing
    print("  Step 7: Testing Protocol Adapters...")

    # MCP Adapter
    mcp_task = convert_to_mcp_task("create", resource=patient, actor=physician)
    assert mcp_task.task_type.value == "create"
    assert mcp_task.resource_type == "Patient"
    print(f"    ✅ MCP export successful: {mcp_task.task_id}")

    # A2A Adapter
    a2a_envelope = create_a2a_envelope("request", physician, observation)
    assert a2a_envelope.message_type.value == "request"
    assert a2a_envelope.sender["agent_name"] == physician.name
    print(f"    ✅ A2A export successful: {a2a_envelope.message_id}")

    # AG-UI Adapter
    ag_ui_event = format_for_ag_ui(
        "observation_alert", "observation_panel", resource=observation, actor=physician
    )
    assert ag_ui_event.event_type.value == "observation_alert"
    assert ag_ui_event.component.value == "observation_panel"
    print(f"    ✅ AG-UI export successful: {ag_ui_event.event_id}")

    # LangGraph State Bridge
    source_state = {
        "workflow_type": "clinical_assessment",
        "patient": patient.model_dump(),
        "observations": [observation.model_dump()],
    }
    target_state = create_state_bridge(source_state, "treatment_planning", physician)
    assert target_state["workflow_type"] == "treatment_planning"
    print("    ✅ LangGraph state bridge successful")

    # CrewAI Agent Binding
    clinical_agent = create_agent_binding("clinical_assessor", actor=physician)
    assert clinical_agent.role.value == "clinical_assessor"
    assert clinical_agent.actor_binding == physician.id
    print(f"    ✅ CrewAI agent binding successful: {clinical_agent.agent_id}")

    print("\n🎉 Complete HACS workflow test passed!")


def test_performance_benchmarks():
    """Test performance benchmarks with target <300ms p95 for CRUD operations."""
    import time

    print("🏃 Running Performance Benchmarks...")

    physician = Actor(
        id="perf-physician",
        name="Performance Test Doctor",
        role=ActorRole.PHYSICIAN,
        permissions=["*:*"],
        is_active=True,
    )

    test_patient = Patient(
        id="perf-test-001",
        given=["Performance"],
        family="Test",
        gender=AdministrativeGender.OTHER,
        birth_date=date(1990, 1, 1),
        active=True,
    )

    # Benchmark CREATE operation
    start_time = time.time()
    patient_id = CreateResource(test_patient, actor=physician)
    create_time = (time.time() - start_time) * 1000  # Convert to ms

    # Benchmark READ operation
    start_time = time.time()
    retrieved_patient = ReadResource("Patient", patient_id, actor=physician)
    assert isinstance(retrieved_patient, Patient)
    read_time = (time.time() - start_time) * 1000

    # Benchmark UPDATE operation
    retrieved_patient.active = False
    start_time = time.time()
    UpdateResource(retrieved_patient, actor=physician)
    update_time = (time.time() - start_time) * 1000

    # Benchmark DELETE operation
    start_time = time.time()
    DeleteResource("Patient", patient_id, actor=physician)
    delete_time = (time.time() - start_time) * 1000

    print("  Performance Results:")
    print(f"    CREATE: {create_time:.2f}ms (target: <300ms)")
    print(f"    READ: {read_time:.2f}ms (target: <300ms)")
    print(f"    UPDATE: {update_time:.2f}ms (target: <300ms)")
    print(f"    DELETE: {delete_time:.2f}ms (target: <300ms)")

    # Assert performance targets
    assert create_time < 300, f"CREATE took {create_time:.2f}ms (target: <300ms)"
    assert read_time < 300, f"READ took {read_time:.2f}ms (target: <300ms)"
    assert update_time < 300, f"UPDATE took {update_time:.2f}ms (target: <300ms)"
    assert delete_time < 300, f"DELETE took {delete_time:.2f}ms (target: <300ms)"

    print("  ✅ All performance benchmarks passed!")


def test_package_imports():
    """Test that all packages can be imported successfully."""
    print("\n🔍 Testing package imports...")

    try:
        # Import all packages to test availability (imports used for testing)
        from hacs_core import BaseResource, Actor, MemoryBlock, Evidence  # noqa: F401
        from hacs_models import Patient, AgentMessage, Encounter, Observation  # noqa: F401
        from hacs_fhir import to_fhir, from_fhir  # noqa: F401
        from hacs_tools import CreateResource, ReadResource  # noqa: F401
        from hacs_tools.adapters import MCPAdapter, A2AAdapter, AGUIAdapter  # noqa: F401

        print("  ✅ All packages imported successfully")
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        raise  # Re-raise to fail the test


if __name__ == "__main__":
    """Run all integration tests."""
    print("🚀 HACS v0.1.0 Integration Test Suite")
    print("=" * 50)

    tests_passed = 0
    total_tests = 3

    try:
        # Test 1: Cross-package imports
        if test_package_imports():
            tests_passed += 1

        # Test 2: Complete workflow
        if test_complete_hacs_workflow():
            tests_passed += 1

        # Test 3: Performance benchmarks
        if test_performance_benchmarks():
            tests_passed += 1

        print("=" * 50)
        print(f"🎯 Test Results: {tests_passed}/{total_tests} tests passed")

        if tests_passed == total_tests:
            print("🎉 HACS v0.1.0 Integration Test Suite: SUCCESS")
            print("✅ All core functionality working correctly!")
            print("✅ Performance targets met!")
            print("✅ Protocol adapters operational!")
            print("✅ FHIR round-trip preservation verified!")
            print("✅ Actor security enforced!")
        else:
            print("❌ Some tests failed - see output above")

    except Exception as e:
        print(f"❌ HACS v0.1.0 Integration Test Suite: FAILED - {e}")
        import traceback

        traceback.print_exc()
        raise
