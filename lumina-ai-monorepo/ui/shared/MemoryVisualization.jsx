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
  Collapse,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Switch,
  FormControlLabel
} from '@mui/material';
import { 
  Memory as MemoryIcon,
  Folder as FolderIcon,
  FolderOpen as FolderOpenIcon,
  Description as DocumentIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Link as LinkIcon,
  Add as AddIcon,
  Refresh as RefreshIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Timeline as TimelineIcon,
  Bookmark as BookmarkIcon,
  BookmarkBorder as BookmarkBorderIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon
} from '@mui/icons-material';
import { ForceGraph2D } from 'react-force-graph';
import { useTheme } from '@mui/material/styles';

/**
 * Memory Visualization Component
 * 
 * Provides an interactive interface for exploring and navigating
 * the hierarchical memory system with multiple visualization modes.
 */
const MemoryVisualization = ({ 
  memories = [], 
  clusters = [],
  connections = [],
  onMemorySelect,
  onMemoryCreate,
  onMemoryUpdate,
  onMemoryDelete,
  onClusterCreate,
  onClusterUpdate,
  onClusterDelete,
  onConnectionCreate,
  onConnectionDelete,
  isLoading = false
}) => {
  const theme = useTheme();
  const graphRef = useRef();
  const [activeTab, setActiveTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    memoryTypes: ['episodic', 'semantic', 'procedural'],
    timeRange: [0, 100],
    importance: [0, 5],
    showArchived: false
  });
  const [showFilters, setShowFilters] = useState(false);
  const [expandedClusters, setExpandedClusters] = useState({});
  const [selectedMemory, setSelectedMemory] = useState(null);
  const [selectedCluster, setSelectedCluster] = useState(null);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [highlightNodes, setHighlightNodes] = useState(new Set());
  const [highlightLinks, setHighlightLinks] = useState(new Set());
  const [hoverNode, setHoverNode] = useState(null);
  
  // Prepare graph data when memories, clusters, or connections change
  useEffect(() => {
    if (activeTab === 1) { // Graph view
      const nodes = [
        ...memories.map(memory => ({
          id: memory.id,
          name: memory.title,
          type: 'memory',
          memoryType: memory.type,
          val: memory.importance || 1,
          color: memory.type === 'episodic' 
            ? theme.palette.primary.main 
            : memory.type === 'semantic' 
              ? theme.palette.secondary.main 
              : theme.palette.warning.main
        })),
        ...clusters.map(cluster => ({
          id: cluster.id,
          name: cluster.name,
          type: 'cluster',
          val: 2,
          color: theme.palette.info.main
        }))
      ];
      
      const links = connections.map(conn => ({
        source: conn.sourceId,
        target: conn.targetId,
        value: conn.strength || 1,
        type: conn.type || 'related'
      }));
      
      setGraphData({ nodes, links });
    }
  }, [memories, clusters, connections, activeTab, theme]);
  
  // Filter memories based on search query and filters
  const filteredMemories = memories.filter(memory => {
    // Search query filter
    if (searchQuery && !memory.title.toLowerCase().includes(searchQuery.toLowerCase()) && 
        !memory.content.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    
    // Memory type filter
    if (!filters.memoryTypes.includes(memory.type)) {
      return false;
    }
    
    // Importance filter
    if (memory.importance < filters.importance[0] || memory.importance > filters.importance[1]) {
      return false;
    }
    
    // Archived filter
    if (memory.archived && !filters.showArchived) {
      return false;
    }
    
    return true;
  });
  
  // Filter clusters based on search query
  const filteredClusters = clusters.filter(cluster => {
    if (searchQuery && !cluster.name.toLowerCase().includes(searchQuery.toLowerCase())) {
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
  
  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };
  
  const toggleClusterExpansion = (clusterId) => {
    setExpandedClusters(prev => ({
      ...prev,
      [clusterId]: !prev[clusterId]
    }));
  };
  
  const handleMemorySelect = (memory) => {
    setSelectedMemory(memory);
    if (onMemorySelect) {
      onMemorySelect(memory);
    }
  };
  
  const handleClusterSelect = (cluster) => {
    setSelectedCluster(cluster);
  };
  
  const handleNodeHover = (node) => {
    if (!node) {
      setHoverNode(null);
      setHighlightNodes(new Set());
      setHighlightLinks(new Set());
      return;
    }
    
    setHoverNode(node);
    
    // Highlight connected nodes and links
    const connectedNodes = new Set();
    const connectedLinks = new Set();
    
    connectedNodes.add(node);
    
    graphData.links.forEach(link => {
      if (link.source.id === node.id || link.target.id === node.id) {
        connectedLinks.add(link);
        connectedNodes.add(link.source.id === node.id ? link.target : link.source);
      }
    });
    
    setHighlightNodes(connectedNodes);
    setHighlightLinks(connectedLinks);
  };
  
  const handleNodeClick = (node) => {
    if (node.type === 'memory') {
      const memory = memories.find(m => m.id === node.id);
      if (memory) {
        handleMemorySelect(memory);
      }
    } else if (node.type === 'cluster') {
      const cluster = clusters.find(c => c.id === node.id);
      if (cluster) {
        handleClusterSelect(cluster);
      }
    }
  };
  
  const renderHierarchicalView = () => {
    return (
      <Box sx={{ display: 'flex', height: '100%' }}>
        {/* Left panel - Clusters and Memories Tree */}
        <Box sx={{ width: 300, borderRight: '1px solid', borderColor: 'divider', p: 2, overflowY: 'auto' }}>
          <Typography variant="h6" gutterBottom>
            Memory Clusters
          </Typography>
          
          <List>
            {filteredClusters.map(cluster => (
              <React.Fragment key={cluster.id}>
                <ListItem 
                  button 
                  onClick={() => toggleClusterExpansion(cluster.id)}
                  selected={selectedCluster?.id === cluster.id}
                  sx={{ 
                    borderRadius: 1,
                    mb: 0.5
                  }}
                >
                  <ListItemIcon>
                    {expandedClusters[cluster.id] ? <FolderOpenIcon /> : <FolderIcon />}
                  </ListItemIcon>
                  <ListItemText primary={cluster.name} />
                  {expandedClusters[cluster.id] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                </ListItem>
                
                <Collapse in={expandedClusters[cluster.id]} timeout="auto" unmountOnExit>
                  <List component="div" disablePadding>
                    {filteredMemories
                      .filter(memory => memory.clusterId === cluster.id)
                      .map(memory => (
                        <ListItem 
                          key={memory.id} 
                          button 
                          onClick={() => handleMemorySelect(memory)}
                          selected={selectedMemory?.id === memory.id}
                          sx={{ 
                            pl: 4,
                            borderRadius: 1,
                            mb: 0.5
                          }}
                        >
                          <ListItemIcon>
                            <DocumentIcon color={
                              memory.type === 'episodic' 
                                ? 'primary' 
                                : memory.type === 'semantic' 
                                  ? 'secondary' 
                                  : 'warning'
                            } />
                          </ListItemIcon>
                          <ListItemText 
                            primary={memory.title} 
                            secondary={`${memory.type} • ${new Date(memory.createdAt).toLocaleDateString()}`}
                          />
                        </ListItem>
                      ))}
                  </List>
                </Collapse>
              </React.Fragment>
            ))}
          </List>
          
          <Divider sx={{ my: 2 }} />
          
          <Typography variant="h6" gutterBottom>
            Uncategorized Memories
          </Typography>
          
          <List>
            {filteredMemories
              .filter(memory => !memory.clusterId)
              .map(memory => (
                <ListItem 
                  key={memory.id} 
                  button 
                  onClick={() => handleMemorySelect(memory)}
                  selected={selectedMemory?.id === memory.id}
                  sx={{ 
                    borderRadius: 1,
                    mb: 0.5
                  }}
                >
                  <ListItemIcon>
                    <DocumentIcon color={
                      memory.type === 'episodic' 
                        ? 'primary' 
                        : memory.type === 'semantic' 
                          ? 'secondary' 
                          : 'warning'
                    } />
                  </ListItemIcon>
                  <ListItemText 
                    primary={memory.title} 
                    secondary={`${memory.type} • ${new Date(memory.createdAt).toLocaleDateString()}`}
                  />
                </ListItem>
              ))}
          </List>
        </Box>
        
        {/* Right panel - Memory Details */}
        <Box sx={{ flex: 1, p: 2, overflowY: 'auto' }}>
          {selectedMemory ? (
            <Card>
              <CardHeader
                title={selectedMemory.title}
                subheader={`${selectedMemory.type} memory • Created: ${new Date(selectedMemory.createdAt).toLocaleString()}`}
                action={
                  <Box>
                    <Tooltip title="Edit Memory">
                      <IconButton onClick={() => onMemoryUpdate(selectedMemory)}>
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete Memory">
                      <IconButton onClick={() => onMemoryDelete(selectedMemory.id)}>
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                }
              />
              <CardContent>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                    {selectedMemory.content}
                  </Typography>
                </Box>
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="subtitle2" gutterBottom>
                  Metadata
                </Typography>
                
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Importance: {selectedMemory.importance}/5
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Last Accessed: {new Date(selectedMemory.lastAccessed || selectedMemory.createdAt).toLocaleString()}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Access Count: {selectedMemory.accessCount || 0}
                    </Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">
                      Status: {selectedMemory.archived ? 'Archived' : 'Active'}
                    </Typography>
                  </Grid>
                </Grid>
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="subtitle2" gutterBottom>
                  Connected Memories
                </Typography>
                
                {connections
                  .filter(conn => conn.sourceId === selectedMemory.id || conn.targetId === selectedMemory.id)
                  .map(conn => {
                    const connectedMemoryId = conn.sourceId === selectedMemory.id ? conn.targetId : conn.sourceId;
                    const connectedMemory = memories.find(m => m.id === connectedMemoryId);
                    
                    if (!connectedMemory) return null;
                    
                    return (
                      <Chip
                        key={conn.id}
                        icon={<LinkIcon />}
                        label={connectedMemory.title}
                        variant="outlined"
                        onClick={() => handleMemorySelect(connectedMemory)}
                        sx={{ m: 0.5 }}
                      />
                    );
                  })}
                
                {connections.filter(conn => conn.sourceId === selectedMemory.id || conn.targetId === selectedMemory.id).length === 0 && (
                  <Typography variant="body2" color="text.secondary">
                    No connected memories
                  </Typography>
                )}
              </CardContent>
              <CardActions>
                <Button 
                  size="small" 
                  startIcon={selectedMemory.bookmarked ? <BookmarkIcon /> : <BookmarkBorderIcon />}
                  onClick={() => onMemoryUpdate({ ...selectedMemory, bookmarked: !selectedMemory.bookmarked })}
                >
                  {selectedMemory.bookmarked ? 'Bookmarked' : 'Bookmark'}
                </Button>
                <Button 
                  size="small" 
                  startIcon={<StarIcon />}
                  onClick={() => onMemoryUpdate({ 
                    ...selectedMemory, 
                    importance: Math.min(5, (selectedMemory.importance || 0) + 1) 
                  })}
                >
                  Increase Importance
                </Button>
                <Button 
                  size="small" 
                  startIcon={selectedMemory.archived ? <VisibilityIcon /> : <VisibilityOffIcon />}
                  onClick={() => onMemoryUpdate({ ...selectedMemory, archived: !selectedMemory.archived })}
                >
                  {selectedMemory.archived ? 'Unarchive' : 'Archive'}
                </Button>
              </CardActions>
            </Card>
          ) : selectedCluster ? (
            <Card>
              <CardHeader
                title={selectedCluster.name}
                subheader={`Cluster • Contains ${memories.filter(m => m.clusterId === selectedCluster.id).length} memories`}
                action={
                  <Box>
                    <Tooltip title="Edit Cluster">
                      <IconButton onClick={() => onClusterUpdate(selectedCluster)}>
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete Cluster">
                      <IconButton onClick={() => onClusterDelete(selectedCluster.id)}>
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                }
              />
              <CardContent>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {selectedCluster.description}
                </Typography>
                
                <Divider sx={{ my: 2 }} />
                
                <Typography variant="subtitle2" gutterBottom>
                  Memories in this Cluster
                </Typography>
                
                <List>
                  {memories
                    .filter(memory => memory.clusterId === selectedCluster.id)
                    .map(memory => (
                      <ListItem 
                        key={memory.id} 
                        button 
                        onClick={() => handleMemorySelect(memory)}
                      >
                        <ListItemIcon>
                          <DocumentIcon color={
                            memory.type === 'episodic' 
                              ? 'primary' 
                              : memory.type === 'semantic' 
                                ? 'secondary' 
                                : 'warning'
                          } />
                        </ListItemIcon>
                        <ListItemText 
                          primary={memory.title} 
                          secondary={`${memory.type} • ${new Date(memory.createdAt).toLocaleDateString()}`}
                        />
                      </ListItem>
                    ))}
                </List>
              </CardContent>
            </Card>
          ) : (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
              <MemoryIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                Select a memory or cluster to view details
              </Typography>
              <Typography variant="body2" color="text.secondary" align="center" sx={{ maxWidth: 400, mb: 3 }}>
                Browse through the hierarchical memory structure on the left panel or use the graph view to explore memory connections.
              </Typography>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button 
                  variant="outlined" 
                  startIcon={<AddIcon />}
                  onClick={() => onMemoryCreate()}
                >
                  Create Memory
                </Button>
                <Button 
                  variant="outlined" 
                  startIcon={<AddIcon />}
                  onClick={() => onClusterCreate()}
                >
                  Create Cluster
                </Button>
              </Box>
            </Box>
          )}
        </Box>
      </Box>
    );
  };
  
  const renderGraphView = () => {
    return (
      <Box sx={{ position: 'relative', height: '100%' }}>
        {graphData.nodes.length > 0 ? (
          <ForceGraph2D
            ref={graphRef}
            graphData={graphData}
            nodeLabel={node => `${node.name} (${node.type})`}
            nodeColor={node => {
              if (highlightNodes.size > 0) {
                return highlightNodes.has(node) ? node.color : theme.palette.grey[300];
              }
              return node.color;
            }}
            nodeRelSize={6}
            linkWidth={link => highlightLinks.has(link) ? 3 : 1}
            linkColor={link => {
              if (highlightLinks.size > 0) {
                return highlightLinks.has(link) ? theme.palette.primary.main : theme.palette.grey[300];
              }
              return theme.palette.grey[400];
            }}
            onNodeHover={handleNodeHover}
            onNodeClick={handleNodeClick}
            cooldownTicks={100}
            nodeCanvasObject={(node, ctx, globalScale) => {
              const label = node.name;
              const fontSize = 12/globalScale;
              ctx.font = `${fontSize}px Sans-Serif`;
              const textWidth = ctx.measureText(label).width;
              const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);
              
              // Draw node
              ctx.beginPath();
              ctx.arc(node.x, node.y, node.val * 3, 0, 2 * Math.PI, false);
              ctx.fillStyle = node.color;
              ctx.fill();
              
              // Draw label if zoomed in enough
              if (globalScale >= 0.8) {
                ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
                ctx.fillRect(
                  node.x - bckgDimensions[0] / 2,
                  node.y + node.val * 3 + 2,
                  bckgDimensions[0],
                  bckgDimensions[1]
                );
                
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillStyle = theme.palette.text.primary;
                ctx.fillText(
                  label,
                  node.x,
                  node.y + node.val * 3 + 2 + bckgDimensions[1] / 2
                );
              }
            }}
          />
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
            <Typography variant="h6" color="text.secondary">
              No memory data to visualize
            </Typography>
          </Box>
        )}
        
        {/* Hover tooltip */}
        {hoverNode && (
          <Box
            sx={{
              position: 'absolute',
              top: 10,
              right: 10,
              p: 2,
              bgcolor: 'background.paper',
              borderRadius: 1,
              boxShadow: 3,
              maxWidth: 300
            }}
          >
            <Typography variant="subtitle2">
              {hoverNode.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Type: {hoverNode.type === 'memory' ? `${hoverNode.memoryType} memory` : 'Cluster'}
            </Typography>
            {hoverNode.type === 'memory' && (
              <Typography variant="body2" color="text.secondary">
                Connections: {connections.filter(c => c.sourceId === hoverNode.id || c.targetId === hoverNode.id).length}
              </Typography>
            )}
          </Box>
        )}
        
        {/* Controls */}
        <Box
          sx={{
            position: 'absolute',
            bottom: 20,
            right: 20,
            display: 'flex',
            flexDirection: 'column',
            gap: 1
          }}
        >
          <Tooltip title="Center Graph">
            <IconButton 
              color="primary" 
              sx={{ bgcolor: 'background.paper', boxShadow: 2 }}
              onClick={() => graphRef.current && graphRef.current.zoomToFit(400)}
            >
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
    );
  };
  
  const renderTimelineView = () => {
    // Group memories by date
    const groupedMemories = {};
    
    filteredMemories.forEach(memory => {
      const date = new Date(memory.createdAt).toLocaleDateString();
      if (!groupedMemories[date]) {
        groupedMemories[date] = [];
      }
      groupedMemories[date].push(memory);
    });
    
    // Sort dates in descending order
    const sortedDates = Object.keys(groupedMemories).sort((a, b) => {
      return new Date(b) - new Date(a);
    });
    
    return (
      <Box sx={{ p: 2, height: '100%', overflowY: 'auto' }}>
        <Typography variant="h6" gutterBottom>
          Memory Timeline
        </Typography>
        
        {sortedDates.map(date => (
          <Box key={date} sx={{ mb: 4 }}>
            <Box 
              sx={{ 
                display: 'flex', 
                alignItems: 'center', 
                mb: 2,
                position: 'sticky',
                top: 0,
                bgcolor: 'background.paper',
                zIndex: 1,
                py: 1
              }}
            >
              <TimelineIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">
                {date}
              </Typography>
            </Box>
            
            {groupedMemories[date].map(memory => (
              <Card 
                key={memory.id} 
                sx={{ 
                  mb: 2, 
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  '&:hover': {
                    boxShadow: 3
                  },
                  borderLeft: '4px solid',
                  borderColor: memory.type === 'episodic' 
                    ? 'primary.main' 
                    : memory.type === 'semantic' 
                      ? 'secondary.main' 
                      : 'warning.main'
                }}
                onClick={() => handleMemorySelect(memory)}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <Typography variant="subtitle1" gutterBottom>
                      {memory.title}
                    </Typography>
                    <Chip 
                      label={memory.type} 
                      size="small" 
                      color={
                        memory.type === 'episodic' 
                          ? 'primary' 
                          : memory.type === 'semantic' 
                            ? 'secondary' 
                            : 'warning'
                      }
                    />
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ 
                    mb: 1,
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis'
                  }}>
                    {memory.content}
                  </Typography>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                    <Typography variant="caption" color="text.secondary">
                      {new Date(memory.createdAt).toLocaleTimeString()}
                    </Typography>
                    
                    <Box>
                      {memory.bookmarked && (
                        <Tooltip title="Bookmarked">
                          <BookmarkIcon fontSize="small" color="primary" sx={{ mr: 1 }} />
                        </Tooltip>
                      )}
                      
                      {Array.from({ length: Math.min(5, Math.max(1, memory.importance || 1)) }).map((_, i) => (
                        <StarIcon key={i} fontSize="small" color="warning" sx={{ fontSize: 16 }} />
                      ))}
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Box>
        ))}
        
        {sortedDates.length === 0 && (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 300 }}>
            <Typography variant="body1" color="text.secondary">
              No memories found matching your filters
            </Typography>
          </Box>
        )}
      </Box>
    );
  };
  
  return (
    <Paper sx={{ p: 3, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h2" gutterBottom>
        Memory System
      </Typography>
      
      {/* Search and filters */}
      <Box sx={{ mb: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <TextField
            fullWidth
            placeholder="Search memories..."
            value={searchQuery}
            onChange={handleSearchChange}
            InputProps={{
              startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
            }}
            size="small"
          />
          
          <Button
            variant="outlined"
            startIcon={<FilterIcon />}
            onClick={() => setShowFilters(!showFilters)}
          >
            Filters
          </Button>
        </Box>
        
        <Collapse in={showFilters}>
          <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Memory Types
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={filters.memoryTypes.includes('episodic')}
                    onChange={(e) => {
                      if (e.target.checked) {
                        handleFilterChange('memoryTypes', [...filters.memoryTypes, 'episodic']);
                      } else {
                        handleFilterChange('memoryTypes', filters.memoryTypes.filter(t => t !== 'episodic'));
                      }
                    }}
                    color="primary"
                  />
                }
                label="Episodic"
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={filters.memoryTypes.includes('semantic')}
                    onChange={(e) => {
                      if (e.target.checked) {
                        handleFilterChange('memoryTypes', [...filters.memoryTypes, 'semantic']);
                      } else {
                        handleFilterChange('memoryTypes', filters.memoryTypes.filter(t => t !== 'semantic'));
                      }
                    }}
                    color="secondary"
                  />
                }
                label="Semantic"
              />
              
              <FormControlLabel
                control={
                  <Switch
                    checked={filters.memoryTypes.includes('procedural')}
                    onChange={(e) => {
                      if (e.target.checked) {
                        handleFilterChange('memoryTypes', [...filters.memoryTypes, 'procedural']);
                      } else {
                        handleFilterChange('memoryTypes', filters.memoryTypes.filter(t => t !== 'procedural'));
                      }
                    }}
                    color="warning"
                  />
                }
                label="Procedural"
              />
            </Box>
            
            <Typography variant="subtitle2" gutterBottom>
              Importance
            </Typography>
            
            <Box sx={{ px: 2, mb: 2 }}>
              <Slider
                value={filters.importance}
                onChange={(e, newValue) => handleFilterChange('importance', newValue)}
                valueLabelDisplay="auto"
                min={0}
                max={5}
                marks
              />
            </Box>
            
            <FormControlLabel
              control={
                <Switch
                  checked={filters.showArchived}
                  onChange={(e) => handleFilterChange('showArchived', e.target.checked)}
                />
              }
              label="Show archived memories"
            />
          </Paper>
        </Collapse>
      </Box>
      
      {/* Tabs */}
      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 2 }}>
        <Tab label="Hierarchical" icon={<FolderIcon />} iconPosition="start" />
        <Tab label="Graph" icon={<LinkIcon />} iconPosition="start" />
        <Tab label="Timeline" icon={<TimelineIcon />} iconPosition="start" />
      </Tabs>
      
      {/* Main content area */}
      <Box sx={{ flex: 1, overflow: 'hidden', border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <CircularProgress />
          </Box>
        ) : (
          <>
            {activeTab === 0 && renderHierarchicalView()}
            {activeTab === 1 && renderGraphView()}
            {activeTab === 2 && renderTimelineView()}
          </>
        )}
      </Box>
    </Paper>
  );
};

MemoryVisualization.propTypes = {
  memories: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      title: PropTypes.string.isRequired,
      content: PropTypes.string.isRequired,
      type: PropTypes.oneOf(['episodic', 'semantic', 'procedural']).isRequired,
      clusterId: PropTypes.string,
      importance: PropTypes.number,
      createdAt: PropTypes.string.isRequired,
      lastAccessed: PropTypes.string,
      accessCount: PropTypes.number,
      archived: PropTypes.bool,
      bookmarked: PropTypes.bool
    })
  ),
  clusters: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      name: PropTypes.string.isRequired,
      description: PropTypes.string
    })
  ),
  connections: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      sourceId: PropTypes.string.isRequired,
      targetId: PropTypes.string.isRequired,
      type: PropTypes.string,
      strength: PropTypes.number
    })
  ),
  onMemorySelect: PropTypes.func,
  onMemoryCreate: PropTypes.func,
  onMemoryUpdate: PropTypes.func,
  onMemoryDelete: PropTypes.func,
  onClusterCreate: PropTypes.func,
  onClusterUpdate: PropTypes.func,
  onClusterDelete: PropTypes.func,
  onConnectionCreate: PropTypes.func,
  onConnectionDelete: PropTypes.func,
  isLoading: PropTypes.bool
};

export default MemoryVisualization;
