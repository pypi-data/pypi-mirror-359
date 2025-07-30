# Basic Usage Examples

This guide provides practical examples of using HACS for common healthcare AI workflows. Each example builds upon the previous ones, showing how to create, manage, and integrate healthcare data with AI agents.

## 🏥 Example 1: Basic Patient Management

Let's start with creating and managing patient records:

```python
from hacs_models import Patient
from hacs_core import Actor
from hacs_tools import CreateResource, ReadResource, UpdateResource
from datetime import date

# Create a healthcare provider
physician = Actor(
    id="dr-martinez-001",
    name="Dr. Sofia Martinez",
    role="physician",
    permissions=["patient:*", "observation:*", "encounter:*"],
    is_active=True,
    organization="Community Health Center"
)

# Create a patient with comprehensive information
patient = Patient(
    id="patient-garcia-001",
    given=["Carlos", "Eduardo"],
    family="Garcia",
    gender="male",
    birth_date=date(1978, 9, 22),
    active=True,
    identifiers=[
        {
            "system": "http://community-health.org/mrn",
            "value": "CHC789012",
            "type": "MR"
        }
    ],
    telecom=[
        {
            "system": "phone",
            "value": "+1-555-0198",
            "use": "mobile"
        },
        {
            "system": "email",
            "value": "carlos.garcia@email.com",
            "use": "home"
        }
    ],
    address=[
        {
            "use": "home",
            "line": ["789 Oak Avenue"],
            "city": "Springfield",
            "state": "IL",
            "postal_code": "62704",
            "country": "US"
        }
    ],
    marital_status="married",
    language="es-US",  # Spanish speaker
    agent_context={
        "preferred_language": "spanish",
        "communication_preference": "phone",
        "health_concerns": ["diabetes", "hypertension"],
        "cultural_considerations": ["family_involvement_important"]
    }
)

# Store the patient
patient_id = CreateResource(patient, actor=physician)
print(f"✅ Created patient: {patient.display_name}")
print(f"   Age: {patient.age_years} years")
print(f"   MRN: {patient.primary_identifier}")
print(f"   Language: {patient.language}")

# Retrieve the patient
retrieved_patient = ReadResource("Patient", patient_id, actor=physician)
print(f"✅ Retrieved patient: {retrieved_patient.display_name}")

# Update patient information
patient.telecom.append({
    "system": "phone",
    "value": "+1-555-0199",
    "use": "work"
})
updated_patient = UpdateResource(patient, actor=physician)
print(f"✅ Updated patient with work phone")
```

## 🩺 Example 2: Clinical Observations

Creating and managing clinical observations with proper FHIR coding:

