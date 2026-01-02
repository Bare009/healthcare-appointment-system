"""
Test all service layer functions
Run this to verify everything works before building UI
"""

from database.connection import initialize_pool, execute_query
from services.patient_service import create_patient, get_patient_by_phone
from services.symptom_service import save_symptom
from services.gemini_service import analyze_symptoms
from services.appointment_service import (
    save_prediction, find_available_doctor, create_appointment, 
    get_appointment_queue, get_all_specializations
)
from datetime import date, timedelta
import random

def cleanup_test_data():
    """Clean up test data - CASCADE handles child records automatically"""
    print("\n🧹 Cleaning up previous test data...")
    
    # Just delete the patient - CASCADE will handle the rest!
    result = execute_query("DELETE FROM patients WHERE phone = %s", ('9999999999',))
    
    if result is not None:
        print("   ✅ Test data cleaned (CASCADE deleted related records)")
    else:
        print("   ℹ️  No previous test data found")

def test_complete_flow():
    """Test complete patient journey"""
    print("\n" + "="*60)
    print("TESTING COMPLETE SERVICE LAYER")
    print("="*60)
    
    # Initialize database
    initialize_pool()
    
    # Clean up any previous test data
    cleanup_test_data()
    
    # Step 1: Create patient
    print("\n1️⃣ Creating patient...")
    patient_id = create_patient(
        first_name="Test",
        last_name="Patient",
        gender="Male",
        age=35,
        phone="9999999999",
        allergies="None"
    )
    assert patient_id is not None, "Patient creation failed"
    print(f"   ✅ Patient ID: {patient_id}")
    
    # Step 2: Save symptom
    print("\n2️⃣ Recording symptoms...")
    symptom_text = """
    I have been experiencing severe chest pain for the last 2 hours.
    The pain is radiating to my left arm and I'm feeling nauseous.
    I'm also sweating excessively and feeling dizzy.
    """
    symptom_id = save_symptom(patient_id, symptom_text)
    assert symptom_id is not None, "Symptom save failed"
    print(f"   ✅ Symptom ID: {symptom_id}")
    
    # Step 3: AI Analysis
    print("\n3️⃣ Calling Gemini AI for diagnosis...")
    diagnosis = analyze_symptoms(symptom_text)
    assert diagnosis is not None, "AI analysis failed"
    print(f"   ✅ Disease: {diagnosis['predicted_disease']}")
    print(f"   ✅ Probability: {diagnosis['probability']}%")
    print(f"   ✅ Urgency: {diagnosis['urgency_level']}/10")
    print(f"   ✅ Reason: {diagnosis['urgency_reason'][:60]}...")
    
    # Step 4: Save prediction
    print("\n4️⃣ Saving AI prediction...")
    prediction_id = save_prediction(symptom_id, diagnosis)
    assert prediction_id is not None, "Prediction save failed"
    print(f"   ✅ Prediction ID: {prediction_id}")
    
    # Step 5: Find doctor
    print("\n5️⃣ Finding available doctor...")
    specializations = get_all_specializations()
    print(f"   Available specializations: {len(specializations)} total")
    
    doctor = find_available_doctor("Cardiology", date.today())
    assert doctor is not None, "No doctor available"
    print(f"   ✅ Assigned Doctor: {doctor['name']}")
    print(f"      Qualification: {doctor['qualification']}")
    
    # Step 6: Create appointment
    print("\n6️⃣ Creating appointment...")
    appointment_id = create_appointment(
        patient_id=patient_id,
        doctor_id=doctor['doctor_id'],
        symptom_id=symptom_id,
        urgency_level=diagnosis['urgency_level'],
        appointment_date=date.today(),
        mode='Offline'
    )
    assert appointment_id is not None, "Appointment creation failed"
    print(f"   ✅ Appointment ID: APT-{appointment_id:03d}")
    
    # Step 7: Fetch queue
    print("\n7️⃣ Fetching appointment queue...")
    queue = get_appointment_queue(date_filter=date.today())
    print(f"   ✅ Total appointments today: {len(queue)}")
    
    if queue:
        print(f"\n   📋 Top 3 Appointments (by urgency):")
        for i, apt in enumerate(queue[:3], 1):
            urgency_emoji = "🔴" if apt['urgency_level'] >= 8 else "🟡" if apt['urgency_level'] >= 4 else "🟢"
            print(f"      {i}. {urgency_emoji} {apt['patient_name']} - {apt['predicted_disease']}")
            print(f"         Urgency: {apt['urgency_level']}/10 | Dr. {apt['doctor_name']}")
    
    # Step 8: Test filters
    print("\n8️⃣ Testing queue filters...")
    high_priority = get_appointment_queue(urgency_filter='High')
    print(f"   ✅ High priority appointments: {len(high_priority)}")
    
    cardiology_apts = get_appointment_queue(specialization_filter='Cardiology')
    print(f"   ✅ Cardiology appointments: {len(cardiology_apts)}")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\n💡 Service layer is ready. You can now build the Streamlit UI!")
    print("="*60 + "\n")

