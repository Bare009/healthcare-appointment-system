import React, { useState } from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Collapse,
  IconButton,
  Chip
} from '@mui/material'
import { ExpandMore, ExpandLess, Info } from '@mui/icons-material'

function DemoCard() {
  const [expanded, setExpanded] = useState(false)

  return (
    <Card sx={{ mb: 3, boxShadow: 2, bgcolor: '#e3f2fd' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Info sx={{ mr: 1, color: 'info.main' }} />
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Demo Example
            </Typography>
          </Box>
          <IconButton
            onClick={() => setExpanded(!expanded)}
            size="small"
          >
            {expanded ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        </Box>

        <Collapse in={expanded}>
          <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #90caf9' }}>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Patient:</strong> XYZ (22, Male)
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Symptoms:</strong> Persistent cough, mild fever for 3 days
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>AI Diagnosis:</strong> Upper Respiratory Infection
              <Chip label="82%" size="small" color="success" sx={{ ml: 1 }} />
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Urgency:</strong> 6/10
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Doctor:</strong> Dr. Suresh Kumar (General Physician)
            </Typography>
            <Typography variant="body2">
              <strong>Time:</strong> Today, 2:00 PM
            </Typography>
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  )
}

export default DemoCard

