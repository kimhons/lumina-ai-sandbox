import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { 
  Box, 
  Typography, 
  Button, 
  TextField, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  FormHelperText,
  Divider,
  Paper,
  Switch,
  FormControlLabel,
  Slider,
  Chip,
  Stack
} from '@mui/material';
import { 
  PlayArrow as ExecuteIcon,
  Close as CancelIcon
} from '@mui/icons-material';

/**
 * Tool Selector Component
 * 
 * Provides an interface for configuring and executing tools
 * with parameter validation and execution controls.
 */
const ToolSelector = ({ tool, onExecute, onCancel }) => {
  const [params, setParams] = useState({});
  const [errors, setErrors] = useState({});
  
  // Initialize default values for parameters
  React.useEffect(() => {
    if (tool && tool.parameters) {
      const defaultParams = {};
      const paramErrors = {};
      
      Object.entries(tool.parameters).forEach(([key, param]) => {
        if (param.default !== undefined) {
          defaultParams[key] = param.default;
        } else if (param.type === 'boolean') {
          defaultParams[key] = false;
        } else if (param.type === 'number' || param.type === 'integer') {
          defaultParams[key] = param.minimum || 0;
        } else if (param.type === 'string' && param.enum) {
          defaultParams[key] = param.enum[0];
        } else if (param.type === 'array') {
          defaultParams[key] = [];
        } else if (param.type === 'object') {
          defaultParams[key] = {};
        } else {
          defaultParams[key] = '';
        }
        
        // Check if required but no default
        if (param.required && param.default === undefined) {
          paramErrors[key] = 'This field is required';
        }
      });
      
      setParams(defaultParams);
      setErrors(paramErrors);
    }
  }, [tool]);
  
  const handleParamChange = (key, value) => {
    setParams(prev => ({
      ...prev,
      [key]: value
    }));
    
    // Validate the parameter
    validateParam(key, value);
  };
  
  const validateParam = (key, value) => {
    const param = tool.parameters[key];
    let error = '';
    
    if (param.required && (value === undefined || value === null || value === '')) {
      error = 'This field is required';
    } else if (param.type === 'string' && param.minLength && value.length < param.minLength) {
      error = `Minimum length is ${param.minLength} characters`;
    } else if (param.type === 'string' && param.maxLength && value.length > param.maxLength) {
      error = `Maximum length is ${param.maxLength} characters`;
    } else if ((param.type === 'number' || param.type === 'integer') && param.minimum !== undefined && value < param.minimum) {
      error = `Minimum value is ${param.minimum}`;
    } else if ((param.type === 'number' || param.type === 'integer') && param.maximum !== undefined && value > param.maximum) {
      error = `Maximum value is ${param.maximum}`;
    } else if (param.type === 'array' && param.minItems && value.length < param.minItems) {
      error = `Minimum ${param.minItems} items required`;
    } else if (param.type === 'array' && param.maxItems && value.length > param.maxItems) {
      error = `Maximum ${param.maxItems} items allowed`;
    }
    
    setErrors(prev => ({
      ...prev,
      [key]: error
    }));
    
    return !error;
  };
  
  const validateAllParams = () => {
    let isValid = true;
    const newErrors = {};
    
    Object.entries(tool.parameters).forEach(([key, param]) => {
      const value = params[key];
      
      if (param.required && (value === undefined || value === null || value === '')) {
        newErrors[key] = 'This field is required';
        isValid = false;
      } else if (param.type === 'string' && param.minLength && value.length < param.minLength) {
        newErrors[key] = `Minimum length is ${param.minLength} characters`;
        isValid = false;
      } else if (param.type === 'string' && param.maxLength && value.length > param.maxLength) {
        newErrors[key] = `Maximum length is ${param.maxLength} characters`;
        isValid = false;
      } else if ((param.type === 'number' || param.type === 'integer') && param.minimum !== undefined && value < param.minimum) {
        newErrors[key] = `Minimum value is ${param.minimum}`;
        isValid = false;
      } else if ((param.type === 'number' || param.type === 'integer') && param.maximum !== undefined && value > param.maximum) {
        newErrors[key] = `Maximum value is ${param.maximum}`;
        isValid = false;
      } else if (param.type === 'array' && param.minItems && value.length < param.minItems) {
        newErrors[key] = `Minimum ${param.minItems} items required`;
        isValid = false;
      } else if (param.type === 'array' && param.maxItems && value.length > param.maxItems) {
        newErrors[key] = `Maximum ${param.maxItems} items allowed`;
        isValid = false;
      } else {
        newErrors[key] = '';
      }
    });
    
    setErrors(newErrors);
    return isValid;
  };
  
  const handleExecute = () => {
    if (validateAllParams()) {
      onExecute(tool.id, params);
    }
  };
  
  // Render different input types based on parameter type
  const renderParamInput = (key, param) => {
    switch (param.type) {
      case 'string':
        if (param.enum) {
          return (
            <FormControl 
              fullWidth 
              margin="normal" 
              error={!!errors[key]}
              required={param.required}
            >
              <InputLabel id={`${key}-label`}>{param.title || key}</InputLabel>
              <Select
                labelId={`${key}-label`}
                value={params[key] || ''}
                label={param.title || key}
                onChange={(e) => handleParamChange(key, e.target.value)}
              >
                {param.enum.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </Select>
              {param.description && (
                <FormHelperText>{errors[key] || param.description}</FormHelperText>
              )}
            </FormControl>
          );
        } else if (param.format === 'textarea') {
          return (
            <TextField
              fullWidth
              margin="normal"
              label={param.title || key}
              multiline
              rows={4}
              value={params[key] || ''}
              onChange={(e) => handleParamChange(key, e.target.value)}
              error={!!errors[key]}
              helperText={errors[key] || param.description}
              required={param.required}
            />
          );
        } else {
          return (
            <TextField
              fullWidth
              margin="normal"
              label={param.title || key}
              value={params[key] || ''}
              onChange={(e) => handleParamChange(key, e.target.value)}
              error={!!errors[key]}
              helperText={errors[key] || param.description}
              required={param.required}
              type={param.format === 'password' ? 'password' : 'text'}
            />
          );
        }
        
      case 'number':
      case 'integer':
        if (param.minimum !== undefined && param.maximum !== undefined) {
          return (
            <Box sx={{ width: '100%', mt: 3, mb: 2 }}>
              <Typography id={`${key}-slider-label`} gutterBottom>
                {param.title || key}{param.required ? ' *' : ''}
              </Typography>
              <Slider
                value={params[key] || param.minimum}
                onChange={(e, newValue) => handleParamChange(key, newValue)}
                aria-labelledby={`${key}-slider-label`}
                valueLabelDisplay="auto"
                step={param.type === 'integer' ? 1 : (param.step || 0.1)}
                marks
                min={param.minimum}
                max={param.maximum}
              />
              {(param.description || errors[key]) && (
                <FormHelperText error={!!errors[key]}>
                  {errors[key] || param.description}
                </FormHelperText>
              )}
            </Box>
          );
        } else {
          return (
            <TextField
              fullWidth
              margin="normal"
              label={param.title || key}
              value={params[key] || ''}
              onChange={(e) => {
                const value = param.type === 'integer' 
                  ? parseInt(e.target.value, 10) 
                  : parseFloat(e.target.value);
                handleParamChange(key, isNaN(value) ? '' : value);
              }}
              error={!!errors[key]}
              helperText={errors[key] || param.description}
              required={param.required}
              type="number"
              inputProps={{
                step: param.type === 'integer' ? 1 : (param.step || 0.1),
                min: param.minimum,
                max: param.maximum
              }}
            />
          );
        }
        
      case 'boolean':
        return (
          <FormControlLabel
            control={
              <Switch
                checked={!!params[key]}
                onChange={(e) => handleParamChange(key, e.target.checked)}
                color="primary"
              />
            }
            label={
              <Box>
                <Typography variant="body1">
                  {param.title || key}{param.required ? ' *' : ''}
                </Typography>
                {param.description && (
                  <Typography variant="caption" color="text.secondary">
                    {param.description}
                  </Typography>
                )}
              </Box>
            }
            sx={{ mt: 2, mb: 1 }}
          />
        );
        
      case 'array':
        // Simple string array with chips
        return (
          <Box sx={{ mt: 2, mb: 1 }}>
            <Typography variant="body1" gutterBottom>
              {param.title || key}{param.required ? ' *' : ''}
            </Typography>
            {param.description && (
              <Typography variant="caption" color="text.secondary" paragraph>
                {param.description}
              </Typography>
            )}
            
            <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 1 }}>
              {(params[key] || []).map((item, index) => (
                <Chip
                  key={index}
                  label={item}
                  onDelete={() => {
                    const newArray = [...params[key]];
                    newArray.splice(index, 1);
                    handleParamChange(key, newArray);
                  }}
                />
              ))}
            </Stack>
            
            <Box sx={{ display: 'flex', mt: 1 }}>
              <TextField
                size="small"
                placeholder="Add item"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && e.target.value) {
                    e.preventDefault();
                    const newArray = [...(params[key] || []), e.target.value];
                    handleParamChange(key, newArray);
                    e.target.value = '';
                  }
                }}
              />
            </Box>
            
            {errors[key] && (
              <FormHelperText error>{errors[key]}</FormHelperText>
            )}
          </Box>
        );
        
      default:
        return (
          <TextField
            fullWidth
            margin="normal"
            label={param.title || key}
            value={params[key] || ''}
            onChange={(e) => handleParamChange(key, e.target.value)}
            error={!!errors[key]}
            helperText={errors[key] || param.description}
            required={param.required}
          />
        );
    }
  };
  
  if (!tool) {
    return null;
  }
  
  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        {tool.name}
      </Typography>
      
      {tool.description && (
        <Typography variant="body2" color="text.secondary" paragraph>
          {tool.description}
        </Typography>
      )}
      
      <Divider sx={{ my: 2 }} />
      
      <Typography variant="subtitle1" gutterBottom>
        Parameters
      </Typography>
      
      <Box sx={{ mt: 2 }}>
        {Object.entries(tool.parameters || {}).map(([key, param]) => (
          <Box key={key}>
            {renderParamInput(key, param)}
          </Box>
        ))}
      </Box>
      
      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
        <Button
          variant="outlined"
          color="inherit"
          onClick={onCancel}
          startIcon={<CancelIcon />}
        >
          Cancel
        </Button>
        <Button
          variant="contained"
          color="primary"
          onClick={handleExecute}
          startIcon={<ExecuteIcon />}
          disabled={Object.values(errors).some(error => !!error)}
        >
          Execute
        </Button>
      </Box>
    </Paper>
  );
};

ToolSelector.propTypes = {
  tool: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    description: PropTypes.string,
    parameters: PropTypes.object
  }),
  onExecute: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired
};

export default ToolSelector;
