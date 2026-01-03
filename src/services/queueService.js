/**
 * Queue Service
 * Placeholder for FastAPI backend integration
 * 
 * TODO: Replace with actual API endpoint
 * const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
 */

/**
 * Fetches the appointment queue with optional filters
 * @param {Object} filters - Filter options
 * @param {string} filters.urgency_level - Filter by urgency level (All, HIGH, MEDIUM, LOW)
 * @param {string} filters.specialization - Filter by specialization (All, General Medicine, etc.)
 * @returns {Promise<Array>} Array of appointment objects
 */
export async function fetchQueue(filters = {}) {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500));

  // Placeholder response - Replace with actual FastAPI call:
  // const response = await axios.get(`${API_BASE_URL}/api/queue`, { params: filters });
  // return response.data;

  const mockQueue = [
    {
      appointment_id: "APT-101",
      patient: { name: "Rahul", age: 45, gender: "Male" },
      symptoms: "Chest pain and breathlessness",
      ai_diagnosis: {
        condition: "Possible Cardiac Event",
        confidence: 91,
        urgency_score: 9,
        urgency_level: "HIGH"
      },
      doctor: {
        name: "Dr. Anjali Rao",
        specialization: "Cardiologist"
      },
      appointment_time: "Today, 1:00 PM",
      queue_position: 1
    },
    {
      appointment_id: "APT-127",
      patient: { name: "XYZ", age: 22, gender: "Male" },
      symptoms: "Persistent cough, mild fever for 3 days",
      ai_diagnosis: {
        condition: "Upper Respiratory Infection",
        confidence: 82,
        urgency_score: 6,
        urgency_level: "MEDIUM"
      },
      doctor: {
        name: "Dr. Suresh Kumar",
        specialization: "General Physician"
      },
      appointment_time: "Today, 2:00 PM",
      queue_position: 8
    },
    {
      appointment_id: "APT-115",
      patient: { name: "Priya", age: 28, gender: "Female" },
      symptoms: "Severe migraine with vision disturbances",
      ai_diagnosis: {
        condition: "Migraine with Aura",
        confidence: 88,
        urgency_score: 7,
        urgency_level: "MEDIUM"
      },
      doctor: {
        name: "Dr. Vikram Singh",
        specialization: "Neurologist"
      },
      appointment_time: "Today, 3:30 PM",
      queue_position: 3
    },
    {
      appointment_id: "APT-098",
      patient: { name: "Amit", age: 35, gender: "Male" },
      symptoms: "Mild skin rash on arms",
      ai_diagnosis: {
        condition: "Contact Dermatitis",
        confidence: 75,
        urgency_score: 3,
        urgency_level: "LOW"
      },
      doctor: {
        name: "Dr. Meera Patel",
        specialization: "Dermatologist"
      },
      appointment_time: "Today, 4:00 PM",
      queue_position: 12
    },
    {
      appointment_id: "APT-134",
      patient: { name: "Sneha", age: 19, gender: "Female" },
      symptoms: "High fever (103°F), body aches, fatigue",
      ai_diagnosis: {
        condition: "Viral Fever",
        confidence: 85,
        urgency_score: 8,
        urgency_level: "HIGH"
      },
      doctor: {
        name: "Dr. Suresh Kumar",
        specialization: "General Physician"
      },
      appointment_time: "Today, 1:30 PM",
      queue_position: 2
    },
    {
      appointment_id: "APT-089",
      patient: { name: "Rajesh", age: 52, gender: "Male" },
      symptoms: "Knee pain after fall, difficulty walking",
      ai_diagnosis: {
        condition: "Possible Fracture",
        confidence: 79,
        urgency_score: 7,
        urgency_level: "MEDIUM"
      },
      doctor: {
        name: "Dr. Arjun Mehta",
        specialization: "Orthopedist"
      },
      appointment_time: "Today, 3:00 PM",
      queue_position: 5
    }
  ];

  // Apply filters (mock filtering)
  let filteredQueue = [...mockQueue];

  if (filters.urgency_level && filters.urgency_level !== 'All') {
    filteredQueue = filteredQueue.filter(
      item => item.ai_diagnosis.urgency_level === filters.urgency_level
    );
  }

  if (filters.specialization && filters.specialization !== 'All') {
    filteredQueue = filteredQueue.filter(
      item => item.doctor.specialization === filters.specialization
    );
  }

  // Sort by urgency_score (descending), then by appointment_time
  filteredQueue.sort((a, b) => {
    if (b.ai_diagnosis.urgency_score !== a.ai_diagnosis.urgency_score) {
      return b.ai_diagnosis.urgency_score - a.ai_diagnosis.urgency_score;
    }
    // If urgency scores are equal, sort by queue position
    return a.queue_position - b.queue_position;
  });

  return Promise.resolve(filteredQueue);
}

