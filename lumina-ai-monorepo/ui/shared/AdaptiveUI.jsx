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
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Card,
  CardContent,
  CardHeader,
  CardActions,
  Switch,
  FormControlLabel,
  Avatar,
  Badge,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemAvatar,
  Collapse,
  Drawer,
  useMediaQuery,
  useTheme
} from '@mui/material';
import { 
  Settings as SettingsIcon,
  Tune as TuneIcon,
  Refresh as RefreshIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Palette as PaletteIcon,
  FormatSize as FontSizeIcon,
  Notifications as NotificationsIcon,
  NotificationsOff as NotificationsOffIcon,
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  Translate as TranslateIcon,
  AccessibilityNew as AccessibilityIcon,
  Speed as PerformanceIcon,
  Save as SaveIcon,
  Person as PersonIcon,
  PersonOutline as PersonOutlineIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  History as HistoryIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  Dashboard as DashboardIcon,
  ViewList as ListViewIcon,
  ViewModule as GridViewIcon,
  FormatListBulleted as BulletListIcon,
  FormatListNumbered as NumberedListIcon
} from '@mui/icons-material';

/**
 * Adaptive UI Component
 * 
 * Provides a personalized user experience based on usage patterns,
 * preferences, and accessibility needs.
 */
const AdaptiveUI = ({ 
  userPreferences = {}, 
  usagePatterns = {},
  suggestedSettings = {},
  onPreferenceChange,
  onLayoutChange,
  onThemeChange,
  onAccessibilityChange,
  onReset,
  isLoading = false
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [activeTab, setActiveTab] = useState(0);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    appearance: true,
    layout: true,
    accessibility: true,
    notifications: true,
    performance: true,
    privacy: true
  });
  const [tempPreferences, setTempPreferences] = useState(userPreferences);
  const [hasChanges, setHasChanges] = useState(false);
  
  // Update temp preferences when user preferences change
  useEffect(() => {
    setTempPreferences(userPreferences);
  }, [userPreferences]);
  
  // Check if there are unsaved changes
  useEffect(() => {
    const hasUnsavedChanges = JSON.stringify(tempPreferences) !== JSON.stringify(userPreferences);
    setHasChanges(hasUnsavedChanges);
  }, [tempPreferences, userPreferences]);
  
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  const toggleDrawer = (open) => {
    setIsDrawerOpen(open);
  };
  
  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };
  
  const handlePreferenceChange = (category, setting, value) => {
    setTempPreferences(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [setting]: value
      }
    }));
  };
  
  const handleSaveChanges = () => {
    if (onPreferenceChange) {
      onPreferenceChange(tempPreferences);
    }
  };
  
  const handleResetToDefaults = () => {
    if (onReset) {
      onReset();
    }
  };
  
  const handleApplySuggested = (category) => {
    if (suggestedSettings && suggestedSettings[category]) {
      setTempPreferences(prev => ({
        ...prev,
        [category]: {
          ...prev[category],
          ...suggestedSettings[category]
        }
      }));
    }
  };
  
  const renderAppearanceSettings = () => {
    const appearance = tempPreferences.appearance || {};
    
    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Appearance
          </Typography>
          <IconButton onClick={() => toggleSection('appearance')}>
            {expandedSections.appearance ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>
        
        <Collapse in={expandedSections.appearance}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Theme
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Card 
                  sx={{ 
                    width: 120, 
                    cursor: 'pointer',
                    border: appearance.theme === 'light' ? `2px solid ${theme.palette.primary.main}` : '2px solid transparent'
                  }}
                  onClick={() => handlePreferenceChange('appearance', 'theme', 'light')}
                >
                  <CardContent sx={{ p: 1, textAlign: 'center' }}>
                    <LightModeIcon sx={{ fontSize: 40, color: 'warning.main', mb: 1 }} />
                    <Typography variant="body2">Light</Typography>
                  </CardContent>
                </Card>
                
                <Card 
                  sx={{ 
                    width: 120, 
                    cursor: 'pointer',
                    border: appearance.theme === 'dark' ? `2px solid ${theme.palette.primary.main}` : '2px solid transparent'
                  }}
                  onClick={() => handlePreferenceChange('appearance', 'theme', 'dark')}
                >
                  <CardContent sx={{ p: 1, textAlign: 'center' }}>
                    <DarkModeIcon sx={{ fontSize: 40, color: 'text.secondary', mb: 1 }} />
                    <Typography variant="body2">Dark</Typography>
                  </CardContent>
                </Card>
                
                <Card 
                  sx={{ 
                    width: 120, 
                    cursor: 'pointer',
                    border: appearance.theme === 'system' ? `2px solid ${theme.palette.primary.main}` : '2px solid transparent'
                  }}
                  onClick={() => handlePreferenceChange('appearance', 'theme', 'system')}
                >
                  <CardContent sx={{ p: 1, textAlign: 'center' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'center', mb: 1 }}>
                      <LightModeIcon sx={{ fontSize: 30, color: 'warning.main' }} />
                      <DarkModeIcon sx={{ fontSize: 30, color: 'text.secondary', ml: -1 }} />
                    </Box>
                    <Typography variant="body2">System</Typography>
                  </CardContent>
                </Card>
              </Box>
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Color Scheme
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
                {['blue', 'purple', 'green', 'orange', 'teal'].map(color => (
                  <Card 
                    key={color}
                    sx={{ 
                      width: 80, 
                      cursor: 'pointer',
                      border: appearance.colorScheme === color ? `2px solid ${theme.palette.primary.main}` : '2px solid transparent'
                    }}
                    onClick={() => handlePreferenceChange('appearance', 'colorScheme', color)}
                  >
                    <Box 
                      sx={{ 
                        height: 40, 
                        bgcolor: 
                          color === 'blue' ? '#1976d2' : 
                          color === 'purple' ? '#9c27b0' : 
                          color === 'green' ? '#2e7d32' : 
                          color === 'orange' ? '#ed6c02' : 
                          color === 'teal' ? '#009688' : 
                          'primary.main'
                      }} 
                    />
                    <CardContent sx={{ p: 1, textAlign: 'center' }}>
                      <Typography variant="caption" sx={{ textTransform: 'capitalize' }}>
                        {color}
                      </Typography>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Font Size
              </Typography>
              <Slider
                value={appearance.fontSize || 16}
                min={12}
                max={24}
                step={1}
                marks={[
                  { value: 12, label: 'S' },
                  { value: 16, label: 'M' },
                  { value: 20, label: 'L' },
                  { value: 24, label: 'XL' }
                ]}
                valueLabelDisplay="auto"
                onChange={(e, value) => handlePreferenceChange('appearance', 'fontSize', value)}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Density
              </Typography>
              <Slider
                value={appearance.density || 'normal'}
                min={0}
                max={2}
                step={1}
                marks={[
                  { value: 0, label: 'Compact' },
                  { value: 1, label: 'Normal' },
                  { value: 2, label: 'Comfortable' }
                ]}
                valueLabelDisplay="off"
                onChange={(e, value) => {
                  const densityMap = {
                    0: 'compact',
                    1: 'normal',
                    2: 'comfortable'
                  };
                  handlePreferenceChange('appearance', 'density', densityMap[value]);
                }}
              />
            </Grid>
          </Grid>
          
          {suggestedSettings.appearance && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Suggested Settings
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Based on your usage patterns, we recommend these appearance settings:
              </Typography>
              <List dense>
                {Object.entries(suggestedSettings.appearance).map(([key, value]) => (
                  <ListItem key={key}>
                    <ListItemIcon>
                      <CheckIcon fontSize="small" color="success" />
                    </ListItemIcon>
                    <ListItemText 
                      primary={
                        key === 'theme' ? `Theme: ${value}` :
                        key === 'colorScheme' ? `Color Scheme: ${value}` :
                        key === 'fontSize' ? `Font Size: ${value}px` :
                        key === 'density' ? `Density: ${value}` :
                        `${key}: ${value}`
                      } 
                    />
                  </ListItem>
                ))}
              </List>
              <Button 
                variant="outlined" 
                size="small" 
                onClick={() => handleApplySuggested('appearance')}
                sx={{ mt: 1 }}
              >
                Apply Suggested Settings
              </Button>
            </Box>
          )}
        </Collapse>
        
        <Divider sx={{ my: 2 }} />
      </Box>
    );
  };
  
  const renderLayoutSettings = () => {
    const layout = tempPreferences.layout || {};
    
    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Layout
          </Typography>
          <IconButton onClick={() => toggleSection('layout')}>
            {expandedSections.layout ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>
        
        <Collapse in={expandedSections.layout}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Default View
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Card 
                  sx={{ 
                    width: 120, 
                    cursor: 'pointer',
                    border: layout.defaultView === 'list' ? `2px solid ${theme.palette.primary.main}` : '2px solid transparent'
                  }}
                  onClick={() => handlePreferenceChange('layout', 'defaultView', 'list')}
                >
                  <CardContent sx={{ p: 1, textAlign: 'center' }}>
                    <ListViewIcon sx={{ fontSize: 40, mb: 1 }} />
                    <Typography variant="body2">List</Typography>
                  </CardContent>
                </Card>
                
                <Card 
                  sx={{ 
                    width: 120, 
                    cursor: 'pointer',
                    border: layout.defaultView === 'grid' ? `2px solid ${theme.palette.primary.main}` : '2px solid transparent'
                  }}
                  onClick={() => handlePreferenceChange('layout', 'defaultView', 'grid')}
                >
                  <CardContent sx={{ p: 1, textAlign: 'center' }}>
                    <GridViewIcon sx={{ fontSize: 40, mb: 1 }} />
                    <Typography variant="body2">Grid</Typography>
                  </CardContent>
                </Card>
                
                <Card 
                  sx={{ 
                    width: 120, 
                    cursor: 'pointer',
                    border: layout.defaultView === 'dashboard' ? `2px solid ${theme.palette.primary.main}` : '2px solid transparent'
                  }}
                  onClick={() => handlePreferenceChange('layout', 'defaultView', 'dashboard')}
                >
                  <CardContent sx={{ p: 1, textAlign: 'center' }}>
                    <DashboardIcon sx={{ fontSize: 40, mb: 1 }} />
                    <Typography variant="body2">Dashboard</Typography>
                  </CardContent>
                </Card>
              </Box>
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Sidebar Position
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={layout.sidebarPosition === 'left'}
                      onChange={() => handlePreferenceChange('layout', 'sidebarPosition', 'left')}
                    />
                  }
                  label="Left"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={layout.sidebarPosition === 'right'}
                      onChange={() => handlePreferenceChange('layout', 'sidebarPosition', 'right')}
                    />
                  }
                  label="Right"
                />
              </Box>
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Show Recent Activity
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={layout.showRecentActivity}
                    onChange={(e) => handlePreferenceChange('layout', 'showRecentActivity', e.target.checked)}
                  />
                }
                label="Display recent activity in sidebar"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Show Favorites
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={layout.showFavorites}
                    onChange={(e) => handlePreferenceChange('layout', 'showFavorites', e.target.checked)}
                  />
                }
                label="Display favorites in sidebar"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Workspace Layout
              </Typography>
              <Select
                fullWidth
                value={layout.workspaceLayout || 'split'}
                onChange={(e) => handlePreferenceChange('layout', 'workspaceLayout', e.target.value)}
              >
                <MenuItem value="split">Split View</MenuItem>
                <MenuItem value="tabbed">Tabbed View</MenuItem>
                <MenuItem value="stacked">Stacked View</MenuItem>
              </Select>
            </Grid>
          </Grid>
          
          {suggestedSettings.layout && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Suggested Layout
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Based on your usage patterns, we recommend these layout settings:
              </Typography>
              <List dense>
                {Object.entries(suggestedSettings.layout).map(([key, value]) => (
                  <ListItem key={key}>
                    <ListItemIcon>
                      <CheckIcon fontSize="small" color="success" />
                    </ListItemIcon>
                    <ListItemText 
                      primary={
                        key === 'defaultView' ? `Default View: ${value}` :
                        key === 'sidebarPosition' ? `Sidebar Position: ${value}` :
                        key === 'showRecentActivity' ? `Show Recent Activity: ${value ? 'Yes' : 'No'}` :
                        key === 'showFavorites' ? `Show Favorites: ${value ? 'Yes' : 'No'}` :
                        key === 'workspaceLayout' ? `Workspace Layout: ${value}` :
                        `${key}: ${value}`
                      } 
                    />
                  </ListItem>
                ))}
              </List>
              <Button 
                variant="outlined" 
                size="small" 
                onClick={() => handleApplySuggested('layout')}
                sx={{ mt: 1 }}
              >
                Apply Suggested Layout
              </Button>
            </Box>
          )}
        </Collapse>
        
        <Divider sx={{ my: 2 }} />
      </Box>
    );
  };
  
  const renderAccessibilitySettings = () => {
    const accessibility = tempPreferences.accessibility || {};
    
    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Accessibility
          </Typography>
          <IconButton onClick={() => toggleSection('accessibility')}>
            {expandedSections.accessibility ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>
        
        <Collapse in={expandedSections.accessibility}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                High Contrast Mode
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={accessibility.highContrast}
                    onChange={(e) => handlePreferenceChange('accessibility', 'highContrast', e.target.checked)}
                  />
                }
                label="Enable high contrast"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Reduce Motion
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={accessibility.reduceMotion}
                    onChange={(e) => handlePreferenceChange('accessibility', 'reduceMotion', e.target.checked)}
                  />
                }
                label="Minimize animations and transitions"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Screen Reader Support
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={accessibility.screenReaderSupport}
                    onChange={(e) => handlePreferenceChange('accessibility', 'screenReaderSupport', e.target.checked)}
                  />
                }
                label="Optimize for screen readers"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Keyboard Navigation
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={accessibility.keyboardNavigation}
                    onChange={(e) => handlePreferenceChange('accessibility', 'keyboardNavigation', e.target.checked)}
                  />
                }
                label="Enhanced keyboard navigation"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Text Spacing
              </Typography>
              <Slider
                value={accessibility.textSpacing || 1}
                min={1}
                max={2}
                step={0.1}
                marks={[
                  { value: 1, label: 'Normal' },
                  { value: 1.5, label: 'Medium' },
                  { value: 2, label: 'Large' }
                ]}
                valueLabelDisplay="auto"
                onChange={(e, value) => handlePreferenceChange('accessibility', 'textSpacing', value)}
              />
            </Grid>
          </Grid>
        </Collapse>
        
        <Divider sx={{ my: 2 }} />
      </Box>
    );
  };
  
  const renderNotificationSettings = () => {
    const notifications = tempPreferences.notifications || {};
    
    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Notifications
          </Typography>
          <IconButton onClick={() => toggleSection('notifications')}>
            {expandedSections.notifications ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>
        
        <Collapse in={expandedSections.notifications}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Enable Notifications
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={notifications.enabled}
                    onChange={(e) => handlePreferenceChange('notifications', 'enabled', e.target.checked)}
                  />
                }
                label="Allow notifications"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Notification Types
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={notifications.taskCompletions}
                    onChange={(e) => handlePreferenceChange('notifications', 'taskCompletions', e.target.checked)}
                    disabled={!notifications.enabled}
                  />
                }
                label="Task completions"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={notifications.mentions}
                    onChange={(e) => handlePreferenceChange('notifications', 'mentions', e.target.checked)}
                    disabled={!notifications.enabled}
                  />
                }
                label="Mentions"
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={notifications.systemUpdates}
                    onChange={(e) => handlePreferenceChange('notifications', 'systemUpdates', e.target.checked)}
                    disabled={!notifications.enabled}
                  />
                }
                label="System updates"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Notification Sound
              </Typography>
              <Select
                fullWidth
                value={notifications.sound || 'default'}
                onChange={(e) => handlePreferenceChange('notifications', 'sound', e.target.value)}
                disabled={!notifications.enabled}
              >
                <MenuItem value="none">None</MenuItem>
                <MenuItem value="default">Default</MenuItem>
                <MenuItem value="subtle">Subtle</MenuItem>
                <MenuItem value="chime">Chime</MenuItem>
              </Select>
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Do Not Disturb
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={notifications.doNotDisturb}
                    onChange={(e) => handlePreferenceChange('notifications', 'doNotDisturb', e.target.checked)}
                    disabled={!notifications.enabled}
                  />
                }
                label="Enable Do Not Disturb mode"
              />
              {notifications.doNotDisturb && (
                <Box sx={{ ml: 4, mt: 1 }}>
                  <Typography variant="body2" gutterBottom>
                    Do Not Disturb Hours
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                    <TextField
                      label="From"
                      type="time"
                      value={notifications.doNotDisturbStart || '22:00'}
                      onChange={(e) => handlePreferenceChange('notifications', 'doNotDisturbStart', e.target.value)}
                      InputLabelProps={{ shrink: true }}
                      inputProps={{ step: 300 }}
                      disabled={!notifications.enabled}
                    />
                    <Typography variant="body2">to</Typography>
                    <TextField
                      label="To"
                      type="time"
                      value={notifications.doNotDisturbEnd || '08:00'}
                      onChange={(e) => handlePreferenceChange('notifications', 'doNotDisturbEnd', e.target.value)}
                      InputLabelProps={{ shrink: true }}
                      inputProps={{ step: 300 }}
                      disabled={!notifications.enabled}
                    />
                  </Box>
                </Box>
              )}
            </Grid>
          </Grid>
          
          {suggestedSettings.notifications && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Suggested Notification Settings
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Based on your usage patterns, we recommend these notification settings:
              </Typography>
              <List dense>
                {Object.entries(suggestedSettings.notifications).map(([key, value]) => (
                  <ListItem key={key}>
                    <ListItemIcon>
                      <CheckIcon fontSize="small" color="success" />
                    </ListItemIcon>
                    <ListItemText 
                      primary={
                        key === 'enabled' ? `Enable Notifications: ${value ? 'Yes' : 'No'}` :
                        key === 'taskCompletions' ? `Task Completions: ${value ? 'Yes' : 'No'}` :
                        key === 'mentions' ? `Mentions: ${value ? 'Yes' : 'No'}` :
                        key === 'systemUpdates' ? `System Updates: ${value ? 'Yes' : 'No'}` :
                        key === 'sound' ? `Sound: ${value}` :
                        key === 'doNotDisturb' ? `Do Not Disturb: ${value ? 'Yes' : 'No'}` :
                        `${key}: ${value}`
                      } 
                    />
                  </ListItem>
                ))}
              </List>
              <Button 
                variant="outlined" 
                size="small" 
                onClick={() => handleApplySuggested('notifications')}
                sx={{ mt: 1 }}
              >
                Apply Suggested Settings
              </Button>
            </Box>
          )}
        </Collapse>
        
        <Divider sx={{ my: 2 }} />
      </Box>
    );
  };
  
  const renderPerformanceSettings = () => {
    const performance = tempPreferences.performance || {};
    
    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Performance
          </Typography>
          <IconButton onClick={() => toggleSection('performance')}>
            {expandedSections.performance ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>
        
        <Collapse in={expandedSections.performance}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Animation Quality
              </Typography>
              <Select
                fullWidth
                value={performance.animationQuality || 'medium'}
                onChange={(e) => handlePreferenceChange('performance', 'animationQuality', e.target.value)}
              >
                <MenuItem value="low">Low (Best Performance)</MenuItem>
                <MenuItem value="medium">Medium (Balanced)</MenuItem>
                <MenuItem value="high">High (Best Appearance)</MenuItem>
              </Select>
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Memory Usage
              </Typography>
              <Select
                fullWidth
                value={performance.memoryUsage || 'balanced'}
                onChange={(e) => handlePreferenceChange('performance', 'memoryUsage', e.target.value)}
              >
                <MenuItem value="minimal">Minimal (Best Performance)</MenuItem>
                <MenuItem value="balanced">Balanced</MenuItem>
                <MenuItem value="maximum">Maximum (Best Experience)</MenuItem>
              </Select>
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Background Processing
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={performance.backgroundProcessing}
                    onChange={(e) => handlePreferenceChange('performance', 'backgroundProcessing', e.target.checked)}
                  />
                }
                label="Allow background processing"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Data Prefetching
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={performance.dataPrefetching}
                    onChange={(e) => handlePreferenceChange('performance', 'dataPrefetching', e.target.checked)}
                  />
                }
                label="Prefetch data for faster navigation"
              />
            </Grid>
          </Grid>
          
          {suggestedSettings.performance && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Suggested Performance Settings
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                Based on your device capabilities, we recommend these performance settings:
              </Typography>
              <List dense>
                {Object.entries(suggestedSettings.performance).map(([key, value]) => (
                  <ListItem key={key}>
                    <ListItemIcon>
                      <CheckIcon fontSize="small" color="success" />
                    </ListItemIcon>
                    <ListItemText 
                      primary={
                        key === 'animationQuality' ? `Animation Quality: ${value}` :
                        key === 'memoryUsage' ? `Memory Usage: ${value}` :
                        key === 'backgroundProcessing' ? `Background Processing: ${value ? 'Yes' : 'No'}` :
                        key === 'dataPrefetching' ? `Data Prefetching: ${value ? 'Yes' : 'No'}` :
                        `${key}: ${value}`
                      } 
                    />
                  </ListItem>
                ))}
              </List>
              <Button 
                variant="outlined" 
                size="small" 
                onClick={() => handleApplySuggested('performance')}
                sx={{ mt: 1 }}
              >
                Apply Suggested Settings
              </Button>
            </Box>
          )}
        </Collapse>
        
        <Divider sx={{ my: 2 }} />
      </Box>
    );
  };
  
  const renderPrivacySettings = () => {
    const privacy = tempPreferences.privacy || {};
    
    return (
      <Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Privacy
          </Typography>
          <IconButton onClick={() => toggleSection('privacy')}>
            {expandedSections.privacy ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        </Box>
        
        <Collapse in={expandedSections.privacy}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Data Collection
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={privacy.dataCollection}
                    onChange={(e) => handlePreferenceChange('privacy', 'dataCollection', e.target.checked)}
                  />
                }
                label="Allow anonymous usage data collection"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Personalization
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={privacy.personalization}
                    onChange={(e) => handlePreferenceChange('privacy', 'personalization', e.target.checked)}
                  />
                }
                label="Allow personalization based on usage patterns"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Session Recording
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={privacy.sessionRecording}
                    onChange={(e) => handlePreferenceChange('privacy', 'sessionRecording', e.target.checked)}
                  />
                }
                label="Allow session recording for support purposes"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Third-Party Integrations
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={privacy.thirdPartyIntegrations}
                    onChange={(e) => handlePreferenceChange('privacy', 'thirdPartyIntegrations', e.target.checked)}
                  />
                }
                label="Allow third-party integrations"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Button 
                variant="outlined" 
                color="error" 
                startIcon={<DeleteIcon />}
                onClick={() => {
                  // This would typically open a confirmation dialog
                  alert('This would delete all your personal data');
                }}
              >
                Delete My Data
              </Button>
            </Grid>
          </Grid>
        </Collapse>
      </Box>
    );
  };
  
  const renderPreferencesTab = () => {
    return (
      <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
        {renderAppearanceSettings()}
        {renderLayoutSettings()}
        {renderAccessibilitySettings()}
        {renderNotificationSettings()}
        {renderPerformanceSettings()}
        {renderPrivacySettings()}
        
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
          <Button 
            variant="outlined" 
            color="error" 
            onClick={handleResetToDefaults}
          >
            Reset to Defaults
          </Button>
          
          <Button 
            variant="contained" 
            color="primary" 
            onClick={handleSaveChanges}
            disabled={!hasChanges}
            startIcon={<SaveIcon />}
          >
            Save Changes
          </Button>
        </Box>
      </Box>
    );
  };
  
  const renderUsageTab = () => {
    return (
      <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
        <Typography variant="h6" gutterBottom>
          Usage Patterns
        </Typography>
        
        <Typography variant="body2" paragraph>
          This tab shows how you use the application and provides insights to help optimize your experience.
        </Typography>
        
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Feature Usage" />
              <CardContent>
                {usagePatterns.featureUsage ? (
                  <Box sx={{ height: 300, display: 'flex', flexDirection: 'column' }}>
                    {Object.entries(usagePatterns.featureUsage).map(([feature, count]) => (
                      <Box key={feature} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body2" sx={{ flex: 1 }}>
                          {feature}
                        </Typography>
                        <Box sx={{ width: '60%', mr: 1 }}>
                          <Box 
                            sx={{ 
                              height: 8, 
                              bgcolor: 'primary.main', 
                              borderRadius: 1,
                              width: `${Math.min(100, count / usagePatterns.maxFeatureUsage * 100)}%`
                            }} 
                          />
                        </Box>
                        <Typography variant="caption" sx={{ width: 40, textAlign: 'right' }}>
                          {count}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No feature usage data available yet
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card>
              <CardHeader title="Session Statistics" />
              <CardContent>
                {usagePatterns.sessionStats ? (
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="subtitle2">Average Session</Typography>
                      <Typography variant="h6">{usagePatterns.sessionStats.averageSessionTime} min</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="subtitle2">Sessions</Typography>
                      <Typography variant="h6">{usagePatterns.sessionStats.totalSessions}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="subtitle2">Most Active Time</Typography>
                      <Typography variant="h6">{usagePatterns.sessionStats.mostActiveTime}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="subtitle2">Last Session</Typography>
                      <Typography variant="h6">{usagePatterns.sessionStats.lastSession}</Typography>
                    </Grid>
                  </Grid>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No session statistics available yet
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12}>
            <Card>
              <CardHeader title="Personalization Insights" />
              <CardContent>
                {usagePatterns.insights ? (
                  <List>
                    {usagePatterns.insights.map((insight, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <LightbulbIcon color="warning" />
                        </ListItemIcon>
                        <ListItemText 
                          primary={insight.title} 
                          secondary={insight.description} 
                        />
                        {insight.actionable && (
                          <Button 
                            size="small" 
                            variant="outlined"
                            onClick={() => {
                              // Apply this insight
                              if (insight.category && insight.settings) {
                                setTempPreferences(prev => ({
                                  ...prev,
                                  [insight.category]: {
                                    ...prev[insight.category],
                                    ...insight.settings
                                  }
                                }));
                              }
                            }}
                          >
                            Apply
                          </Button>
                        )}
                      </ListItem>
                    ))}
                  </List>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No personalization insights available yet. Continue using the application to generate insights.
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
    );
  };
  
  const renderSuggestionsTab = () => {
    return (
      <Box sx={{ p: 3, height: '100%', overflow: 'auto' }}>
        <Typography variant="h6" gutterBottom>
          Personalized Suggestions
        </Typography>
        
        <Typography variant="body2" paragraph>
          Based on your usage patterns, we've generated these suggestions to enhance your experience.
        </Typography>
        
        {Object.keys(suggestedSettings).length > 0 ? (
          <Grid container spacing={3}>
            {Object.entries(suggestedSettings).map(([category, settings]) => (
              <Grid item xs={12} key={category}>
                <Card>
                  <CardHeader 
                    title={category.charAt(0).toUpperCase() + category.slice(1)} 
                    action={
                      <Button 
                        size="small" 
                        variant="outlined"
                        onClick={() => handleApplySuggested(category)}
                      >
                        Apply All
                      </Button>
                    }
                  />
                  <CardContent>
                    <List dense>
                      {Object.entries(settings).map(([key, value]) => (
                        <ListItem key={key}>
                          <ListItemIcon>
                            <CheckIcon fontSize="small" color="success" />
                          </ListItemIcon>
                          <ListItemText 
                            primary={
                              `${key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1')}: ${typeof value === 'boolean' ? (value ? 'Enabled' : 'Disabled') : value}`
                            } 
                          />
                          <Button 
                            size="small"
                            onClick={() => handlePreferenceChange(category, key, value)}
                          >
                            Apply
                          </Button>
                        </ListItem>
                      ))}
                    </List>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', py: 8 }}>
            <TuneIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No suggestions available yet
            </Typography>
            <Typography variant="body2" color="text.secondary" align="center" sx={{ maxWidth: 400 }}>
              Continue using the application to generate personalized suggestions based on your usage patterns.
            </Typography>
          </Box>
        )}
      </Box>
    );
  };
  
  // Helper component for the LightbulbIcon
  const LightbulbIcon = ({ color }) => (
    <svg 
      width={24} 
      height={24} 
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path 
        d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7zm2.85 11.1l-.85.6V16h-4v-2.3l-.85-.6C7.8 12.16 7 10.63 7 9c0-2.76 2.24-5 5-5s5 2.24 5 5c0 1.63-.8 3.16-2.15 4.1z" 
        fill={color === 'warning' ? '#ed6c02' : 'currentColor'} 
      />
    </svg>
  );
  
  return (
    <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h2" gutterBottom>
        Adaptive UI
      </Typography>
      
      <Typography variant="body1" paragraph>
        Personalize your experience with these settings. The system will also learn from your usage patterns to suggest optimal configurations.
      </Typography>
      
      {/* Tabs */}
      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 2 }}>
        <Tab label="Preferences" icon={<SettingsIcon />} iconPosition="start" />
        <Tab label="Usage Patterns" icon={<HistoryIcon />} iconPosition="start" />
        <Tab 
          label="Suggestions" 
          icon={
            <Badge 
              badgeContent={Object.keys(suggestedSettings).length} 
              color="primary"
              invisible={Object.keys(suggestedSettings).length === 0}
            >
              <TuneIcon />
            </Badge>
          } 
          iconPosition="start" 
        />
      </Tabs>
      
      {/* Main content area */}
      <Box sx={{ flex: 1, overflow: 'hidden', border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {activeTab === 0 && renderPreferencesTab()}
            {activeTab === 1 && renderUsageTab()}
            {activeTab === 2 && renderSuggestionsTab()}
          </>
        )}
      </Box>
      
      {/* Mobile drawer for settings */}
      {isMobile && (
        <Drawer
          anchor="bottom"
          open={isDrawerOpen}
          onClose={() => toggleDrawer(false)}
        >
          <Box sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quick Settings
            </Typography>
            
            <List>
              <ListItem>
                <ListItemIcon>
                  <DarkModeIcon />
                </ListItemIcon>
                <ListItemText primary="Dark Mode" />
                <Switch
                  checked={(tempPreferences.appearance || {}).theme === 'dark'}
                  onChange={(e) => handlePreferenceChange('appearance', 'theme', e.target.checked ? 'dark' : 'light')}
                />
              </ListItem>
              
              <ListItem>
                <ListItemIcon>
                  <NotificationsIcon />
                </ListItemIcon>
                <ListItemText primary="Notifications" />
                <Switch
                  checked={(tempPreferences.notifications || {}).enabled}
                  onChange={(e) => handlePreferenceChange('notifications', 'enabled', e.target.checked)}
                />
              </ListItem>
              
              <ListItem>
                <ListItemIcon>
                  <AccessibilityIcon />
                </ListItemIcon>
                <ListItemText primary="Accessibility" />
                <Switch
                  checked={(tempPreferences.accessibility || {}).highContrast}
                  onChange={(e) => handlePreferenceChange('accessibility', 'highContrast', e.target.checked)}
                />
              </ListItem>
            </List>
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
              <Button onClick={() => toggleDrawer(false)}>
                Close
              </Button>
              <Button 
                color="primary" 
                onClick={handleSaveChanges}
                disabled={!hasChanges}
                sx={{ ml: 1 }}
              >
                Save
              </Button>
            </Box>
          </Box>
        </Drawer>
      )}
      
      {/* Mobile FAB for quick settings */}
      {isMobile && (
        <Box sx={{ position: 'fixed', bottom: 16, right: 16 }}>
          <Tooltip title="Quick Settings">
            <IconButton
              color="primary"
              sx={{ bgcolor: 'background.paper', boxShadow: 2 }}
              onClick={() => toggleDrawer(true)}
            >
              <SettingsIcon />
            </IconButton>
          </Tooltip>
        </Box>
      )}
    </Paper>
  );
};

AdaptiveUI.propTypes = {
  userPreferences: PropTypes.shape({
    appearance: PropTypes.object,
    layout: PropTypes.object,
    accessibility: PropTypes.object,
    notifications: PropTypes.object,
    performance: PropTypes.object,
    privacy: PropTypes.object
  }),
  usagePatterns: PropTypes.shape({
    featureUsage: PropTypes.object,
    maxFeatureUsage: PropTypes.number,
    sessionStats: PropTypes.object,
    insights: PropTypes.arrayOf(
      PropTypes.shape({
        title: PropTypes.string,
        description: PropTypes.string,
        actionable: PropTypes.bool,
        category: PropTypes.string,
        settings: PropTypes.object
      })
    )
  }),
  suggestedSettings: PropTypes.object,
  onPreferenceChange: PropTypes.func,
  onLayoutChange: PropTypes.func,
  onThemeChange: PropTypes.func,
  onAccessibilityChange: PropTypes.func,
  onReset: PropTypes.func,
  isLoading: PropTypes.bool
};

export default AdaptiveUI;
