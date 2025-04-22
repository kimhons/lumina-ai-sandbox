import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { 
  Box, 
  Typography, 
  Paper, 
  TextField, 
  Button, 
  IconButton,
  Tooltip,
  Divider
} from '@mui/material';
import { 
  FormatBold as BoldIcon,
  FormatItalic as ItalicIcon,
  FormatListBulleted as BulletListIcon,
  FormatListNumbered as NumberedListIcon,
  Code as CodeIcon,
  Link as LinkIcon,
  FormatQuote as QuoteIcon,
  Image as ImageIcon,
  FormatClear as ClearFormattingIcon
} from '@mui/icons-material';

/**
 * Rich Text Editor Component
 * 
 * A simplified rich text editor for message composition with
 * markdown formatting capabilities.
 */
const RichTextEditor = ({ value, onChange, onSubmit, placeholder, sx }) => {
  const editorRef = useRef(null);
  const [selectionStart, setSelectionStart] = useState(0);
  const [selectionEnd, setSelectionEnd] = useState(0);
  
  // Track selection position
  const handleSelect = (e) => {
    setSelectionStart(e.target.selectionStart);
    setSelectionEnd(e.target.selectionEnd);
  };
  
  // Apply formatting to selected text or insert at cursor position
  const applyFormatting = (prefix, suffix = '') => {
    const textarea = editorRef.current;
    if (!textarea) return;
    
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = value.substring(start, end);
    
    const beforeText = value.substring(0, start);
    const afterText = value.substring(end);
    
    const newText = beforeText + prefix + selectedText + suffix + afterText;
    onChange(newText);
    
    // Set cursor position after formatting
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(
        start + prefix.length,
        end + prefix.length
      );
    }, 0);
  };
  
  const handleBold = () => applyFormatting('**', '**');
  const handleItalic = () => applyFormatting('*', '*');
  const handleBulletList = () => applyFormatting('- ');
  const handleNumberedList = () => applyFormatting('1. ');
  const handleCode = () => applyFormatting('`', '`');
  const handleCodeBlock = () => applyFormatting('```\n', '\n```');
  const handleQuote = () => applyFormatting('> ');
  
  const handleLink = () => {
    const selectedText = value.substring(selectionStart, selectionEnd);
    const linkText = selectedText || 'link text';
    applyFormatting('[' + linkText + '](', ')');
  };
  
  const handleImage = () => {
    const selectedText = value.substring(selectionStart, selectionEnd);
    const altText = selectedText || 'image';
    applyFormatting('![' + altText + '](', ')');
  };
  
  const handleClearFormatting = () => {
    const selectedText = value.substring(selectionStart, selectionEnd);
    // Remove markdown formatting
    const cleanText = selectedText
      .replace(/\*\*(.*?)\*\*/g, '$1') // Bold
      .replace(/\*(.*?)\*/g, '$1')     // Italic
      .replace(/`(.*?)`/g, '$1')       // Inline code
      .replace(/```([\s\S]*?)```/g, '$1') // Code block
      .replace(/\[(.*?)\]\((.*?)\)/g, '$1') // Links
      .replace(/!\[(.*?)\]\((.*?)\)/g, '$1') // Images
      .replace(/^> (.*?)$/gm, '$1')   // Quotes
      .replace(/^- (.*?)$/gm, '$1')   // Bullet lists
      .replace(/^\d+\. (.*?)$/gm, '$1'); // Numbered lists
    
    const beforeText = value.substring(0, selectionStart);
    const afterText = value.substring(selectionEnd);
    
    const newText = beforeText + cleanText + afterText;
    onChange(newText);
  };
  
  const handleKeyDown = (e) => {
    // Submit on Ctrl+Enter or Cmd+Enter
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      onSubmit();
    }
    
    // Handle tab key to insert spaces instead of changing focus
    if (e.key === 'Tab') {
      e.preventDefault();
      const textarea = editorRef.current;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      
      const newText = value.substring(0, start) + '    ' + value.substring(end);
      onChange(newText);
      
      // Set cursor position after tab
      setTimeout(() => {
        textarea.focus();
        textarea.setSelectionRange(start + 4, start + 4);
      }, 0);
    }
  };
  
  return (
    <Box sx={{ width: '100%', ...sx }}>
      <Paper 
        variant="outlined" 
        sx={{ 
          p: 1, 
          mb: 1, 
          display: 'flex', 
          flexWrap: 'wrap', 
          gap: 0.5,
          bgcolor: 'background.paper'
        }}
      >
        <Tooltip title="Bold (Ctrl+B)">
          <IconButton size="small" onClick={handleBold}>
            <BoldIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        
        <Tooltip title="Italic (Ctrl+I)">
          <IconButton size="small" onClick={handleItalic}>
            <ItalicIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        
        <Divider orientation="vertical" flexItem />
        
        <Tooltip title="Bullet List">
          <IconButton size="small" onClick={handleBulletList}>
            <BulletListIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        
        <Tooltip title="Numbered List">
          <IconButton size="small" onClick={handleNumberedList}>
            <NumberedListIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        
        <Divider orientation="vertical" flexItem />
        
        <Tooltip title="Code">
          <IconButton size="small" onClick={handleCode}>
            <CodeIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        
        <Tooltip title="Code Block">
          <IconButton size="small" onClick={handleCodeBlock}>
            <CodeIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        
        <Divider orientation="vertical" flexItem />
        
        <Tooltip title="Link">
          <IconButton size="small" onClick={handleLink}>
            <LinkIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        
        <Tooltip title="Image">
          <IconButton size="small" onClick={handleImage}>
            <ImageIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        
        <Tooltip title="Quote">
          <IconButton size="small" onClick={handleQuote}>
            <QuoteIcon fontSize="small" />
          </IconButton>
        </Tooltip>
        
        <Box sx={{ flex: 1 }} />
        
        <Tooltip title="Clear Formatting">
          <IconButton size="small" onClick={handleClearFormatting}>
            <ClearFormattingIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Paper>
      
      <TextField
        inputRef={editorRef}
        fullWidth
        multiline
        minRows={3}
        maxRows={10}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onSelect={handleSelect}
        onKeyDown={handleKeyDown}
        variant="outlined"
        sx={{
          '& .MuiOutlinedInput-root': {
            fontFamily: 'monospace'
          }
        }}
      />
      
      <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
        Use Markdown for formatting. Press Ctrl+Enter to send.
      </Typography>
    </Box>
  );
};

RichTextEditor.propTypes = {
  value: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  sx: PropTypes.object
};

export default RichTextEditor;
