import React, { useRef } from 'react';
import PropTypes from 'prop-types';
import { Box, Button, CircularProgress } from '@mui/material';
import { CloudUpload as CloudUploadIcon } from '@mui/icons-material';

/**
 * File Uploader Component
 * 
 * Provides a hidden file input with a reference that can be
 * triggered by parent components.
 */
const FileUploader = React.forwardRef(({ onUpload, multiple, accept, maxSize = 10485760 }, ref) => {
  const handleFileChange = (event) => {
    const files = event.target.files;
    
    if (!files || files.length === 0) {
      return;
    }
    
    // Check file size if maxSize is provided
    if (maxSize) {
      const oversizedFiles = Array.from(files).filter(file => file.size > maxSize);
      
      if (oversizedFiles.length > 0) {
        alert(`The following files exceed the maximum size of ${maxSize / 1048576}MB: ${oversizedFiles.map(f => f.name).join(', ')}`);
        return;
      }
    }
    
    // Call the onUpload callback with the files
    onUpload(files);
    
    // Reset the input value to allow uploading the same file again
    event.target.value = '';
  };
  
  return (
    <input
      type="file"
      ref={ref}
      onChange={handleFileChange}
      style={{ display: 'none' }}
      multiple={multiple}
      accept={accept}
    />
  );
});

FileUploader.displayName = 'FileUploader';

FileUploader.propTypes = {
  onUpload: PropTypes.func.isRequired,
  multiple: PropTypes.bool,
  accept: PropTypes.string,
  maxSize: PropTypes.number
};

/**
 * File Upload Button Component
 * 
 * A button that triggers file selection and handles uploads
 */
export const FileUploadButton = ({ onUpload, multiple, accept, maxSize, isUploading, buttonText = 'Upload Files' }) => {
  const fileInputRef = useRef(null);
  
  return (
    <Box>
      <Button
        variant="outlined"
        component="span"
        startIcon={isUploading ? <CircularProgress size={20} /> : <CloudUploadIcon />}
        onClick={() => fileInputRef.current.click()}
        disabled={isUploading}
      >
        {isUploading ? 'Uploading...' : buttonText}
      </Button>
      <FileUploader
        ref={fileInputRef}
        onUpload={onUpload}
        multiple={multiple}
        accept={accept}
        maxSize={maxSize}
      />
    </Box>
  );
};

FileUploadButton.propTypes = {
  onUpload: PropTypes.func.isRequired,
  multiple: PropTypes.bool,
  accept: PropTypes.string,
  maxSize: PropTypes.number,
  isUploading: PropTypes.bool,
  buttonText: PropTypes.string
};

export default FileUploader;
