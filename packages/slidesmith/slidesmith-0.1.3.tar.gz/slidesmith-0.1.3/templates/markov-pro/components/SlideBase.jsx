import React from 'react';

/**
 * SlideBase - Base container component for all slides
 * 
 * Provides consistent dimensions (1920x1080), margins, and layout structure
 * for all slides in the presentation.
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Content to render inside the slide
 * @param {string} props.className - Additional CSS classes
 * @param {string} props.background - Background color or gradient
 */
export const SlideBase = ({ 
  children, 
  className = '', 
  background = 'bg-white' 
}) => {
  return (
    <div 
      className={`w-full min-h-screen flex flex-col items-start justify-between ${background} ${className}`}
      style={{ 
        width: '1920px', 
        minHeight: '1080px', 
        fontFamily: "'Montserrat', sans-serif" 
      }}
    >
      {children}
    </div>
  );
};

export default SlideBase;