```python
from hacs_models import Observation
from datetime import datetime

# Create a blood pressure observation
bp_observation = Observation(
    id="obs-bp-garcia-001",
    status="final",
    category=[
        {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "vital-signs",
                "display": "Vital Signs"
            }]
        }
    ],
    code={
        "coding": [{
            "system": "http://loinc.org",
            "code": "85354-9",
            "display": "Blood pressure panel with all children optional"
        }]
    },
    subject=patient_id,
    effective_datetime=datetime(2024, 1, 20, 10, 30),
    performer=[physician.id],
    component=[
        {
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "8480-6",
                    "display": "Systolic blood pressure"
                }]
            },
            "value_quantity": {
                "value": 155,
                "unit": "mmHg",
                "system": "http://unitsofmeasure.org"
            }
        },
        {
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "8462-4",
                    "display": "Diastolic blood pressure"
                }]
            },
            "value_quantity": {
                "value": 95,
                "unit": "mmHg",
                "system": "http://unitsofmeasure.org"
            }
        }
    ],
    reference_range=[
        {
            "low": {"value": 90, "unit": "mmHg"},
            "high": {"value": 140, "unit": "mmHg"},
            "type": "normal",
            "text": "Normal systolic BP range"
        }
    ],
    interpretation=[
        {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                "code": "H",
                "display": "High"
            }]
        }
    ],
    agent_context={
        "measurement_method": "automated_cuff",
        "patient_position": "seated",
        "ai_flagged": True,
        "alert_level": "high",
        "follow_up_required": True
    }
)

# Store the observation
obs_id = CreateResource(bp_observation, actor=physician)
print(f"✅ Created BP observation: {bp_observation.display_name}")
print(f"   Systolic: 155 mmHg (HIGH)")
print(f"   Diastolic: 95 mmHg (HIGH)")
print(f"   AI Flagged: {bp_observation.agent_context['ai_flagged']}")

# Create a glucose observation
glucose_observation = Observation(
    id="obs-glucose-garcia-001",
    status="final",
    category=[
        {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                "code": "laboratory",
                "display": "Laboratory"
            }]
        }
    ],
    code={
        "coding": [{
            "system": "http://loinc.org",
            "code": "33747-0",
            "display": "Fasting glucose [Mass/volume] in Serum or Plasma"
        }]
    },
    subject=patient_id,
    effective_datetime=datetime(2024, 1, 20, 8, 0),  # Fasting sample
    performer=[physician.id],
    value_quantity={
        "value": 128,
        "unit": "mg/dL",
        "system": "http://unitsofmeasure.org"
    },
    reference_range=[
        {
            "high": {"value": 100, "unit": "mg/dL"},
            "type": "normal",
            "text": "Normal fasting glucose"
        }
    ],
    interpretation=[
        {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                "code": "H",
                "display": "High"
            }]
        }
    ],
    agent_context={
        "fasting_status": True,
        "sample_type": "venous",
        "ai_interpretation": "Impaired fasting glucose - diabetes risk",
        "clinical_significance": "high"
    }
)

glucose_id = CreateResource(glucose_observation, actor=physician)
print(f"✅ Created glucose observation: 128 mg/dL (HIGH)")
```

## 🧠 Example 3: Memory and Evidence Management

Using HACS memory and evidence systems for clinical decision support:

```python
from hacs_core import MemoryBlock, Evidence, EvidenceType
from hacs_tools import store_memory, create_evidence

# Store episodic memory about the patient encounter
encounter_memory = MemoryBlock(
    id="memory-garcia-encounter-001",
    memory_type="episodic",
    content=f"Patient {patient.display_name} (MRN: {patient.primary_identifier}) "
           f"presented for routine checkup. Found elevated BP (155/95) and fasting glucose (128). "
           f"Patient is Spanish-speaking, married, with family history of diabetes. "
           f"Discussed lifestyle modifications and need for medication consideration.",
    importance_score=0.85,
    metadata={
        "patient_id": patient_id,
        "encounter_date": "2024-01-20",
        "clinical_findings": ["hypertension", "impaired_fasting_glucose"],
        "language": "spanish",
        "family_involvement": True,
        "follow_up_needed": True
    }
)

memory_id = store_memory(encounter_memory, actor=physician)
print(f"✅ Stored encounter memory: {memory_id}")

# Store procedural memory about diabetes screening
screening_memory = MemoryBlock(
    id="memory-diabetes-screening-protocol",
    memory_type="procedural",
    content="Diabetes screening protocol: Fasting glucose ≥126 mg/dL or random glucose ≥200 mg/dL "
           "indicates diabetes. Fasting glucose 100-125 mg/dL indicates prediabetes. "
           "For Spanish-speaking patients, provide materials in Spanish and involve family in education.",
    importance_score=0.7,
    metadata={
        "protocol_type": "screening",
        "condition": "diabetes",
        "cultural_considerations": ["spanish_language", "family_involvement"],
        "threshold_values": {
            "fasting_glucose_diabetes": 126,
            "fasting_glucose_prediabetes": 100
        }
    }
)

protocol_memory_id = store_memory(screening_memory, actor=physician)
print(f"✅ Stored screening protocol memory: {protocol_memory_id}")

# Create evidence for hypertension management
hypertension_evidence = create_evidence(
    citation="2024 AHA/ACC Guideline for the Management of Blood Pressure in Adults",
    content="For adults with stage 1 hypertension (systolic 130-139 or diastolic 80-89 mmHg) "
           "and estimated 10-year ASCVD risk <10%, lifestyle modifications are recommended. "
           "For stage 2 hypertension (≥140/90 mmHg), both lifestyle modifications and "
           "antihypertensive medication are recommended.",
    actor=physician,
    evidence_type=EvidenceType.GUIDELINE,
    confidence_score=0.95,
    quality_score=0.9,
    tags=["hypertension", "guidelines", "medication", "lifestyle"]
)

print(f"✅ Created hypertension evidence: {hypertension_evidence.id}")

# Create evidence for diabetes prevention
diabetes_evidence = create_evidence(
    citation="Diabetes Prevention Program Research Group (2002)",
    content="Lifestyle intervention including diet modification and increased physical activity "
           "reduced the incidence of type 2 diabetes by 58% in individuals with impaired glucose tolerance. "
           "Weight loss of 5-7% of body weight was associated with significant risk reduction.",
    actor=physician,
    evidence_type=EvidenceType.RESEARCH_STUDY,
    confidence_score=0.9,
    quality_score=0.85,
    tags=["diabetes", "prevention", "lifestyle", "weight_loss"]
)

print(f"✅ Created diabetes prevention evidence: {diabetes_evidence.id}")
```

