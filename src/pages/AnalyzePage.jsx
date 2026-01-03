import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Container,
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Grid
} from '@mui/material'
import { LocalHospital, ArrowForward } from '@mui/icons-material'
import PatientForm from '../components/PatientForm'
import DiagnosisResult from '../components/DiagnosisResult'
import AppointmentCard from '../components/AppointmentCard'
import DemoCard from '../components/DemoCard'
import { analyzeAndBook } from '../services/analysisService'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { DatePicker } from '@mui/x-date-pickers/DatePicker'
import dayjs from 'dayjs'

function AnalyzePage() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    patient_name: '',
    age: '',
    gender: '',
    symptoms: '',
    preferred_specialization: 'General Medicine',
    preferred_date: dayjs()
  })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const symptomsCharCount = formData.symptoms.length
  const isFormValid = formData.patient_name && formData.age && formData.gender && symptomsCharCount >= 50

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleDateChange = (newValue) => {
    setFormData(prev => ({
      ...prev,
      preferred_date: newValue
    }))
  }

  const handleSubmit = async () => {
    if (!isFormValid) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const payload = {
        patient_name: formData.patient_name,
        age: parseInt(formData.age),
        gender: formData.gender,
        symptoms: formData.symptoms,
        preferred_specialization: formData.preferred_specialization,
        preferred_date: formData.preferred_date.format('YYYY-MM-DD')
      }

      const response = await analyzeAndBook(payload)
      setResult(response)
    } catch (err) {
      setError('An error occurred while analyzing symptoms. Please try again.')
      console.error('Analysis error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDayjs}>
      <Box sx={{ minHeight: '100vh', bgcolor: '#f5f5f5', pb: 4 }}>
        {/* Header */}
        <Box sx={{ bgcolor: 'primary.main', color: 'white', py: 3, mb: 4 }}>
          <Container>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <LocalHospital sx={{ mr: 2, fontSize: 40 }} />
              <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
                Smart Healthcare Appointment & Diagnosis System
              </Typography>
            </Box>
          </Container>
        </Box>

        <Container maxWidth="lg">
          <Grid container spacing={3}>
            {/* Sidebar Placeholder */}
            <Grid item xs={12} md={3}>
              <Card sx={{ boxShadow: 2, height: 'fit-content', position: 'sticky', top: 20 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    Navigation
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Additional navigation items will appear here
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            {/* Main Content */}
            <Grid item xs={12} md={9}>
              <DemoCard />

              <Card sx={{ boxShadow: 3 }}>
                <CardContent sx={{ p: 4 }}>
                  {!result && (
                    <>
                      <PatientForm
                        formData={formData}
                        handleChange={handleChange}
                        symptomsCharCount={symptomsCharCount}
                      />

                      {/* Date Picker */}
                      <Box sx={{ mt: 3 }}>
                        <DatePicker
                          label="Preferred Appointment Date"
                          value={formData.preferred_date}
                          onChange={handleDateChange}
                          minDate={dayjs()}
                          slotProps={{
                            textField: {
                              fullWidth: true,
                              required: true
                            }
                          }}
                        />
                      </Box>

                      {/* Analyze Button */}
                      <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
                        <Button
                          variant="contained"
                          size="large"
                          onClick={handleSubmit}
                          disabled={!isFormValid || loading}
                          sx={{ px: 4, py: 1.5, fontSize: '1rem' }}
                        >
                          {loading ? (
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <CircularProgress size={20} color="inherit" />
                              Analyzing with AI...
                            </Box>
                          ) : (
                            'Analyze Symptoms & Book Appointment'
                          )}
                        </Button>
                      </Box>
                    </>
                  )}

                  {/* Error Alert */}
                  {error && (
                    <Alert severity="error" sx={{ mt: 3 }}>
                      {error}
                    </Alert>
                  )}

                  {/* Success UI */}
                  {result && (
                    <Box>
                      <Alert severity="success" sx={{ mb: 3 }}>
                        ✅ Analysis Complete! Appointment Booked Successfully
                      </Alert>

                      <DiagnosisResult diagnosisData={result} />
                      <AppointmentCard appointmentData={result.appointment} />

                      {/* Navigation Button */}
                      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
                        <Button
                          variant="outlined"
                          size="large"
                          endIcon={<ArrowForward />}
                          onClick={() => navigate('/queue')}
                          sx={{ px: 4, py: 1.5 }}
                        >
                          👉 View Full Appointment Queue
                        </Button>
                      </Box>
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </LocalizationProvider>
  )
}

export default AnalyzePage

