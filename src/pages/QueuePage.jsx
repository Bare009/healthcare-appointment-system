import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Container,
  Box,
  Typography,
  Button,
  Grid,
  CircularProgress,
  Alert,
  Card,
  CardContent
} from '@mui/material'
import { ArrowBack, Queue } from '@mui/icons-material'
import Sidebar from '../components/Sidebar'
import QueueFilters from '../components/QueueFilters'
import QueueCard from '../components/QueueCard'
import { fetchQueue } from '../services/queueService'

// Mock current user - Replace with actual auth context
const CURRENT_USER_NAME = 'XYZ'

function QueuePage() {
  const navigate = useNavigate()
  const [queueData, setQueueData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filters, setFilters] = useState({
    urgency_level: 'All',
    specialization: 'All'
  })

  const loadQueue = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchQueue(filters)
      setQueueData(data)
    } catch (err) {
      setError('Failed to load appointment queue. Please try again.')
      console.error('Queue loading error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadQueue()
  }, [filters])

  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }))
  }

  const handleRefresh = () => {
    loadQueue()
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f5f5f5', pb: 4 }}>
      {/* Header */}
      <Box sx={{ bgcolor: 'primary.main', color: 'white', py: 3, mb: 4 }}>
        <Container>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Queue sx={{ mr: 2, fontSize: 40 }} />
            <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
              Appointment Queue (Urgency-Based Priority)
            </Typography>
          </Box>
        </Container>
      </Box>

      <Container maxWidth="lg">
        <Grid container spacing={3}>
          {/* Sidebar */}
          <Grid item xs={12} md={3}>
            <Sidebar />
            <Button
              variant="outlined"
              fullWidth
              startIcon={<ArrowBack />}
              onClick={() => navigate('/analyze')}
              sx={{ mt: 2 }}
            >
              ⬅ Back to Symptom Analysis
            </Button>
          </Grid>

          {/* Main Content */}
          <Grid item xs={12} md={9}>
            <Card sx={{ boxShadow: 3 }}>
              <CardContent sx={{ p: 4 }}>
                {/* Filters */}
                <QueueFilters
                  filters={filters}
                  onFilterChange={handleFilterChange}
                  onRefresh={handleRefresh}
                />

                {/* Loading State */}
                {loading && (
                  <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                    <CircularProgress />
                  </Box>
                )}

                {/* Error State */}
                {error && (
                  <Alert severity="error" sx={{ mb: 3 }}>
                    {error}
                  </Alert>
                )}

                {/* Queue List */}
                {!loading && !error && (
                  <>
                    {queueData.length === 0 ? (
                      <Box sx={{ textAlign: 'center', py: 4 }}>
                        <Queue sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
                        <Typography variant="h6" color="text.secondary">
                          No appointments found
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                          Try adjusting your filters or check back later.
                        </Typography>
                      </Box>
                    ) : (
                      <Box
                        sx={{
                          maxHeight: '70vh',
                          overflowY: 'auto',
                          pr: 1,
                          '&::-webkit-scrollbar': {
                            width: '8px'
                          },
                          '&::-webkit-scrollbar-track': {
                            background: '#f1f1f1',
                            borderRadius: '4px'
                          },
                          '&::-webkit-scrollbar-thumb': {
                            background: '#888',
                            borderRadius: '4px',
                            '&:hover': {
                              background: '#555'
                            }
                          }
                        }}
                      >
                        {queueData.map((appointment) => {
                          const isCurrentUser = appointment.patient.name === CURRENT_USER_NAME
                          return (
                            <QueueCard
                              key={appointment.appointment_id}
                              appointment={appointment}
                              isCurrentUser={isCurrentUser}
                            />
                          )
                        })}
                      </Box>
                    )}
                  </>
                )}

                {/* Queue Summary */}
                {!loading && !error && queueData.length > 0 && (
                  <Box sx={{ mt: 3, pt: 2, borderTop: '1px solid #e0e0e0' }}>
                    <Typography variant="body2" color="text.secondary">
                      Showing {queueData.length} appointment{queueData.length !== 1 ? 's' : ''} 
                      {filters.urgency_level !== 'All' || filters.specialization !== 'All' 
                        ? ' (filtered)' 
                        : ''}
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  )
}

export default QueuePage