## 🤖 Example 4: Agent Communication

Creating sophisticated agent messages with memory and evidence integration:

```python
from hacs_models import AgentMessage
from datetime import datetime, timedelta

# Create a comprehensive clinical assessment message
assessment_message = AgentMessage(
    id="msg-garcia-assessment-001",
    role="assistant",
    content="""Based on today's clinical findings for Carlos Garcia:

FINDINGS:
• Blood Pressure: 155/95 mmHg (Stage 2 Hypertension)
• Fasting Glucose: 128 mg/dL (Impaired Fasting Glucose)
• Patient is Spanish-speaking with family support system

RECOMMENDATIONS:
1. HYPERTENSION MANAGEMENT:
   - Initiate ACE inhibitor (lisinopril 10mg daily)
   - Lifestyle modifications: DASH diet, sodium restriction <2g/day
   - Home BP monitoring with Spanish-language instructions

2. DIABETES PREVENTION:
   - Refer to diabetes prevention program (Spanish-speaking counselor)
   - Target weight loss: 5-7% of current body weight
   - Follow-up HbA1c in 3 months

3. CULTURAL CONSIDERATIONS:
   - Provide educational materials in Spanish
   - Involve family in care planning
   - Schedule follow-up in 2 weeks for medication tolerance

FOLLOW-UP: 2 weeks (medication check), 3 months (comprehensive reassessment)""",
    
    related_to=[patient_id, obs_id, glucose_id],
    confidence_score=0.88,
    urgency_score=0.7,  # Moderate urgency due to stage 2 hypertension
    
    memory_handles=[
        memory_id,  # Encounter memory
        protocol_memory_id  # Screening protocol
    ],
    
    evidence_links=[
        hypertension_evidence.id,
        diabetes_evidence.id
    ],
    
    reasoning_trace=[
        "Analyzed BP readings: 155/95 mmHg indicates Stage 2 hypertension",
        "Reviewed fasting glucose: 128 mg/dL indicates impaired fasting glucose",
        "Consulted AHA guidelines for hypertension management",
        "Considered patient's Spanish language preference and cultural factors",
        "Applied diabetes prevention evidence for lifestyle recommendations",
        "Incorporated family involvement based on cultural considerations"
    ],
    
    tool_calls=[
        {
            "tool": "calculate_cardiovascular_risk",
            "parameters": {
                "age": patient.age_years,
                "systolic_bp": 155,
                "diastolic_bp": 95,
                "fasting_glucose": 128
            },
            "result": {
                "ten_year_risk": 0.15,
                "risk_category": "moderate",
                "recommendation": "medication_indicated"
            }
        },
        {
            "tool": "lookup_cultural_resources",
            "parameters": {
                "language": "spanish",
                "condition": "hypertension"
            },
            "result": {
                "materials_available": True,
                "counselor_available": True,
                "family_education_resources": True
            }
        }
    ],
    
    clinical_context={
        "encounter_id": "encounter-garcia-001",
        "provider_id": physician.id,
        "clinical_domains": ["cardiology", "endocrinology"],
        "intervention_types": ["medication", "lifestyle", "education"],
        "cultural_factors": ["spanish_language", "family_involvement"],
        "follow_up_timeline": "2_weeks_medication_3_months_comprehensive"
    },
    
    agent_metadata={
        "model": "gpt-4-turbo",
        "temperature": 0.2,
        "tokens_used": 2150,
        "processing_time_ms": 1200,
        "guidelines_consulted": ["AHA_2024", "ADA_2024"],
        "cultural_database_accessed": True
    },
    
    deadline=datetime.now() + timedelta(days=1),  # 24-hour response needed
    tags=["clinical_assessment", "hypertension", "diabetes_risk", "spanish_language"]
)

# Store the agent message
message_id = CreateResource(assessment_message, actor=physician)
print(f"✅ Created comprehensive assessment message")
print(f"   Confidence: {assessment_message.confidence_score}")
print(f"   Urgency: {assessment_message.urgency_level}")
print(f"   Memory handles: {len(assessment_message.memory_handles)}")
print(f"   Evidence links: {len(assessment_message.evidence_links)}")
print(f"   Tool calls: {len(assessment_message.tool_calls)}")
```

