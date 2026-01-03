import React from 'react'
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  List,
  ListItem,
  ListItemText
} from '@mui/material'
import { LocalHospital, TrendingUp } from '@mui/icons-material'

function DiagnosisResult({ diagnosisData }) {
  const { predicted_condition, confidence, alternatives, urgency_score, urgency_level, urgency_explanation } = diagnosisData

  const getUrgencyColor = (level) => {
    switch (level) {
      case 'LOW':
        return 'success'
      case 'MEDIUM':
        return 'warning'
      case 'HIGH':
        return 'error'
      default:
        return 'default'
    }
  }

  return (
    <Card sx={{ mt: 3, boxShadow: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <LocalHospital sx={{ mr: 1, color: 'primary.main' }} />
          <Typography variant="h5" component="h2" sx={{ fontWeight: 600 }}>
            AI Diagnosis
          </Typography>
        </Box>

        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" color="primary" sx={{ fontWeight: 600, mb: 1 }}>
            {predicted_condition}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TrendingUp sx={{ color: 'success.main' }} />
            <Typography variant="body1" color="text.secondary">
              Confidence: <strong>{confidence}%</strong>
            </Typography>
          </Box>
        </Box>

        {alternatives && alternatives.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
              Alternative Diagnoses:
            </Typography>
            <List dense>
              {alternatives.map((alt, index) => (
                <ListItem key={index} sx={{ pl: 0 }}>
                  <ListItemText
                    primary={alt.name}
                    secondary={`${alt.confidence}% confidence`}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}

        <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid #e0e0e0' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
              Urgency Level:
            </Typography>
            <Chip
              label={urgency_level}
              color={getUrgencyColor(urgency_level)}
              size="small"
            />
            <Typography variant="body2" color="text.secondary">
              Score: {urgency_score}/10
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary">
            {urgency_explanation}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  )
}

export default DiagnosisResult

