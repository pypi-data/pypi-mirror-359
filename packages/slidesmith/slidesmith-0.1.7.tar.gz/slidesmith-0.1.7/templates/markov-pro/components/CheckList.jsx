import React from 'react';

/**
 * CheckList - Styled checklist component with checkmarks
 * 
 * @param {Object} props
 * @param {Array<string>} props.items - List items
 * @param {string} props.iconColor - Color for check icons
 * @param {string} props.textSize - Text size class
 * @param {string} props.spacing - Spacing between items
 */
export const CheckList = ({ 
  items = [],
  iconColor = "text-green-600",
  textSize = "text-lg",
  spacing = "4",
  className = ''
}) => {
  return (
    <ul className={`space-y-${spacing} ${className}`}>
      {items.map((item, index) => (
        <li key={index} className="flex items-start">
          <i className={`fas fa-check-circle ${iconColor} mt-1 mr-3 flex-shrink-0`}></i>
          <span className={`text-gray-700 ${textSize}`}>{item}</span>
        </li>
      ))}
    </ul>
  );
};

export default CheckList;