## 🏥 Example 5: Healthcare Encounter Management

Managing complete healthcare encounters with workflow tracking:

```python
from hacs_models import Encounter
from datetime import datetime

# Create a comprehensive encounter
encounter = Encounter(
    id="encounter-garcia-001",
    status="finished",
    class_fhir="ambulatory",
    subject=patient_id,
    period={
        "start": datetime(2024, 1, 20, 9, 0),
        "end": datetime(2024, 1, 20, 10, 15)
    },
    participants=[
        {
            "type": "PPRF",  # Primary performer
            "individual": physician.id,
            "name": physician.name,
            "role": "attending_physician"
        },
        {
            "type": "PART",  # Participant
            "individual": "ma-rodriguez-001",
            "name": "Maria Rodriguez, MA",
            "role": "medical_assistant"
        }
    ],
    reason_code=[
        {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "185349003",
                "display": "Encounter for check up"
            }]
        }
    ],
    diagnosis=[
        {
            "condition": "condition-hypertension-garcia",
            "rank": 1,
            "use": "billing"
        },
        {
            "condition": "condition-prediabetes-garcia",
            "rank": 2,
            "use": "billing"
        }
    ],
    location=[
        {
            "location": "location-exam-room-3",
            "status": "completed",
            "period": {
                "start": datetime(2024, 1, 20, 9, 0),
                "end": datetime(2024, 1, 20, 10, 15)
            }
        }
    ],
    agent_context={
        "session_id": "agent-session-garcia-001",
        "workflow_state": "completed",
        "ai_assistance_used": True,
        "decision_support_tools": [
            "cardiovascular_risk_calculator",
            "diabetes_risk_assessor",
            "cultural_resource_finder"
        ],
        "language_support": "spanish",
        "interpreter_used": False,  # Provider is bilingual
        "family_present": True,
        "care_plan_created": True
    }
)

encounter_id = CreateResource(encounter, actor=physician)
print(f"✅ Created encounter: {encounter.id}")
print(f"   Duration: {encounter.duration_minutes} minutes")
print(f"   Participants: {len(encounter.participants)}")
print(f"   Diagnoses: {len(encounter.diagnosis)}")
print(f"   AI assistance used: {encounter.agent_context['ai_assistance_used']}")
```

## 🔄 Example 6: FHIR Integration

Converting between HACS and FHIR formats:

