import React, { useState, useEffect } from 'react';
import { 
    Box, 
    Typography, 
    Paper, 
    List, 
    ListItem, 
    ListItemText, 
    Button,
    CircularProgress
} from '@mui/material';
import { EssayWithEvaluation } from '../types/essay';
import { fetchEssays } from '../services/api';

const ITEMS_PER_PAGE = 10;

const EssayList: React.FC = () => {
    const [essays, setEssays] = useState<EssayWithEvaluation[]>([]);
    const [loading, setLoading] = useState(false);
    const [hasMore, setHasMore] = useState(true);
    const [page, setPage] = useState(1);

    const loadEssays = async (pageNum: number) => {
        try {
            setLoading(true);
            const skip = (pageNum - 1) * ITEMS_PER_PAGE;
            const data = await fetchEssays(skip, ITEMS_PER_PAGE);
            
            if (pageNum === 1) {
                setEssays(data);
            } else {
                setEssays(prev => [...prev, ...data]);
            }
            
            setHasMore(data.length === ITEMS_PER_PAGE);
        } catch (error) {
            console.error('Error loading essays:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadEssays(1);
    }, []);

    const handleLoadMore = () => {
        const nextPage = page + 1;
        setPage(nextPage);
        loadEssays(nextPage);
    };

    return (
        <Box sx={{ mt: 4 }}>
            <Typography variant="h4" gutterBottom>
                Your Essays
            </Typography>
            <List>
                {essays.map((essay) => (
                    <Paper 
                        key={essay.id} 
                        elevation={2} 
                        sx={{ mb: 2, p: 2 }}
                    >
                        <ListItem>
                            <ListItemText
                                primary={essay.prompt}
                                secondary={
                                    <Box>
                                        <Typography variant="body2" color="text.secondary">
                                            {essay.content.substring(0, 200)}...
                                        </Typography>
                                        {essay.evaluation && (
                                            <Box sx={{ mt: 1 }}>
                                                <Typography variant="subtitle2">
                                                    Score: {essay.evaluation.overall_score}
                                                </Typography>
                                                <Typography variant="body2">
                                                    {essay.evaluation.feedback}
                                                </Typography>
                                            </Box>
                                        )}
                                    </Box>
                                }
                            />
                        </ListItem>
                    </Paper>
                ))}
            </List>
            {hasMore && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                    <Button
                        variant="contained"
                        onClick={handleLoadMore}
                        disabled={loading}
                        sx={{ minWidth: 200 }}
                    >
                        {loading ? (
                            <CircularProgress size={24} color="inherit" />
                        ) : (
                            'Load More'
                        )}
                    </Button>
                </Box>
            )}
        </Box>
    );
};

export default EssayList; 