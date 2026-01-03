import React from 'react'
import {
  Card,
  CardContent,
  Box,
  Typography,
  Chip,
  Divider
} from '@mui/material'
import {
  Person,
  LocalHospital,
  CalendarToday,
  TrendingUp,
  AccessTime
} from '@mui/icons-material'

function QueueCard({ appointment, isCurrentUser = false }) {
  const { appointment_id, patient, symptoms, ai_diagnosis, doctor, appointment_time, queue_position } = appointment

  const getUrgencyColor = (level) => {
    switch (level) {
      case 'HIGH':
        return 'error'
      case 'MEDIUM':
        return 'warning'
      case 'LOW':
        return 'success'
      default:
        return 'default'
    }
  }

  // Truncate symptoms if too long
  const truncatedSymptoms = symptoms.length > 100 
    ? symptoms.substring(0, 100) + '...' 
    : symptoms

  return (
    <Card
      sx={{
        mb: 2,
        boxShadow: isCurrentUser ? 4 : 2,
        border: isCurrentUser ? '2px solid' : '1px solid',
        borderColor: isCurrentUser ? 'primary.main' : 'divider',
        bgcolor: isCurrentUser ? '#e3f2fd' : 'background.paper',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: 4
        }
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              label={`#${queue_position}`}
              color="primary"
              size="small"
              sx={{ fontWeight: 600 }}
            />
            {isCurrentUser && (
              <Chip
                label="Your Appointment"
                color="primary"
                size="small"
                variant="outlined"
              />
            )}
          </Box>
          <Chip
            label={ai_diagnosis.urgency_level}
            color={getUrgencyColor(ai_diagnosis.urgency_level)}
            size="small"
          />
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Patient Information */}
        <Box sx={{ display: 'flex', alignItems: 'start', mb: 2 }}>
          <Person sx={{ mr: 1, color: 'text.secondary', mt: 0.5 }} />
          <Box>
            <Typography variant="body2" color="text.secondary">
              Patient
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 600 }}>
              {patient.name} ({patient.age}, {patient.gender})
            </Typography>
          </Box>
        </Box>

        {/* Symptoms */}
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Symptoms
          </Typography>
          <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
            {truncatedSymptoms}
          </Typography>
        </Box>

        {/* AI Diagnosis */}
        <Box sx={{ mb: 2, p: 1.5, bgcolor: 'grey.50', borderRadius: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <TrendingUp sx={{ color: 'success.main', fontSize: 20 }} />
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
              AI Diagnosis
            </Typography>
          </Box>
          <Typography variant="body2" sx={{ fontWeight: 600, color: 'primary.main' }}>
            {ai_diagnosis.condition}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Confidence: {ai_diagnosis.confidence}% | Urgency: {ai_diagnosis.urgency_score}/10
          </Typography>
        </Box>

        <Divider sx={{ my: 2 }} />

        {/* Doctor Information */}
        <Box sx={{ display: 'flex', alignItems: 'start', mb: 2 }}>
          <LocalHospital sx={{ mr: 1, color: 'text.secondary', mt: 0.5 }} />
          <Box>
            <Typography variant="body2" color="text.secondary">
              Doctor
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 600 }}>
              {doctor.name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {doctor.specialization}
            </Typography>
          </Box>
        </Box>

        {/* Appointment Time */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <AccessTime sx={{ color: 'text.secondary', fontSize: 18 }} />
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            {appointment_time}
          </Typography>
        </Box>

        {/* Appointment ID */}
        <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #e0e0e0' }}>
          <Typography variant="caption" color="text.secondary">
            Appointment ID: <strong>{appointment_id}</strong>
          </Typography>
        </Box>
      </CardContent>
    </Card>
  )
}

export default QueueCard

