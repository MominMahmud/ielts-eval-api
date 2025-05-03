import { createTheme } from '@mui/material/styles';

// Using Google Fonts
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#3B82F6', // Bright blue
      light: '#60A5FA',
      dark: '#2563EB',
    },
    secondary: {
      main: '#10B981', // Emerald green
      light: '#34D399',
      dark: '#059669',
    },
    error: {
      main: '#EF4444',
      light: '#F87171',
      dark: '#DC2626',
    },
    warning: {
      main: '#F59E0B',
      light: '#FBBF24',
      dark: '#D97706',
    },
    info: {
      main: '#6366F1',
      light: '#818CF8',
      dark: '#4F46E5',
    },
    success: {
      main: '#10B981',
      light: '#34D399',
      dark: '#059669',
    },
    background: {
      default: '#111827', // Dark background
      paper: '#1F2937', // Slightly lighter dark for cards
    },
    text: {
      primary: '#F9FAFB',
      secondary: '#D1D5DB',
    },
  },
  typography: {
    fontFamily: '"Open Sans", sans-serif',
    h1: {
      fontFamily: '"Playfair Display", serif',
      fontWeight: 700,
      fontSize: '2.5rem',
      lineHeight: 1.2,
      color: '#F9FAFB',
    },
    h2: {
      fontFamily: '"Playfair Display", serif',
      fontWeight: 700,
      fontSize: '2rem',
      lineHeight: 1.3,
      color: '#F9FAFB',
    },
    h3: {
      fontFamily: '"Playfair Display", serif',
      fontWeight: 700,
      fontSize: '1.75rem',
      lineHeight: 1.3,
      color: '#F9FAFB',
    },
    h4: {
      fontFamily: '"Playfair Display", serif',
      fontWeight: 700,
      fontSize: '1.5rem',
      lineHeight: 1.4,
      color: '#F9FAFB',
    },
    h5: {
      fontFamily: '"Playfair Display", serif',
      fontWeight: 700,
      fontSize: '1.25rem',
      lineHeight: 1.4,
      color: '#F9FAFB',
    },
    h6: {
      fontFamily: '"Playfair Display", serif',
      fontWeight: 700,
      fontSize: '1rem',
      lineHeight: 1.4,
      color: '#F9FAFB',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
      color: '#D1D5DB',
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.6,
      color: '#D1D5DB',
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 0,
          padding: '10px 24px',
          fontSize: '0.9375rem',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 12px rgba(59,130,246,0.2)',
            transform: 'translateY(-1px)',
          },
          transition: 'all 0.2s ease-in-out',
        },
        containedPrimary: {
          background: 'linear-gradient(45deg, #3B82F6, #60A5FA)',
          '&:hover': {
            background: 'linear-gradient(45deg, #2563EB, #3B82F6)',
          },
        },
        containedSecondary: {
          background: 'linear-gradient(45deg, #10B981, #34D399)',
          '&:hover': {
            background: 'linear-gradient(45deg, #059669, #10B981)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          backgroundColor: '#1F2937',
          borderRadius: 8,
          boxShadow: '0 1px 3px 0 rgba(0,0,0,0.3)',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 12px 24px rgba(0,0,0,0.4)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 12,
            transition: 'all 0.2s ease-in-out',
            backgroundColor: '#374151',
            '&:hover': {
              boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
            },
            '&.Mui-focused': {
              boxShadow: '0 4px 12px rgba(59,130,246,0.2)',
            },
          },
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          height: 10,
          backgroundColor: 'rgba(59,130,246,0.2)',
        },
        bar: {
          borderRadius: 10,
          background: 'linear-gradient(45deg, #3B82F6, #60A5FA)',
        },
      },
    },
    MuiCircularProgress: {
      styleOverrides: {
        root: {
          transition: 'all 0.3s ease-in-out',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundColor: '#1F2937',
          borderRadius: 8,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#0F172A',
          backdropFilter: 'blur(12px)',
          boxShadow: 'none',
          borderBottom: '1px solid rgba(255,255,255,0.1)',
        },
      },
    },
  },
  shape: {
    borderRadius: 8,
  },
});

export default theme; 