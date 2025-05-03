import React from 'react';
import { Box, Typography, Link as MuiLink, IconButton } from '@mui/material';
import LinkedInIcon from '@mui/icons-material/LinkedIn';

const Footer = () => {
    return (
        <Box
            component="footer"
            sx={{
                backgroundColor: '#20689a', // Main blue
                color: '#ffffff',
                py: 3,
                mt: 8,
                borderTop: '1px solid #26b7fd', // Light blue border
                textAlign: 'center',
            }}
        >
            <Typography variant="body2" sx={{ color: '#ffffff', mb: 1 }}>
                &copy; {new Date().getFullYear()} Neurograde. All rights reserved.
            </Typography>
            <MuiLink
                href="https://www.linkedin.com/mominmahmud"
                target="_blank"
                rel="noopener noreferrer"
                sx={{ 
                    color: '#ffffff', 
                    display: 'inline-flex', 
                    alignItems: 'center', 
                    gap: 0.5,
                    '&:hover': {
                        color: '#26b7fd', // Light blue on hover
                    }
                }}
            >
                <IconButton sx={{ 
                    color: '#ffffff', 
                    p: 0.5,
                    '&:hover': {
                        color: '#26b7fd', // Light blue on hover
                    }
                }}>
                    <LinkedInIcon />
                </IconButton>
                Connect on LinkedIn
            </MuiLink>
        </Box>
    );
};

export default Footer; 