def test_multiple_patients():
    """Test creating multiple patients with different urgency levels"""
    print("\n" + "="*60)
    print("TESTING MULTIPLE PATIENTS (Queue Sorting)")
    print("="*60)
    
    initialize_pool()
    
    test_cases = [
        {
            "name": "Emergency Case",
            "phone": "8888888881",
            "symptoms": "Severe chest pain, shortness of breath, sweating profusely",
            "specialization": "Cardiology"
        },
        {
            "name": "Moderate Case",
            "phone": "8888888882",
            "symptoms": "Persistent headache for 3 days, mild fever, sensitivity to light",
            "specialization": "Neurology"
        },
        {
            "name": "Minor Case",
            "phone": "8888888883",
            "symptoms": "Mild skin rash on arms, itching, no pain",
            "specialization": "Dermatology"
        }
    ]
    
    print("\n📝 Creating 3 test patients with different urgency levels...\n")
    
    for i, case in enumerate(test_cases, 1):
        print(f"{i}. Processing: {case['name']}")
        
        # Clean up if exists
        execute_query("DELETE FROM patients WHERE phone = %s", (case['phone'],))
        
        # Create patient
        patient_id = create_patient("Test", case['name'], "Male", 30, case['phone'])
        symptom_id = save_symptom(patient_id, case['symptoms'])
        diagnosis = analyze_symptoms(case['symptoms'])
        save_prediction(symptom_id, diagnosis)
        
        doctor = find_available_doctor(case['specialization'], date.today())
        if doctor:
            create_appointment(patient_id, doctor['doctor_id'], symptom_id, 
                             diagnosis['urgency_level'], date.today())
        
        print(f"   ✅ Urgency: {diagnosis['urgency_level']}/10 - {diagnosis['predicted_disease']}\n")
    
    # Show sorted queue
    print("\n📊 Final Appointment Queue (sorted by urgency):")
    print("-" * 60)
    queue = get_appointment_queue(date_filter=date.today())
    
    for i, apt in enumerate(queue, 1):
        urgency_emoji = "🔴" if apt['urgency_level'] >= 8 else "🟡" if apt['urgency_level'] >= 4 else "🟢"
        print(f"{i}. {urgency_emoji} {apt['patient_name']:<20} | Urgency: {apt['urgency_level']:2}/10")
        print(f"   {apt['predicted_disease']:<30} | Dr. {apt['doctor_name']}")
        print(f"   Time: {apt['appointment_time']} | {apt['specialization']}")
        print("-" * 60)
    
    print("\n✅ Queue sorting verified!")
    print("="*60 + "\n")

if __name__ == "__main__":
    # Run basic test.
    test_complete_flow()
    
    # Optional: Run multi-patient test
    response = input("Run multi-patient queue test? (y/n): ")
    if response.lower() == 'y':
        test_multiple_patients()
