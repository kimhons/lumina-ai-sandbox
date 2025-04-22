import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { 
  Box, 
  Typography, 
  Paper, 
  Tabs, 
  Tab,
  IconButton,
  Tooltip,
  Divider,
  Button,
  TextField,
  Chip,
  CircularProgress,
  Avatar,
  Badge,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemAvatar,
  Card,
  CardContent,
  CardHeader,
  CardActions,
  Grid,
  Menu,
  MenuItem,
  Collapse,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { 
  Refresh as RefreshIcon,
  FilterList as FilterIcon,
  MoreVert as MoreVertIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as SuccessIcon,
  Pause as PauseIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Person as PersonIcon,
  SmartToy as RobotIcon,
  Code as CodeIcon,
  Search as SearchIcon,
  Storage as DatabaseIcon,
  CloudDownload as DownloadIcon,
  CloudUpload as UploadIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Bookmark as BookmarkIcon,
  BookmarkBorder as BookmarkBorderIcon,
  Timeline as TimelineIcon,
  ViewList as ListViewIcon,
  ViewModule as GridViewIcon,
  Notifications as NotificationsIcon,
  NotificationsOff as NotificationsOffIcon,
  Settings as SettingsIcon,
  FilterAlt as FilterAltIcon,
  Sort as SortIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
  Bolt as BoltIcon,
  Memory as MemoryIcon,
  Psychology as PsychologyIcon,
  Lightbulb as LightbulbIcon,
  Insights as InsightsIcon,
  Biotech as BiotechIcon,
  Science as ScienceIcon,
  Construction as ToolsIcon,
  Api as ApiIcon,
  Terminal as TerminalIcon,
  DataObject as DataObjectIcon,
  Dns as ServerIcon,
  Hub as HubIcon
} from '@mui/icons-material';

/**
 * Enhanced Agent Activity Panel Component
 * 
 * A comprehensive panel for visualizing and monitoring agent activities
 * with real-time updates, filtering, and detailed information.
 */
const EnhancedAgentActivityPanel = ({
  agents = [],
  activities = [],
  onRefresh,
  onFilterChange,
  onAgentSelect,
  onActivitySelect,
  onPauseAgent,
  onResumeAgent,
  onStopAgent,
  onBookmarkActivity,
  isLoading = false
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [viewMode, setViewMode] = useState('timeline');
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [selectedActivity, setSelectedActivity] = useState(null);
  const [expandedActivities, setExpandedActivities] = useState({});
  const [filters, setFilters] = useState({
    types: [],
    status: [],
    timeRange: 'all',
    agents: []
  });
  const [sortConfig, setSortConfig] = useState({
    key: 'timestamp',
    direction: 'desc'
  });
  const [anchorEl, setAnchorEl] = useState(null);
  const [filterMenuAnchor, setFilterMenuAnchor] = useState(null);
  const [sortMenuAnchor, setSortMenuAnchor] = useState(null);
  const timelineRef = useRef(null);
  
  // Auto-scroll to bottom of timeline on new activities
  useEffect(() => {
    if (viewMode === 'timeline' && timelineRef.current && activities.length > 0) {
      timelineRef.current.scrollTop = timelineRef.current.scrollHeight;
    }
  }, [activities, viewMode]);
  
  // Handle agent selection
  const handleAgentSelect = (agent) => {
    setSelectedAgent(agent);
    if (onAgentSelect) {
      onAgentSelect(agent);
    }
  };
  
  // Handle activity selection
  const handleActivitySelect = (activity) => {
    setSelectedActivity(activity);
    if (onActivitySelect) {
      onActivitySelect(activity);
    }
  };
  
  // Toggle activity expansion
  const toggleActivityExpansion = (activityId) => {
    setExpandedActivities(prev => ({
      ...prev,
      [activityId]: !prev[activityId]
    }));
  };
  
  // Handle filter changes
  const handleFilterChange = (filterType, value) => {
    const newFilters = {
      ...filters,
      [filterType]: value
    };
    setFilters(newFilters);
    if (onFilterChange) {
      onFilterChange(newFilters);
    }
  };
  
  // Handle sort changes
  const handleSortChange = (key) => {
    const direction = sortConfig.key === key && sortConfig.direction === 'asc' ? 'desc' : 'asc';
    const newSortConfig = { key, direction };
    setSortConfig(newSortConfig);
    setSortMenuAnchor(null);
  };
  
  // Filter activities based on current filters
  const filteredActivities = activities.filter(activity => {
    // Filter by type
    if (filters.types.length > 0 && !filters.types.includes(activity.type)) {
      return false;
    }
    
    // Filter by status
    if (filters.status.length > 0 && !filters.status.includes(activity.status)) {
      return false;
    }
    
    // Filter by agent
    if (filters.agents.length > 0 && !filters.agents.includes(activity.agentId)) {
      return false;
    }
    
    // Filter by time range
    if (filters.timeRange !== 'all') {
      const now = new Date();
      const activityTime = new Date(activity.timestamp);
      const diffInHours = (now - activityTime) / (1000 * 60 * 60);
      
      if (filters.timeRange === 'last-hour' && diffInHours > 1) {
        return false;
      } else if (filters.timeRange === 'today' && diffInHours > 24) {
        return false;
      } else if (filters.timeRange === 'week' && diffInHours > 168) {
        return false;
      }
    }
    
    return true;
  });
  
  // Sort filtered activities
  const sortedActivities = [...filteredActivities].sort((a, b) => {
    if (sortConfig.key === 'timestamp') {
      return sortConfig.direction === 'asc' 
        ? new Date(a.timestamp) - new Date(b.timestamp)
        : new Date(b.timestamp) - new Date(a.timestamp);
    } else if (sortConfig.key === 'priority') {
      return sortConfig.direction === 'asc'
        ? a.priority - b.priority
        : b.priority - a.priority;
    } else if (sortConfig.key === 'duration') {
      return sortConfig.direction === 'asc'
        ? a.duration - b.duration
        : b.duration - a.duration;
    }
    return 0;
  });
  
  // Get activity icon based on type
  const getActivityIcon = (type, status) => {
    // Status-based icons take precedence
    if (status === 'error') {
      return <ErrorIcon color="error" />;
    } else if (status === 'warning') {
      return <WarningIcon color="warning" />;
    } else if (status === 'success') {
      return <SuccessIcon color="success" />;
    }
    
    // Type-based icons
    switch (type) {
      case 'thinking':
        return <PsychologyIcon color="primary" />;
      case 'memory':
        return <MemoryIcon color="primary" />;
      case 'tool_use':
        return <ToolsIcon color="primary" />;
      case 'api_call':
        return <ApiIcon color="primary" />;
      case 'search':
        return <SearchIcon color="primary" />;
      case 'code_execution':
        return <CodeIcon color="primary" />;
      case 'data_processing':
        return <DataObjectIcon color="primary" />;
      case 'message':
        return <NotificationsIcon color="primary" />;
      case 'insight':
        return <LightbulbIcon color="primary" />;
      case 'experiment':
        return <ScienceIcon color="primary" />;
      case 'analysis':
        return <InsightsIcon color="primary" />;
      default:
        return <InfoIcon color="primary" />;
    }
  };
  
  // Get activity color based on type and status
  const getActivityColor = (type, status) => {
    if (status === 'error') {
      return theme.palette.error.main;
    } else if (status === 'warning') {
      return theme.palette.warning.main;
    } else if (status === 'success') {
      return theme.palette.success.main;
    }
    
    switch (type) {
      case 'thinking':
        return theme.palette.primary.main;
      case 'memory':
        return theme.palette.secondary.main;
      case 'tool_use':
        return theme.palette.info.main;
      case 'api_call':
        return theme.palette.info.dark;
      case 'search':
        return theme.palette.primary.light;
      case 'code_execution':
        return theme.palette.secondary.dark;
      case 'data_processing':
        return theme.palette.info.light;
      case 'message':
        return theme.palette.success.light;
      case 'insight':
        return theme.palette.warning.light;
      default:
        return theme.palette.grey[500];
    }
  };
  
  // Format timestamp
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };
  
  // Format duration
  const formatDuration = (durationMs) => {
    if (durationMs < 1000) {
      return `${durationMs}ms`;
    } else if (durationMs < 60000) {
      return `${(durationMs / 1000).toFixed(2)}s`;
    } else {
      const minutes = Math.floor(durationMs / 60000);
      const seconds = ((durationMs % 60000) / 1000).toFixed(0);
      return `${minutes}m ${seconds}s`;
    }
  };
  
  // Render agent list
  const renderAgentList = () => {
    return (
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle1" gutterBottom>
          Agents
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {agents.map(agent => (
            <Chip
              key={agent.id}
              avatar={
                <Avatar 
                  sx={{ 
                    bgcolor: agent.isActive ? 'success.main' : 'grey.500'
                  }}
                >
                  {agent.type === 'human' ? <PersonIcon /> : <RobotIcon />}
                </Avatar>
              }
              label={agent.name}
              onClick={() => handleAgentSelect(agent)}
              variant={selectedAgent?.id === agent.id ? 'filled' : 'outlined'}
              color={selectedAgent?.id === agent.id ? 'primary' : 'default'}
              sx={{ m: 0.5 }}
            />
          ))}
        </Box>
      </Box>
    );
  };
  
  // Render timeline view
  const renderTimelineView = () => {
    return (
      <Box 
        ref={timelineRef}
        sx={{ 
          height: '100%', 
          overflowY: 'auto',
          px: 1
        }}
      >
        <Timeline position="right">
          {sortedActivities.map(activity => (
            <TimelineItem key={activity.id}>
              <TimelineOppositeContent sx={{ flex: 0.2, minWidth: 80 }}>
                <Typography variant="caption" color="text.secondary">
                  {formatTimestamp(activity.timestamp)}
                </Typography>
              </TimelineOppositeContent>
              
              <TimelineSeparator>
                <TimelineDot sx={{ bgcolor: getActivityColor(activity.type, activity.status) }}>
                  {getActivityIcon(activity.type, activity.status)}
                </TimelineDot>
                <TimelineConnector />
              </TimelineSeparator>
              
              <TimelineContent>
                <Card 
                  sx={{ 
                    mb: 2,
                    border: activity.isBookmarked ? `1px solid ${theme.palette.warning.main}` : 'none'
                  }}
                  onClick={() => handleActivitySelect(activity)}
                >
                  <CardHeader
                    avatar={
                      <Avatar sx={{ bgcolor: getActivityColor(activity.type, activity.status) }}>
                        {getActivityIcon(activity.type, activity.status)}
                      </Avatar>
                    }
                    title={activity.title}
                    subheader={`${activity.agentName} • ${activity.type} • ${formatDuration(activity.duration)}`}
                    action={
                      <Box>
                        <IconButton 
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            if (onBookmarkActivity) {
                              onBookmarkActivity(activity.id, !activity.isBookmarked);
                            }
                          }}
                        >
                          {activity.isBookmarked ? 
                            <BookmarkIcon color="warning" /> : 
                            <BookmarkBorderIcon />
                          }
                        </IconButton>
                        <IconButton 
                          size="small"
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleActivityExpansion(activity.id);
                          }}
                        >
                          {expandedActivities[activity.id] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </IconButton>
                      </Box>
                    }
                  />
                  
                  <Collapse in={expandedActivities[activity.id] || false}>
                    <CardContent>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        {activity.description}
                      </Typography>
                      
                      {activity.details && (
                        <Box sx={{ mt: 1, p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                          <Typography variant="caption" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                            {typeof activity.details === 'object' 
                              ? JSON.stringify(activity.details, null, 2)
                              : activity.details
                            }
                          </Typography>
                        </Box>
                      )}
                      
                      {activity.result && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Result
                          </Typography>
                          <Box sx={{ p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                            <Typography variant="caption" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                              {typeof activity.result === 'object' 
                                ? JSON.stringify(activity.result, null, 2)
                                : activity.result
                              }
                            </Typography>
                          </Box>
                        </Box>
                      )}
                      
                      {activity.metrics && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Metrics
                          </Typography>
                          <Grid container spacing={1}>
                            {Object.entries(activity.metrics).map(([key, value]) => (
                              <Grid item xs={6} sm={4} key={key}>
                                <Box sx={{ p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                                  <Typography variant="caption" color="text.secondary">
                                    {key}
                                  </Typography>
                                  <Typography variant="body2">
                                    {value}
                                  </Typography>
                                </Box>
                              </Grid>
                            ))}
                          </Grid>
                        </Box>
                      )}
                    </CardContent>
                    
                    <CardActions sx={{ justifyContent: 'flex-end' }}>
                      {activity.actions && activity.actions.map(action => (
                        <Button 
                          key={action.label} 
                          size="small" 
                          startIcon={action.icon}
                          onClick={(e) => {
                            e.stopPropagation();
                            if (action.handler) {
                              action.handler(activity);
                            }
                          }}
                        >
                          {action.label}
                        </Button>
                      ))}
                    </CardActions>
                  </Collapse>
                </Card>
              </TimelineContent>
            </TimelineItem>
          ))}
        </Timeline>
      </Box>
    );
  };
  
  // Render list view
  const renderListView = () => {
    return (
      <List sx={{ height: '100%', overflowY: 'auto' }}>
        {sortedActivities.map(activity => (
          <ListItem 
            key={activity.id}
            alignItems="flex-start"
            button
            onClick={() => handleActivitySelect(activity)}
            secondaryAction={
              <Box>
                <IconButton 
                  edge="end" 
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (onBookmarkActivity) {
                      onBookmarkActivity(activity.id, !activity.isBookmarked);
                    }
                  }}
                >
                  {activity.isBookmarked ? 
                    <BookmarkIcon color="warning" /> : 
                    <BookmarkBorderIcon />
                  }
                </IconButton>
                <IconButton 
                  edge="end" 
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleActivityExpansion(activity.id);
                  }}
                >
                  {expandedActivities[activity.id] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                </IconButton>
              </Box>
            }
          >
            <ListItemAvatar>
              <Avatar sx={{ bgcolor: getActivityColor(activity.type, activity.status) }}>
                {getActivityIcon(activity.type, activity.status)}
              </Avatar>
            </ListItemAvatar>
            <ListItemText
              primary={
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Typography variant="subtitle2">
                    {activity.title}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {formatTimestamp(activity.timestamp)}
                  </Typography>
                </Box>
              }
              secondary={
                <React.Fragment>
                  <Typography variant="body2" color="text.secondary">
                    {activity.agentName} • {activity.type} • {formatDuration(activity.duration)}
                  </Typography>
                  
                  <Collapse in={expandedActivities[activity.id] || false}>
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="body2" color="text.secondary" paragraph>
                        {activity.description}
                      </Typography>
                      
                      {activity.details && (
                        <Box sx={{ mt: 1, p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                          <Typography variant="caption" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                            {typeof activity.details === 'object' 
                              ? JSON.stringify(activity.details, null, 2)
                              : activity.details
                            }
                          </Typography>
                        </Box>
                      )}
                      
                      {activity.result && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Result
                          </Typography>
                          <Box sx={{ p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                            <Typography variant="caption" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                              {typeof activity.result === 'object' 
                                ? JSON.stringify(activity.result, null, 2)
                                : activity.result
                              }
                            </Typography>
                          </Box>
                        </Box>
                      )}
                      
                      {activity.metrics && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="subtitle2" gutterBottom>
                            Metrics
                          </Typography>
                          <Grid container spacing={1}>
                            {Object.entries(activity.metrics).map(([key, value]) => (
                              <Grid item xs={6} sm={4} key={key}>
                                <Box sx={{ p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                                  <Typography variant="caption" color="text.secondary">
                                    {key}
                                  </Typography>
                                  <Typography variant="body2">
                                    {value}
                                  </Typography>
                                </Box>
                              </Grid>
                            ))}
                          </Grid>
                        </Box>
                      )}
                      
                      {activity.actions && (
                        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                          {activity.actions.map(action => (
                            <Button 
                              key={action.label} 
                              size="small" 
                              startIcon={action.icon}
                              onClick={(e) => {
                                e.stopPropagation();
                                if (action.handler) {
                                  action.handler(activity);
                                }
                              }}
                              sx={{ ml: 1 }}
                            >
                              {action.label}
                            </Button>
                          ))}
                        </Box>
                      )}
                    </Box>
                  </Collapse>
                </React.Fragment>
              }
            />
          </ListItem>
        ))}
      </List>
    );
  };
  
  // Render grid view
  const renderGridView = () => {
    return (
      <Box sx={{ height: '100%', overflowY: 'auto', p: 2 }}>
        <Grid container spacing={2}>
          {sortedActivities.map(activity => (
            <Grid item xs={12} sm={6} md={4} key={activity.id}>
              <Card 
                sx={{ 
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  border: activity.isBookmarked ? `1px solid ${theme.palette.warning.main}` : 'none'
                }}
                onClick={() => handleActivitySelect(activity)}
              >
                <CardHeader
                  avatar={
                    <Avatar sx={{ bgcolor: getActivityColor(activity.type, activity.status) }}>
                      {getActivityIcon(activity.type, activity.status)}
                    </Avatar>
                  }
                  title={activity.title}
                  subheader={`${formatTimestamp(activity.timestamp)}`}
                  action={
                    <Box>
                      <IconButton 
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          if (onBookmarkActivity) {
                            onBookmarkActivity(activity.id, !activity.isBookmarked);
                          }
                        }}
                      >
                        {activity.isBookmarked ? 
                          <BookmarkIcon color="warning" /> : 
                          <BookmarkBorderIcon />
                        }
                      </IconButton>
                      <IconButton 
                        size="small"
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleActivityExpansion(activity.id);
                        }}
                      >
                        {expandedActivities[activity.id] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                      </IconButton>
                    </Box>
                  }
                />
                
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {activity.agentName} • {activity.type} • {formatDuration(activity.duration)}
                  </Typography>
                  
                  <Typography variant="body2" noWrap={!expandedActivities[activity.id]}>
                    {activity.description}
                  </Typography>
                  
                  <Collapse in={expandedActivities[activity.id] || false}>
                    {activity.details && (
                      <Box sx={{ mt: 2, p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                        <Typography variant="caption" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                          {typeof activity.details === 'object' 
                            ? JSON.stringify(activity.details, null, 2)
                            : activity.details
                          }
                        </Typography>
                      </Box>
                    )}
                    
                    {activity.result && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          Result
                        </Typography>
                        <Box sx={{ p: 1, bgcolor: 'background.default', borderRadius: 1 }}>
                          <Typography variant="caption" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                            {typeof activity.result === 'object' 
                              ? JSON.stringify(activity.result, null, 2)
                              : activity.result
                            }
                          </Typography>
                        </Box>
                      </Box>
                    )}
                  </Collapse>
                </CardContent>
                
                <CardActions>
                  {activity.actions && activity.actions.map(action => (
                    <Button 
                      key={action.label} 
                      size="small" 
                      startIcon={action.icon}
                      onClick={(e) => {
                        e.stopPropagation();
                        if (action.handler) {
                          action.handler(activity);
                        }
                      }}
                    >
                      {action.label}
                    </Button>
                  ))}
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    );
  };
  
  // Render filter menu
  const renderFilterMenu = () => {
    const activityTypes = [...new Set(activities.map(a => a.type))];
    const activityStatuses = [...new Set(activities.map(a => a.status))];
    
    return (
      <Menu
        anchorEl={filterMenuAnchor}
        open={Boolean(filterMenuAnchor)}
        onClose={() => setFilterMenuAnchor(null)}
      >
        <Box sx={{ px: 2, py: 1 }}>
          <Typography variant="subtitle2" gutterBottom>
            Activity Types
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
            {activityTypes.map(type => (
              <Chip
                key={type}
                label={type}
                size="small"
                onClick={() => {
                  const newTypes = filters.types.includes(type)
                    ? filters.types.filter(t => t !== type)
                    : [...filters.types, type];
                  handleFilterChange('types', newTypes);
                }}
                color={filters.types.includes(type) ? 'primary' : 'default'}
                variant={filters.types.includes(type) ? 'filled' : 'outlined'}
              />
            ))}
          </Box>
          
          <Typography variant="subtitle2" gutterBottom>
            Status
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
            {activityStatuses.map(status => (
              <Chip
                key={status}
                label={status}
                size="small"
                onClick={() => {
                  const newStatuses = filters.status.includes(status)
                    ? filters.status.filter(s => s !== status)
                    : [...filters.status, status];
                  handleFilterChange('status', newStatuses);
                }}
                color={filters.status.includes(status) ? 'primary' : 'default'}
                variant={filters.status.includes(status) ? 'filled' : 'outlined'}
              />
            ))}
          </Box>
          
          <Typography variant="subtitle2" gutterBottom>
            Time Range
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
            {[
              { value: 'all', label: 'All Time' },
              { value: 'last-hour', label: 'Last Hour' },
              { value: 'today', label: 'Today' },
              { value: 'week', label: 'This Week' }
            ].map(option => (
              <Chip
                key={option.value}
                label={option.label}
                size="small"
                onClick={() => handleFilterChange('timeRange', option.value)}
                color={filters.timeRange === option.value ? 'primary' : 'default'}
                variant={filters.timeRange === option.value ? 'filled' : 'outlined'}
              />
            ))}
          </Box>
          
          <Typography variant="subtitle2" gutterBottom>
            Agents
          </Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
            {agents.map(agent => (
              <Chip
                key={agent.id}
                label={agent.name}
                size="small"
                onClick={() => {
                  const newAgents = filters.agents.includes(agent.id)
                    ? filters.agents.filter(a => a !== agent.id)
                    : [...filters.agents, agent.id];
                  handleFilterChange('agents', newAgents);
                }}
                color={filters.agents.includes(agent.id) ? 'primary' : 'default'}
                variant={filters.agents.includes(agent.id) ? 'filled' : 'outlined'}
              />
            ))}
          </Box>
          
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 1 }}>
            <Button 
              size="small" 
              onClick={() => {
                handleFilterChange('types', []);
                handleFilterChange('status', []);
                handleFilterChange('timeRange', 'all');
                handleFilterChange('agents', []);
              }}
            >
              Clear All
            </Button>
            <Button 
              size="small" 
              variant="contained" 
              onClick={() => setFilterMenuAnchor(null)}
              sx={{ ml: 1 }}
            >
              Apply
            </Button>
          </Box>
        </Box>
      </Menu>
    );
  };
  
  // Render sort menu
  const renderSortMenu = () => {
    return (
      <Menu
        anchorEl={sortMenuAnchor}
        open={Boolean(sortMenuAnchor)}
        onClose={() => setSortMenuAnchor(null)}
      >
        <MenuItem 
          onClick={() => handleSortChange('timestamp')}
          selected={sortConfig.key === 'timestamp'}
        >
          <ListItemIcon>
            {sortConfig.key === 'timestamp' && sortConfig.direction === 'asc' ? 
              <ArrowUpwardIcon fontSize="small" /> : 
              <ArrowDownwardIcon fontSize="small" />
            }
          </ListItemIcon>
          <ListItemText>Timestamp</ListItemText>
        </MenuItem>
        <MenuItem 
          onClick={() => handleSortChange('priority')}
          selected={sortConfig.key === 'priority'}
        >
          <ListItemIcon>
            {sortConfig.key === 'priority' && sortConfig.direction === 'asc' ? 
              <ArrowUpwardIcon fontSize="small" /> : 
              <ArrowDownwardIcon fontSize="small" />
            }
          </ListItemIcon>
          <ListItemText>Priority</ListItemText>
        </MenuItem>
        <MenuItem 
          onClick={() => handleSortChange('duration')}
          selected={sortConfig.key === 'duration'}
        >
          <ListItemIcon>
            {sortConfig.key === 'duration' && sortConfig.direction === 'asc' ? 
              <ArrowUpwardIcon fontSize="small" /> : 
              <ArrowDownwardIcon fontSize="small" />
            }
          </ListItemIcon>
          <ListItemText>Duration</ListItemText>
        </MenuItem>
      </Menu>
    );
  };
  
  // Render agent control menu
  const renderAgentControlMenu = () => {
    return (
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => setAnchorEl(null)}
      >
        <MenuItem 
          onClick={() => {
            if (selectedAgent && onPauseAgent) {
              onPauseAgent(selectedAgent.id);
            }
            setAnchorEl(null);
          }}
          disabled={!selectedAgent || !selectedAgent.isActive}
        >
          <ListItemIcon>
            <PauseIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Pause Agent</ListItemText>
        </MenuItem>
        <MenuItem 
          onClick={() => {
            if (selectedAgent && onResumeAgent) {
              onResumeAgent(selectedAgent.id);
            }
            setAnchorEl(null);
          }}
          disabled={!selectedAgent || selectedAgent.isActive}
        >
          <ListItemIcon>
            <PlayIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText>Resume Agent</ListItemText>
        </MenuItem>
        <MenuItem 
          onClick={() => {
            if (selectedAgent && onStopAgent) {
              onStopAgent(selectedAgent.id);
            }
            setAnchorEl(null);
          }}
          disabled={!selectedAgent}
        >
          <ListItemIcon>
            <StopIcon fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText>Stop Agent</ListItemText>
        </MenuItem>
      </Menu>
    );
  };
  
  return (
    <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h2">
            Agent Activity
          </Typography>
          
          <Box>
            <Tooltip title="Refresh">
              <IconButton onClick={onRefresh} disabled={isLoading}>
                {isLoading ? <CircularProgress size={24} /> : <RefreshIcon />}
              </IconButton>
            </Tooltip>
            <Tooltip title="Filter">
              <IconButton 
                onClick={(e) => setFilterMenuAnchor(e.currentTarget)}
                color={
                  filters.types.length > 0 || 
                  filters.status.length > 0 || 
                  filters.timeRange !== 'all' || 
                  filters.agents.length > 0 
                    ? 'primary' 
                    : 'default'
                }
              >
                <FilterAltIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Sort">
              <IconButton onClick={(e) => setSortMenuAnchor(e.currentTarget)}>
                <SortIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="View Mode">
              <IconButton
                onClick={(e) => setAnchorEl(e.currentTarget)}
              >
                <MoreVertIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Tabs 
              value={viewMode} 
              onChange={(e, newValue) => setViewMode(newValue)}
              sx={{ minHeight: 'auto' }}
            >
              <Tab 
                icon={<TimelineIcon />} 
                iconPosition="start" 
                label={isMobile ? "" : "Timeline"} 
                value="timeline" 
                sx={{ minHeight: 'auto', py: 1 }}
              />
              <Tab 
                icon={<ListViewIcon />} 
                iconPosition="start" 
                label={isMobile ? "" : "List"} 
                value="list" 
                sx={{ minHeight: 'auto', py: 1 }}
              />
              <Tab 
                icon={<GridViewIcon />} 
                iconPosition="start" 
                label={isMobile ? "" : "Grid"} 
                value="grid" 
                sx={{ minHeight: 'auto', py: 1 }}
              />
            </Tabs>
          </Box>
          
          <Box>
            <Typography variant="body2" color="text.secondary">
              {sortedActivities.length} activities
              {filters.types.length > 0 || 
               filters.status.length > 0 || 
               filters.timeRange !== 'all' || 
               filters.agents.length > 0 
                ? ' (filtered)' 
                : ''}
            </Typography>
          </Box>
        </Box>
      </Box>
      
      {/* Agent List */}
      <Box sx={{ px: 2, py: 1, borderBottom: 1, borderColor: 'divider' }}>
        {renderAgentList()}
      </Box>
      
      {/* Main Content */}
      <Box sx={{ flex: 1, overflow: 'hidden' }}>
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <CircularProgress />
          </Box>
        ) : sortedActivities.length === 0 ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100%', p: 3 }}>
            <TimelineIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No activities to display
            </Typography>
            <Typography variant="body2" color="text.secondary" align="center">
              {filters.types.length > 0 || 
               filters.status.length > 0 || 
               filters.timeRange !== 'all' || 
               filters.agents.length > 0 
                ? 'Try changing your filters to see more activities' 
                : 'Activities will appear here as agents perform tasks'}
            </Typography>
            {(filters.types.length > 0 || 
              filters.status.length > 0 || 
              filters.timeRange !== 'all' || 
              filters.agents.length > 0) && (
              <Button 
                variant="outlined" 
                startIcon={<FilterAltIcon />} 
                onClick={() => {
                  handleFilterChange('types', []);
                  handleFilterChange('status', []);
                  handleFilterChange('timeRange', 'all');
                  handleFilterChange('agents', []);
                }}
                sx={{ mt: 2 }}
              >
                Clear Filters
              </Button>
            )}
          </Box>
        ) : (
          <>
            {viewMode === 'timeline' && renderTimelineView()}
            {viewMode === 'list' && renderListView()}
            {viewMode === 'grid' && renderGridView()}
          </>
        )}
      </Box>
      
      {/* Menus */}
      {renderFilterMenu()}
      {renderSortMenu()}
      {renderAgentControlMenu()}
    </Paper>
  );
};

