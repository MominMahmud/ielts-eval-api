import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Button,
  Chip,
  Divider,
  Alert,
  useTheme,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  TaskAlt as TaskAltIcon,
  Psychology as PsychologyIcon,
  Translate as TranslateIcon,
  AutoGraph as AutoGraphIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { toast } from 'react-toastify';
import { essayService } from '../services/api';
import type { Essay, Evaluation } from '../types/essay';

const ResultPage = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const theme = useTheme();
  const [loading, setLoading] = useState(true);
  const [essay, setEssay] = useState<Essay | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEssay = async () => {
      try {
        if (!id) {
          throw new Error('No essay ID provided');
        }
        const data = await essayService.getEssay(id);
        setEssay(data);
      } catch (err) {
        setError('Failed to load essay results');
        toast.error('Failed to load essay results');
      } finally {
        setLoading(false);
      }
    };

    fetchEssay();
  }, [id]);

  const fadeInUp = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            minHeight: '60vh',
          }}
        >
          <CircularProgress size={60} />
        </Box>
      </Container>
    );
  }

  if (error || !essay || !essay.evaluation) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ py: 4 }}>
          <Alert severity="error" sx={{ mb: 3 }}>
            {error || 'No evaluation data available'}
          </Alert>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/')}
            variant="outlined"
          >
            Back to Home
          </Button>
        </Box>
      </Container>
    );
  }

  const { evaluation } = essay;

  const ScoreCard = ({
    title,
    score,
    icon,
    color,
  }: {
    title: string;
    score: number;
    icon: React.ReactNode;
    color: 'primary' | 'secondary' | 'info' | 'success';
  }) => (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        p: 3,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '4px',
          background: `linear-gradient(90deg, ${theme.palette[color].main}, ${theme.palette[color].light})`,
        }}
      />
      {icon}
      <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
        {title}
      </Typography>
      <Box
        sx={{
          position: 'relative',
          display: 'inline-flex',
          mt: 1,
        }}
      >
        <CircularProgress
          variant="determinate"
          value={score * 10}
          size={80}
          thickness={4}
          sx={{ color: theme.palette[color].main }}
        />
        <Box
          sx={{
            top: 0,
            left: 0,
            bottom: 0,
            right: 0,
            position: 'absolute',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Typography
            variant="h4"
            component="div"
            color={color}
            sx={{ fontWeight: 700 }}
          >
            {score}
          </Typography>
        </Box>
      </Box>
    </Card>
  );

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: { xs: 4, md: 6 } }}>
        <motion.div
          initial="hidden"
          animate="visible"
          variants={fadeInUp}
          transition={{ duration: 0.5 }}
        >
          <Box sx={{ mb: 4 }}>
            <Button
              startIcon={<ArrowBackIcon />}
              onClick={() => navigate('/')}
              variant="outlined"
              sx={{ mb: 3 }}
            >
              Back to Home
            </Button>
            <Typography variant="h4" gutterBottom>
              Essay Evaluation Results
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
              Detailed analysis of your essay performance across all IELTS criteria
            </Typography>
          </Box>

          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={3}>
              <ScoreCard
                title="Task Achievement"
                score={evaluation.task_achievement}
                icon={<TaskAltIcon color="primary" sx={{ fontSize: 40 }} />}
                color="primary"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <ScoreCard
                title="Coherence & Cohesion"
                score={evaluation.coherence_cohesion}
                icon={<PsychologyIcon color="secondary" sx={{ fontSize: 40 }} />}
                color="secondary"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <ScoreCard
                title="Lexical Resource"
                score={evaluation.lexical_resource}
                icon={<TranslateIcon color="info" sx={{ fontSize: 40 }} />}
                color="info"
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <ScoreCard
                title="Grammar"
                score={evaluation.grammatical_range}
                icon={<AutoGraphIcon color="success" sx={{ fontSize: 40 }} />}
                color="success"
              />
            </Grid>
          </Grid>

          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Overall Score
              </Typography>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 2,
                  mb: 3,
                }}
              >
                <Chip
                  label={`Band ${evaluation.overall_score}`}
                  color="primary"
                  size="large"
                  sx={{
                    fontSize: '1.5rem',
                    height: '48px',
                    px: 2,
                  }}
                />
                <Typography variant="body1" color="text.secondary">
                  Based on IELTS band score criteria
                </Typography>
              </Box>
              <Divider sx={{ my: 3 }} />
              <Typography variant="h6" gutterBottom>
                Detailed Feedback
              </Typography>
              <Box sx={{ mt: 2 }}>
                {evaluation.feedback.split('\n').map((paragraph, index) => {
                  if (paragraph.startsWith('**')) {
                    const [heading, content] = paragraph.split(':**');
                    return (
                      <Box key={index} sx={{ mb: 2 }}>
                        <Typography
                          variant="subtitle1"
                          sx={{
                            color: 'primary.main',
                            fontWeight: 700,
                            mb: 1,
                          }}
                        >
                          {heading.replace('**', '')}
                        </Typography>
                        <Typography
                          variant="body1"
                          sx={{
                            whiteSpace: 'pre-line',
                            lineHeight: 1.8,
                            color: 'text.secondary',
                          }}
                        >
                          {content.trim()}
                        </Typography>
                      </Box>
                    );
                  }
                  return (
                    <Typography
                      key={index}
                      variant="body1"
                      sx={{
                        whiteSpace: 'pre-line',
                        lineHeight: 1.8,
                        color: 'text.secondary',
                        mb: 2,
                      }}
                    >
                      {paragraph}
                    </Typography>
                  );
                })}
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Original Essay
              </Typography>
              <Typography
                variant="body1"
                sx={{
                  whiteSpace: 'pre-line',
                  lineHeight: 1.8,
                  color: 'text.secondary',
                }}
              >
                {essay.content}
              </Typography>
            </CardContent>
          </Card>
        </motion.div>
      </Box>
    </Container>
  );
};

export default ResultPage; 