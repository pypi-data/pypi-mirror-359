import React from 'react';

/**
 * ImpactBox - Highlighted metric display component
 * 
 * Used for showcasing important metrics or impacts with blue background
 * 
 * @param {Object} props
 * @param {string} props.metric - Main metric value (e.g., "40%", "$2.5M")
 * @param {string} props.label - Label for the metric
 * @param {string} props.icon - FontAwesome icon class
 * @param {string} props.description - Additional description text
 * @param {string} props.size - Size variant: "sm", "md", "lg"
 */
export const ImpactBox = ({ 
  metric,
  label,
  icon,
  description,
  size = "md",
  className = ''
}) => {
  const sizeClasses = {
    sm: "p-4 text-2xl",
    md: "p-6 text-3xl",
    lg: "p-8 text-4xl"
  };

  const iconSizes = {
    sm: "text-3xl",
    md: "text-4xl",
    lg: "text-5xl"
  };

  return (
    <div className={`bg-blue-50 rounded-lg ${sizeClasses[size]} ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className={`font-bold text-blue-700 ${size === 'lg' ? 'text-5xl' : size === 'sm' ? 'text-3xl' : 'text-4xl'}`}>
            {metric}
          </div>
          {label && (
            <div className="text-blue-600 font-semibold mt-2">
              {label}
            </div>
          )}
          {description && (
            <div className="text-gray-600 mt-3 text-base">
              {description}
            </div>
          )}
        </div>
        {icon && (
          <div className={`ml-6 text-blue-300 ${iconSizes[size]}`}>
            <i className={icon}></i>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImpactBox;