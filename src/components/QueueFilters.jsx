import React from 'react'
import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Grid
} from '@mui/material'
import { Refresh } from '@mui/icons-material'

function QueueFilters({ filters, onFilterChange, onRefresh }) {
  const urgencyLevels = ['All', 'HIGH', 'MEDIUM', 'LOW']
  const specializations = [
    'All',
    'General Medicine',
    'Cardiology',
    'Neurology',
    'Orthopedics',
    'Dermatology',
    'ENT'
  ]

  return (
    <Box sx={{ mb: 3 }}>
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} sm={4}>
          <FormControl fullWidth>
            <InputLabel>Urgency Level</InputLabel>
            <Select
              value={filters.urgency_level || 'All'}
              onChange={(e) => onFilterChange('urgency_level', e.target.value)}
              label="Urgency Level"
            >
              {urgencyLevels.map((level) => (
                <MenuItem key={level} value={level}>
                  {level}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={4}>
          <FormControl fullWidth>
            <InputLabel>Specialization</InputLabel>
            <Select
              value={filters.specialization || 'All'}
              onChange={(e) => onFilterChange('specialization', e.target.value)}
              label="Specialization"
            >
              {specializations.map((spec) => (
                <MenuItem key={spec} value={spec}>
                  {spec}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={4}>
          <Button
            variant="contained"
            fullWidth
            startIcon={<Refresh />}
            onClick={onRefresh}
            sx={{ height: '56px' }}
          >
            Refresh Queue
          </Button>
        </Grid>
      </Grid>
    </Box>
  )
}

export default QueueFilters