EnhancedAgentActivityPanel.propTypes = {
  agents: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      type: PropTypes.string.isRequired,
      isActive: PropTypes.bool.isRequired
    })
  ),
  activities: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      agentId: PropTypes.string.isRequired,
      agentName: PropTypes.string.isRequired,
      type: PropTypes.string.isRequired,
      title: PropTypes.string.isRequired,
      description: PropTypes.string,
      timestamp: PropTypes.string.isRequired,
      duration: PropTypes.number,
      status: PropTypes.string,
      details: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
      result: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
      metrics: PropTypes.object,
      priority: PropTypes.number,
      isBookmarked: PropTypes.bool,
      actions: PropTypes.arrayOf(
        PropTypes.shape({
          label: PropTypes.string.isRequired,
          icon: PropTypes.node,
          handler: PropTypes.func
        })
      )
    })
  ),
  onRefresh: PropTypes.func,
  onFilterChange: PropTypes.func,
  onAgentSelect: PropTypes.func,
  onActivitySelect: PropTypes.func,
  onPauseAgent: PropTypes.func,
  onResumeAgent: PropTypes.func,
  onStopAgent: PropTypes.func,
  onBookmarkActivity: PropTypes.func,
  isLoading: PropTypes.bool
};

export default EnhancedAgentActivityPanel;
