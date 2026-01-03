import React from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Divider
} from '@mui/material'
import { CalendarToday, Person, LocalHospital, Queue } from '@mui/icons-material'

function AppointmentCard({ appointmentData }) {
  const { appointment_id, doctor_name, specialization, datetime, queue_position } = appointmentData

  return (
    <Card sx={{ mt: 3, boxShadow: 3, bgcolor: '#f8f9fa' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <CalendarToday sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }}>
            Appointment Confirmation
          </Typography>
        </Box>

        <Box sx={{ mt: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="body2" color="text.secondary" sx={{ mr: 1 }}>
              Appointment ID:
            </Typography>
            <Typography variant="body1" sx={{ fontWeight: 600, color: 'primary.main' }}>
              {appointment_id}
            </Typography>
          </Box>

          <Divider sx={{ my: 2 }} />

          <Box sx={{ display: 'flex', alignItems: 'start', mb: 2 }}>
            <Person sx={{ mr: 1, color: 'text.secondary', mt: 0.5 }} />
            <Box>
              <Typography variant="body2" color="text.secondary">
                Doctor
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 600 }}>
                {doctor_name}
              </Typography>
            </Box>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'start', mb: 2 }}>
            <LocalHospital sx={{ mr: 1, color: 'text.secondary', mt: 0.5 }} />
            <Box>
              <Typography variant="body2" color="text.secondary">
                Specialization
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 600 }}>
                {specialization}
              </Typography>
            </Box>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'start', mb: 2 }}>
            <CalendarToday sx={{ mr: 1, color: 'text.secondary', mt: 0.5 }} />
            <Box>
              <Typography variant="body2" color="text.secondary">
                Date & Time
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 600 }}>
                {datetime}
              </Typography>
            </Box>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'start' }}>
            <Queue sx={{ mr: 1, color: 'text.secondary', mt: 0.5 }} />
            <Box>
              <Typography variant="body2" color="text.secondary">
                Queue Position
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 600 }}>
                #{queue_position}
              </Typography>
            </Box>
          </Box>
        </Box>
      </CardContent>
    </Card>
  )
}

export default AppointmentCard

