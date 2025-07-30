import React from 'react';

/**
 * BulletList - Styled bullet list component
 * 
 * @param {Object} props
 * @param {Array<string>} props.items - List items
 * @param {string} props.icon - FontAwesome icon class for bullets
 * @param {string} props.iconColor - Color for bullet icons
 * @param {string} props.textSize - Text size class
 * @param {string} props.spacing - Spacing between items
 */
export const BulletList = ({ 
  items = [],
  icon = "fas fa-chevron-right",
  iconColor = "text-blue-600",
  textSize = "text-lg",
  spacing = "4",
  className = ''
}) => {
  return (
    <ul className={`space-y-${spacing} ${className}`}>
      {items.map((item, index) => (
        <li key={index} className="flex items-start">
          <i className={`${icon} ${iconColor} mt-1 mr-3 flex-shrink-0`}></i>
          <span className={`text-gray-700 ${textSize}`}>{item}</span>
        </li>
      ))}
    </ul>
  );
};

export default BulletList;