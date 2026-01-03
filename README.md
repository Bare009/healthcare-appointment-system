# Smart Healthcare Appointment & Diagnosis System

A production-ready React frontend for a Smart Healthcare Appointment & Diagnosis System with AI-powered symptom analysis.

## Features

- **Symptom Input & Analysis**: Patient information form with symptom description
- **AI Diagnosis**: Mock AI-powered diagnosis with confidence scores and alternative conditions
- **Appointment Booking**: Automatic appointment scheduling with queue management
- **Appointment Queue**: Real-time queue display with filtering and urgency-based sorting
- **Responsive Design**: Modern UI built with Material UI
- **Modular Architecture**: Clean component structure ready for backend integration

## Tech Stack

- React 18.3.1
- Vite 5.4.0
- React Router 6.26.0
- Material UI 5.16.0
- Axios 1.7.2 (for API calls)
- Day.js (for date handling)

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open your browser and navigate to `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The production build will be in the `dist` folder.

## Project Structure

```
smart_healthcare/
├── src/
│   ├── components/
│   │   ├── PatientForm.jsx          # Patient information form
│   │   ├── DiagnosisResult.jsx      # AI diagnosis display
│   │   ├── AppointmentCard.jsx      # Appointment confirmation
│   │   ├── DemoCard.jsx             # Demo example card
│   │   ├── Sidebar.jsx              # Navigation sidebar
│   │   ├── QueueFilters.jsx        # Queue filtering controls
│   │   └── QueueCard.jsx            # Queue item display
│   ├── pages/
│   │   ├── AnalyzePage.jsx          # Main analysis page
│   │   └── QueuePage.jsx            # Appointment queue page
│   ├── services/
│   │   ├── analysisService.js       # API service (placeholder)
│   │   └── queueService.js          # Queue API service (placeholder)
│   ├── App.jsx                      # Main app component with routing
│   ├── main.jsx                     # Entry point
│   └── index.css                    # Global styles
├── index.html
├── vite.config.js
├── package.json
├── requirements.txt                 # Python backend dependencies
└── README.md
```

## Pages

### Page 1: Symptom Analysis (`/analyze`)

- Patient information form (name, age, gender)
- Symptom description textarea (minimum 50 characters)
- Character counter with visual feedback
- Appointment preferences (specialization, date)
- Real-time form validation
- Loading states during analysis
- Success/error handling
- AI diagnosis display with confidence scores
- Appointment confirmation card

### Page 2: Appointment Queue (`/queue`)

- Real-time appointment queue display
- Urgency-based sorting (highest first)
- Filtering by urgency level and specialization
- Refresh functionality
- Current user highlighting (mock user: "XYZ")
- Responsive design with sidebar navigation
- Loading and error states
- Empty state handling

## Backend Integration

The frontend is designed to work with a FastAPI backend. To integrate:

1. Update `src/services/analysisService.js`:
   - Replace the placeholder function with actual API calls
   - Set the API base URL (use environment variables)

2. Update `src/services/queueService.js`:
   - Replace the placeholder function with actual API calls
   - Set the API base URL (use environment variables)

3. Expected API Endpoints:

   **POST** `/api/analyze-and-book`
   - Request body:
     ```json
     {
       "patient_name": "string",
       "age": number,
       "gender": "string",
       "symptoms": "string",
       "preferred_specialization": "string",
       "preferred_date": "YYYY-MM-DD"
     }
     ```
   - Response:
     ```json
     {
       "status": "success",
       "predicted_condition": "string",
       "confidence": number,
       "alternatives": [...],
       "urgency_score": number,
       "urgency_level": "LOW|MEDIUM|HIGH",
       "urgency_explanation": "string",
       "appointment": {
         "appointment_id": "string",
         "doctor_name": "string",
         "specialization": "string",
         "datetime": "string",
         "queue_position": number
       }
     }
     ```

   **GET** `/api/queue`
   - Query parameters: `urgency_level`, `specialization`
   - Response: Array of appointment objects

## Routes

- `/` or `/analyze` - Main symptom analysis page
- `/queue` - Appointment queue page

## Development Notes

- All API calls are currently mocked in service files
- The date picker uses Day.js for date handling
- Material UI theme can be customized in `App.jsx`
- Components are fully modular and reusable
- Mock current user is set to "XYZ" in QueuePage.jsx (replace with actual auth context)

## Backend Setup

For the FastAPI backend, install Python dependencies:

```bash
pip install -r requirements.txt
```

The `requirements.txt` includes:
- FastAPI and Uvicorn
- MySQL connectors
- SQLAlchemy
- Security libraries
- Data validation (Pydantic)

## License

ISC

