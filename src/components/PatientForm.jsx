import React from 'react'
import {
  TextField,
  MenuItem,
  Box,
  Typography,
  TextareaAutosize,
  FormControl,
  InputLabel,
  Select
} from '@mui/material'

function PatientForm({ formData, handleChange, symptomsCharCount }) {
  return (
    <Box>
      {/* Patient Information Section */}
      <Typography variant="h6" gutterBottom sx={{ mt: 2, mb: 2, fontWeight: 600 }}>
        Patient Information
      </Typography>
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <TextField
          label="Patient Name"
          variant="outlined"
          fullWidth
          required
          name="patient_name"
          value={formData.patient_name}
          onChange={handleChange}
        />
        
        <TextField
          label="Age"
          type="number"
          variant="outlined"
          fullWidth
          required
          name="age"
          value={formData.age}
          onChange={handleChange}
          inputProps={{ min: 0, max: 120 }}
        />
        
        <FormControl fullWidth required>
          <InputLabel>Gender</InputLabel>
          <Select
            name="gender"
            value={formData.gender}
            onChange={handleChange}
            label="Gender"
          >
            <MenuItem value="Male">Male</MenuItem>
            <MenuItem value="Female">Female</MenuItem>
            <MenuItem value="Other">Other</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Medical Information Section */}
      <Typography variant="h6" gutterBottom sx={{ mt: 4, mb: 2, fontWeight: 600 }}>
        Medical Information
      </Typography>
      
      <Box>
        <TextareaAutosize
          minRows={6}
          placeholder="I've been experiencing severe headache for 2 days, along with high fever and body aches..."
          name="symptoms"
          value={formData.symptoms}
          onChange={handleChange}
          style={{
            width: '100%',
            padding: '12px',
            fontSize: '14px',
            fontFamily: 'inherit',
            border: '1px solid #ccc',
            borderRadius: '4px',
            resize: 'vertical'
          }}
        />
        <Typography
          variant="caption"
          sx={{
            mt: 0.5,
            color: symptomsCharCount >= 50 ? '#4caf50' : '#666',
            fontWeight: symptomsCharCount >= 50 ? 600 : 400
          }}
        >
          {symptomsCharCount} / 50 characters (minimum required)
        </Typography>
      </Box>

      {/* Appointment Preferences Section */}
      <Typography variant="h6" gutterBottom sx={{ mt: 4, mb: 2, fontWeight: 600 }}>
        Appointment Preferences
      </Typography>
      
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        <FormControl fullWidth required>
          <InputLabel>Preferred Specialization</InputLabel>
          <Select
            name="preferred_specialization"
            value={formData.preferred_specialization}
            onChange={handleChange}
            label="Preferred Specialization"
          >
            <MenuItem value="General Medicine">General Medicine</MenuItem>
            <MenuItem value="Cardiology">Cardiology</MenuItem>
            <MenuItem value="Neurology">Neurology</MenuItem>
            <MenuItem value="Orthopedics">Orthopedics</MenuItem>
            <MenuItem value="Dermatology">Dermatology</MenuItem>
            <MenuItem value="ENT">ENT</MenuItem>
          </Select>
        </FormControl>
      </Box>
    </Box>
  )
}

export default PatientForm

