import React from 'react';
import { Box } from '@mui/material';
import Navbar from './Navbar';
import Footer from './Footer';

interface LayoutProps {
    children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
    return (
        <Box
            sx={{
                display: 'flex',
                flexDirection: 'column',
                minHeight: '100vh',
                width: '100%',
                position: 'relative',
                overflow: 'hidden',
            }}
        >
            <Navbar />
            <Box
                component="main"
                sx={{
                    flex: '1 0 auto',
                    width: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    position: 'relative',
                }}
            >
                {children}
            </Box>
            <Footer />
        </Box>
    );
};

export default Layout; 