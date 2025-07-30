import React from 'react';

/**
 * Header - Top section of slides with logo and metadata
 * 
 * @param {Object} props
 * @param {string} props.logo - Logo text or component
 * @param {string} props.date - Date text
 * @param {string} props.confidentiality - Confidentiality text
 * @param {boolean} props.showLogo - Whether to show the logo
 * @param {boolean} props.showMetadata - Whether to show date/confidentiality
 */
export const Header = ({ 
  logo = 'MARKOV AI',
  date = 'June 2025',
  confidentiality = 'Confidential',
  showLogo = true,
  showMetadata = true
}) => {
  return (
    <div className="w-full pt-16 px-32">
      <div className="flex justify-between items-center">
        {showLogo && (
          <div className="w-64 h-16 flex items-center">
            <div className="bg-blue-700 text-white font-bold text-2xl py-2 px-4 rounded">
              {logo}
            </div>
          </div>
        )}
        {showMetadata && (
          <div className="w-64 h-16 flex items-center justify-end">
            <div className="border-l-4 border-blue-700 pl-4 text-gray-600">
              <div className="text-sm font-semibold">{date}</div>
              <div className="text-sm">{confidentiality}</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Header;