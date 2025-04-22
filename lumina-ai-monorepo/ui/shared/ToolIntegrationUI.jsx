import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { 
  Box, 
  Typography, 
  Paper, 
  Tabs, 
  Tab,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Tooltip,
  Divider,
  Button,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Badge,
  Card,
  CardContent,
  CardActions,
  Grid,
  Switch,
  FormControlLabel,
  CircularProgress
} from '@mui/material';
import { 
  Build as ToolIcon,
  Code as CodeIcon,
  Search as SearchIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  PlayArrow as RunIcon,
  Refresh as RefreshIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  History as HistoryIcon,
  Settings as SettingsIcon,
  FilterList as FilterIcon,
  Category as CategoryIcon,
  Extension as ExtensionIcon,
  CloudDownload as InstallIcon,
  Info as InfoIcon,
  Link as LinkIcon,
  OpenInNew as OpenInNewIcon
} from '@mui/icons-material';

/**
 * Tool Integration UI Component
 * 
 * Provides a comprehensive interface for discovering, configuring,
 * and using tools within the Lumina AI platform.
 */
const ToolIntegrationUI = ({ 
  tools = [], 
  categories = [],
  installedTools = [],
  recentTools = [],
  favoriteTools = [],
  onToolSelect,
  onToolInstall,
  onToolUninstall,
  onToolFavorite,
  onToolRun,
  onToolConfigure,
  onToolCreate,
  isLoading = false
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showOnlyInstalled, setShowOnlyInstalled] = useState(false);
  const [selectedTool, setSelectedTool] = useState(null);
  const [isToolDialogOpen, setIsToolDialogOpen] = useState(false);
  const [toolDialogMode, setToolDialogMode] = useState('view'); // view, configure, run
  
  // Filter tools based on search query, category, and installation status
  const filteredTools = tools.filter(tool => {
    // Search query filter
    if (searchQuery && !tool.name.toLowerCase().includes(searchQuery.toLowerCase()) && 
        !tool.description.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    
    // Category filter
    if (selectedCategory !== 'all' && tool.category !== selectedCategory) {
      return false;
    }
    
    // Installation status filter
    if (showOnlyInstalled && !installedTools.includes(tool.id)) {
      return false;
    }
    
    return true;
  });
  
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
  };
  
  const handleCategoryChange = (event) => {
    setSelectedCategory(event.target.value);
  };
  
  const handleToolClick = (tool) => {
    setSelectedTool(tool);
    setToolDialogMode('view');
    setIsToolDialogOpen(true);
    
    if (onToolSelect) {
      onToolSelect(tool);
    }
  };
  
  const handleToolRun = (tool) => {
    setSelectedTool(tool);
    setToolDialogMode('run');
    setIsToolDialogOpen(true);
    
    if (onToolRun) {
      onToolRun(tool);
    }
  };
  
  const handleToolConfigure = (tool) => {
    setSelectedTool(tool);
    setToolDialogMode('configure');
    setIsToolDialogOpen(true);
    
    if (onToolConfigure) {
      onToolConfigure(tool);
    }
  };
  
  const handleToolFavorite = (tool, isFavorite) => {
    if (onToolFavorite) {
      onToolFavorite(tool, isFavorite);
    }
  };
  
  const handleToolInstall = (tool) => {
    if (onToolInstall) {
      onToolInstall(tool);
    }
  };
  
  const handleToolUninstall = (tool) => {
    if (onToolUninstall) {
      onToolUninstall(tool);
    }
  };
  
  const handleCloseToolDialog = () => {
    setIsToolDialogOpen(false);
  };
  
  const isToolInstalled = (toolId) => {
    return installedTools.includes(toolId);
  };
  
  const isToolFavorite = (toolId) => {
    return favoriteTools.includes(toolId);
  };
  
  const renderToolList = (toolsToRender) => {
    return (
      <List>
        {toolsToRender.map(tool => (
          <ListItem 
            key={tool.id} 
            button 
            onClick={() => handleToolClick(tool)}
            sx={{ 
              borderRadius: 1,
              mb: 0.5,
              border: '1px solid',
              borderColor: 'divider'
            }}
          >
            <ListItemIcon>
              {tool.icon ? (
                <tool.icon />
              ) : (
                <ExtensionIcon color={isToolInstalled(tool.id) ? 'primary' : 'disabled'} />
              )}
            </ListItemIcon>
            
            <ListItemText 
              primary={
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  {tool.name}
                  {isToolFavorite(tool.id) && (
                    <StarIcon color="warning" sx={{ ml: 1, fontSize: 16 }} />
                  )}
                </Box>
              }
              secondary={
                <Typography variant="body2" color="text.secondary" sx={{
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  display: '-webkit-box',
                  WebkitLineClamp: 2,
                  WebkitBoxOrient: 'vertical'
                }}>
                  {tool.description}
                </Typography>
              }
            />
            
            <ListItemSecondaryAction>
              <Tooltip title={isToolInstalled(tool.id) ? "Run Tool" : "Install Tool"}>
                <IconButton 
                  edge="end" 
                  onClick={(e) => {
                    e.stopPropagation();
                    isToolInstalled(tool.id) ? handleToolRun(tool) : handleToolInstall(tool);
                  }}
                  color="primary"
                >
                  {isToolInstalled(tool.id) ? <RunIcon /> : <InstallIcon />}
                </IconButton>
              </Tooltip>
            </ListItemSecondaryAction>
          </ListItem>
        ))}
        
        {toolsToRender.length === 0 && (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', py: 4 }}>
            <ToolIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="body1" color="text.secondary">
              No tools found matching your criteria
            </Typography>
          </Box>
        )}
      </List>
    );
  };
  
  const renderToolGrid = (toolsToRender) => {
    return (
      <Grid container spacing={2}>
        {toolsToRender.map(tool => (
          <Grid item xs={12} sm={6} md={4} key={tool.id}>
            <Card 
              sx={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                cursor: 'pointer',
                transition: 'all 0.2s',
                '&:hover': {
                  boxShadow: 3
                }
              }}
              onClick={() => handleToolClick(tool)}
            >
              <CardContent sx={{ flexGrow: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  {tool.icon ? (
                    <tool.icon sx={{ mr: 1, color: isToolInstalled(tool.id) ? 'primary.main' : 'text.secondary' }} />
                  ) : (
                    <ExtensionIcon sx={{ mr: 1, color: isToolInstalled(tool.id) ? 'primary.main' : 'text.secondary' }} />
                  )}
                  
                  <Typography variant="h6" component="div">
                    {tool.name}
                  </Typography>
                  
                  <Box sx={{ ml: 'auto' }}>
                    <IconButton 
                      size="small" 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleToolFavorite(tool, !isToolFavorite(tool.id));
                      }}
                    >
                      {isToolFavorite(tool.id) ? (
                        <StarIcon fontSize="small" color="warning" />
                      ) : (
                        <StarBorderIcon fontSize="small" />
                      )}
                    </IconButton>
                  </Box>
                </Box>
                
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {tool.description}
                </Typography>
                
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                  <Chip 
                    label={tool.category} 
                    size="small" 
                    color="primary" 
                    variant="outlined" 
                  />
                  
                  {tool.tags && tool.tags.map(tag => (
                    <Chip 
                      key={tag} 
                      label={tag} 
                      size="small" 
                      variant="outlined" 
                    />
                  ))}
                </Box>
                
                <Typography variant="caption" color="text.secondary">
                  Version: {tool.version}
                </Typography>
              </CardContent>
              
              <CardActions>
                {isToolInstalled(tool.id) ? (
                  <>
                    <Button 
                      size="small" 
                      startIcon={<RunIcon />}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleToolRun(tool);
                      }}
                    >
                      Run
                    </Button>
                    <Button 
                      size="small" 
                      startIcon={<SettingsIcon />}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleToolConfigure(tool);
                      }}
                    >
                      Configure
                    </Button>
                    <Button 
                      size="small" 
                      color="error"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleToolUninstall(tool);
                      }}
                    >
                      Uninstall
                    </Button>
                  </>
                ) : (
                  <Button 
                    size="small" 
                    startIcon={<InstallIcon />}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleToolInstall(tool);
                    }}
                    color="primary"
                  >
                    Install
                  </Button>
                )}
              </CardActions>
            </Card>
          </Grid>
        ))}
        
        {toolsToRender.length === 0 && (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', py: 4, width: '100%' }}>
            <ToolIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="body1" color="text.secondary">
              No tools found matching your criteria
            </Typography>
          </Box>
        )}
      </Grid>
    );
  };
  
  const renderAllTools = () => {
    return (
      <Box sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <FormControl sx={{ minWidth: 200, mr: 2 }}>
            <InputLabel id="category-select-label">Category</InputLabel>
            <Select
              labelId="category-select-label"
              value={selectedCategory}
              label="Category"
              onChange={handleCategoryChange}
              size="small"
            >
              <MenuItem value="all">All Categories</MenuItem>
              {categories.map(category => (
                <MenuItem key={category.id} value={category.id}>{category.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          
          <FormControlLabel
            control={
              <Switch
                checked={showOnlyInstalled}
                onChange={(e) => setShowOnlyInstalled(e.target.checked)}
              />
            }
            label="Show only installed"
          />
          
          <Box sx={{ flex: 1 }} />
          
          <Button 
            variant="outlined" 
            startIcon={<AddIcon />}
            onClick={() => onToolCreate && onToolCreate()}
            sx={{ mr: 2 }}
          >
            Create Custom Tool
          </Button>
          
          <Button 
            variant="outlined" 
            startIcon={<RefreshIcon />}
            onClick={() => {
              // Refresh tool list
              setSearchQuery('');
              setSelectedCategory('all');
            }}
          >
            Refresh
          </Button>
        </Box>
        
        {renderToolGrid(filteredTools)}
      </Box>
    );
  };
  
  const renderInstalledTools = () => {
    const installed = tools.filter(tool => installedTools.includes(tool.id));
    
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Installed Tools
        </Typography>
        
        {renderToolGrid(installed)}
      </Box>
    );
  };
  
  const renderFavoriteTools = () => {
    const favorites = tools.filter(tool => favoriteTools.includes(tool.id));
    
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Favorite Tools
        </Typography>
        
        {renderToolGrid(favorites)}
      </Box>
    );
  };
  
  const renderRecentTools = () => {
    const recent = tools.filter(tool => recentTools.includes(tool.id));
    
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Recently Used Tools
        </Typography>
        
        {renderToolList(recent)}
      </Box>
    );
  };
  
  const renderToolDialog = () => {
    if (!selectedTool) return null;
    
    return (
      <Dialog 
        open={isToolDialogOpen} 
        onClose={handleCloseToolDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {selectedTool.icon ? (
              <selectedTool.icon sx={{ mr: 1, color: isToolInstalled(selectedTool.id) ? 'primary.main' : 'text.secondary' }} />
            ) : (
              <ExtensionIcon sx={{ mr: 1, color: isToolInstalled(selectedTool.id) ? 'primary.main' : 'text.secondary' }} />
            )}
            {selectedTool.name}
            <Typography variant="caption" sx={{ ml: 1, color: 'text.secondary' }}>
              v{selectedTool.version}
            </Typography>
            
            <Box sx={{ ml: 'auto' }}>
              <IconButton 
                onClick={() => handleToolFavorite(selectedTool, !isToolFavorite(selectedTool.id))}
              >
                {isToolFavorite(selectedTool.id) ? (
                  <StarIcon color="warning" />
                ) : (
                  <StarBorderIcon />
                )}
              </IconButton>
            </Box>
          </Box>
        </DialogTitle>
        
        <DialogContent dividers>
          {toolDialogMode === 'view' && (
            <Box>
              <Typography variant="body1" paragraph>
                {selectedTool.description}
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Details
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" component="div">
                      <strong>Category:</strong> {selectedTool.category}
                    </Typography>
                    <Typography variant="body2" component="div">
                      <strong>Author:</strong> {selectedTool.author || 'Lumina AI'}
                    </Typography>
                    <Typography variant="body2" component="div">
                      <strong>License:</strong> {selectedTool.license || 'MIT'}
                    </Typography>
                    <Typography variant="body2" component="div">
                      <strong>Last Updated:</strong> {selectedTool.lastUpdated || 'Unknown'}
                    </Typography>
                  </Box>
                  
                  {selectedTool.tags && selectedTool.tags.length > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        Tags
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {selectedTool.tags.map(tag => (
                          <Chip key={tag} label={tag} size="small" />
                        ))}
                      </Box>
                    </Box>
                  )}
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" gutterBottom>
                    Capabilities
                  </Typography>
                  
                  <List dense>
                    {selectedTool.capabilities && selectedTool.capabilities.map((capability, index) => (
                      <ListItem key={index}>
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          <CheckIcon fontSize="small" color="success" />
                        </ListItemIcon>
                        <ListItemText primary={capability} />
                      </ListItem>
                    ))}
                    
                    {(!selectedTool.capabilities || selectedTool.capabilities.length === 0) && (
                      <Typography variant="body2" color="text.secondary">
                        No specific capabilities listed
                      </Typography>
                    )}
                  </List>
                  
                  {selectedTool.documentation && (
                    <Button
                      startIcon={<InfoIcon />}
                      variant="outlined"
                      size="small"
                      component="a"
                      href={selectedTool.documentation}
                      target="_blank"
                      rel="noopener noreferrer"
                      sx={{ mt: 2 }}
                    >
                      Documentation
                    </Button>
                  )}
                </Grid>
              </Grid>
              
              {selectedTool.parameters && selectedTool.parameters.length > 0 && (
                <>
                  <Divider sx={{ my: 2 }} />
                  
                  <Typography variant="subtitle1" gutterBottom>
                    Parameters
                  </Typography>
                  
                  <List>
                    {selectedTool.parameters.map((param, index) => (
                      <ListItem key={index} sx={{ py: 1 }}>
                        <ListItemText 
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              {param.name}
                              {param.required && (
                                <Typography variant="caption" color="error" sx={{ ml: 1 }}>
                                  (Required)
                                </Typography>
                              )}
                            </Box>
                          }
                          secondary={
                            <>
                              <Typography variant="body2" color="text.secondary">
                                {param.description}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                Type: {param.type} {param.default !== undefined && `• Default: ${param.default}`}
                              </Typography>
                            </>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                </>
              )}
              
              {selectedTool.examples && selectedTool.examples.length > 0 && (
                <>
                  <Divider sx={{ my: 2 }} />
                  
                  <Typography variant="subtitle1" gutterBottom>
                    Examples
                  </Typography>
                  
                  {selectedTool.examples.map((example, index) => (
                    <Box key={index} sx={{ mb: 2 }}>
                      <Typography variant="subtitle2" gutterBottom>
                        {example.title || `Example ${index + 1}`}
                      </Typography>
                      <Typography variant="body2" paragraph>
                        {example.description}
                      </Typography>
                      <Paper variant="outlined" sx={{ p: 1, bgcolor: 'background.default' }}>
                        <Typography variant="caption" component="pre" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                          {JSON.stringify(example.parameters, null, 2)}
                        </Typography>
                      </Paper>
                    </Box>
                  ))}
                </>
              )}
            </Box>
          )}
          
          {toolDialogMode === 'configure' && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Tool Configuration
              </Typography>
              
              {/* Configuration form would go here */}
              <Typography variant="body2" color="text.secondary">
                Configure settings for {selectedTool.name}
              </Typography>
              
              {/* Placeholder for configuration UI */}
              <Box sx={{ mt: 2 }}>
                <TextField
                  label="API Key"
                  fullWidth
                  margin="normal"
                  type="password"
                />
                
                <TextField
                  label="Endpoint URL"
                  fullWidth
                  margin="normal"
                />
                
                <FormControlLabel
                  control={<Switch defaultChecked />}
                  label="Enable caching"
                  sx={{ mt: 1 }}
                />
                
                <FormControlLabel
                  control={<Switch />}
                  label="Debug mode"
                  sx={{ mt: 1 }}
                />
              </Box>
            </Box>
          )}
          
          {toolDialogMode === 'run' && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Run Tool
              </Typography>
              
              <Typography variant="body2" paragraph>
                {selectedTool.description}
              </Typography>
              
              {/* Parameter inputs would go here */}
              {selectedTool.parameters && selectedTool.parameters.map((param, index) => (
                <TextField
                  key={index}
                  label={param.name}
                  fullWidth
                  margin="normal"
                  helperText={param.description}
                  required={param.required}
                  type={param.type === 'number' ? 'number' : 'text'}
                  defaultValue={param.default}
                />
              ))}
            </Box>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={handleCloseToolDialog}>
            Close
          </Button>
          
          {toolDialogMode === 'view' && isToolInstalled(selectedTool.id) && (
            <>
              <Button 
                color="primary" 
                onClick={() => {
                  setToolDialogMode('run');
                }}
                startIcon={<RunIcon />}
              >
                Run
              </Button>
              <Button 
                color="primary" 
                onClick={() => {
                  setToolDialogMode('configure');
                }}
                startIcon={<SettingsIcon />}
              >
                Configure
              </Button>
            </>
          )}
          
          {toolDialogMode === 'view' && !isToolInstalled(selectedTool.id) && (
            <Button 
              color="primary" 
              onClick={() => handleToolInstall(selectedTool)}
              startIcon={<InstallIcon />}
            >
              Install
            </Button>
          )}
          
          {toolDialogMode === 'configure' && (
            <Button 
              color="primary" 
              onClick={handleCloseToolDialog}
            >
              Save Configuration
            </Button>
          )}
          
          {toolDialogMode === 'run' && (
            <Button 
              color="primary" 
              onClick={handleCloseToolDialog}
              startIcon={<RunIcon />}
            >
              Execute
            </Button>
          )}
        </DialogActions>
      </Dialog>
    );
  };
  
  return (
    <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h2" gutterBottom>
        Tool Integration
      </Typography>
      
      {/* Search bar */}
      <Box sx={{ mb: 2 }}>
        <TextField
          fullWidth
          placeholder="Search tools..."
          value={searchQuery}
          onChange={handleSearchChange}
          InputProps={{
            startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
          }}
          size="small"
        />
      </Box>
      
      {/* Tabs */}
      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 2 }}>
        <Tab label="All Tools" icon={<ToolIcon />} iconPosition="start" />
        <Tab 
          label="Installed" 
          icon={
            <Badge badgeContent={installedTools.length} color="primary">
              <ExtensionIcon />
            </Badge>
          } 
          iconPosition="start" 
        />
        <Tab 
          label="Favorites" 
          icon={
            <Badge badgeContent={favoriteTools.length} color="primary">
              <StarIcon />
            </Badge>
          } 
          iconPosition="start" 
        />
        <Tab label="Recent" icon={<HistoryIcon />} iconPosition="start" />
      </Tabs>
      
      {/* Main content area */}
      <Box sx={{ flex: 1, overflow: 'auto', border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {activeTab === 0 && renderAllTools()}
            {activeTab === 1 && renderInstalledTools()}
            {activeTab === 2 && renderFavoriteTools()}
            {activeTab === 3 && renderRecentTools()}
          </>
        )}
      </Box>
      
      {/* Tool dialog */}
      {renderToolDialog()}
    </Paper>
  );
};

// Helper component for the dialog
const CheckIcon = ({ fontSize, color }) => (
  <svg 
    width={fontSize === 'small' ? 18 : 24} 
    height={fontSize === 'small' ? 18 : 24} 
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" 
      fill={color === 'success' ? '#4caf50' : 'currentColor'} 
    />
  </svg>
);

ToolIntegrationUI.propTypes = {
  tools: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      description: PropTypes.string.isRequired,
      category: PropTypes.string.isRequired,
      version: PropTypes.string.isRequired,
      author: PropTypes.string,
      license: PropTypes.string,
      lastUpdated: PropTypes.string,
      tags: PropTypes.arrayOf(PropTypes.string),
      capabilities: PropTypes.arrayOf(PropTypes.string),
      documentation: PropTypes.string,
      parameters: PropTypes.arrayOf(
        PropTypes.shape({
          name: PropTypes.string.isRequired,
          description: PropTypes.string,
          type: PropTypes.string.isRequired,
          required: PropTypes.bool,
          default: PropTypes.any
        })
      ),
      examples: PropTypes.arrayOf(
        PropTypes.shape({
          title: PropTypes.string,
          description: PropTypes.string,
          parameters: PropTypes.object
        })
      ),
      icon: PropTypes.elementType
    })
  ),
  categories: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired
    })
  ),
  installedTools: PropTypes.arrayOf(PropTypes.string),
  recentTools: PropTypes.arrayOf(PropTypes.string),
  favoriteTools: PropTypes.arrayOf(PropTypes.string),
  onToolSelect: PropTypes.func,
  onToolInstall: PropTypes.func,
  onToolUninstall: PropTypes.func,
  onToolFavorite: PropTypes.func,
  onToolRun: PropTypes.func,
  onToolConfigure: PropTypes.func,
  onToolCreate: PropTypes.func,
  isLoading: PropTypes.bool
};

export default ToolIntegrationUI;
