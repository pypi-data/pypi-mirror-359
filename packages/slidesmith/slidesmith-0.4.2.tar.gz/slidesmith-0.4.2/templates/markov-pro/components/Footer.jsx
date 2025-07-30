import React from 'react';

/**
 * Footer - Bottom section of slides with page number and tagline
 * 
 * @param {Object} props
 * @param {number} props.pageNumber - Current page number
 * @param {string} props.tagline - Footer tagline text
 * @param {boolean} props.showPageNumber - Whether to show page number
 * @param {boolean} props.showTagline - Whether to show tagline
 */
export const Footer = ({ 
  pageNumber,
  tagline = 'Transform. Automate. Scale.',
  showPageNumber = true,
  showTagline = true
}) => {
  return (
    <div className="w-full pb-8 px-32">
      <div className="flex justify-between items-center text-gray-500">
        <div className="flex items-center space-x-6">
          {showPageNumber && pageNumber && (
            <div className="text-sm font-medium">{pageNumber}</div>
          )}
          {showTagline && (
            <div className="text-sm">{tagline}</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Footer;