```python
from hacs_fhir import to_fhir, from_fhir, validate_fhir_compliance

# Convert patient to FHIR
fhir_patient = to_fhir(patient)
print(f"✅ Converted patient to FHIR")
print(f"   FHIR Resource Type: {fhir_patient['resourceType']}")
print(f"   FHIR ID: {fhir_patient['id']}")

# Convert observation to FHIR
fhir_observation = to_fhir(bp_observation)
print(f"✅ Converted BP observation to FHIR")
print(f"   FHIR Resource Type: {fhir_observation['resourceType']}")
print(f"   Components: {len(fhir_observation.get('component', []))}")

# Convert back from FHIR
back_to_hacs_patient = from_fhir(fhir_patient)
back_to_hacs_observation = from_fhir(fhir_observation)

print(f"✅ Round-trip conversion successful")
print(f"   Patient ID match: {patient.id == back_to_hacs_patient.id}")
print(f"   Observation ID match: {bp_observation.id == back_to_hacs_observation.id}")

# Validate FHIR compliance
compliance_issues = validate_fhir_compliance(patient)
if not compliance_issues:
    print("✅ Patient is FHIR compliant")
else:
    print(f"⚠️ FHIR compliance issues: {compliance_issues}")
```

## 📊 Example 7: Performance Monitoring

Monitoring HACS performance and validating benchmarks:

```python
import time
from hacs_tools import CreateResource, ReadResource, UpdateResource, DeleteResource

def measure_performance():
    """Measure HACS performance across CRUD operations."""
    
    # Create test patient
    test_patient = Patient(
        id="perf-test-001",
        given=["Performance"],
        family="Test",
        gender="other",
        birth_date=date(2000, 1, 1)
    )
    
    # Measure CREATE performance
    start_time = time.time()
    patient_id = CreateResource(test_patient, actor=physician)
    create_time = (time.time() - start_time) * 1000
    
    # Measure READ performance
    start_time = time.time()
    retrieved_patient = ReadResource("Patient", patient_id, actor=physician)
    read_time = (time.time() - start_time) * 1000
    
    # Measure UPDATE performance
    test_patient.given = ["Updated", "Performance"]
    start_time = time.time()
    updated_patient = UpdateResource(test_patient, actor=physician)
    update_time = (time.time() - start_time) * 1000
    
    # Measure DELETE performance
    start_time = time.time()
    delete_success = DeleteResource("Patient", patient_id, actor=physician)
    delete_time = (time.time() - start_time) * 1000
    
    # Report results
    print(f"⚡ Performance Results:")
    print(f"   CREATE: {create_time:.2f}ms (target: <300ms)")
    print(f"   READ:   {read_time:.2f}ms (target: <300ms)")
    print(f"   UPDATE: {update_time:.2f}ms (target: <300ms)")
    print(f"   DELETE: {delete_time:.2f}ms (target: <300ms)")
    
    max_time = max(create_time, read_time, update_time, delete_time)
    status = "✅ PASSED" if max_time < 300 else "❌ FAILED"
    print(f"   Overall: {status}")
    
    return {
        "create_ms": create_time,
        "read_ms": read_time,
        "update_ms": update_time,
        "delete_ms": delete_time,
        "max_ms": max_time,
        "passed": max_time < 300
    }

# Run performance test
performance_results = measure_performance()
```

## 🎯 Summary

These examples demonstrate the core capabilities of HACS:

1. **Patient Management**: Comprehensive demographics with cultural considerations
2. **Clinical Observations**: FHIR-compliant measurements with AI flagging
3. **Memory & Evidence**: Clinical decision support with provenance tracking
4. **Agent Communication**: Sophisticated messages with reasoning and context
5. **Encounter Management**: Complete workflow tracking with AI integration
6. **FHIR Integration**: Seamless conversion between formats
7. **Performance Monitoring**: Sub-300ms operations with comprehensive validation

## 🚀 Next Steps

- Explore [Protocol Adapters](protocol-adapters.md) for framework integration
- Learn about [FHIR Mapping](fhir-mapping.md) for healthcare standards
- Review [Agent Integration](agent-integration.md) for AI workflows
- Check [Memory & Evidence](memory-evidence.md) for advanced features

Each example builds upon HACS's foundation to create sophisticated healthcare AI applications that maintain clinical safety, cultural sensitivity, and regulatory compliance. 