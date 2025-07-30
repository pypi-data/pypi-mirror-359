import React from 'react';

/**
 * MetricSection - Icon + title + content display component
 * 
 * @param {Object} props
 * @param {string} props.icon - FontAwesome icon class
 * @param {string} props.iconColor - Color for the icon
 * @param {string} props.iconBg - Background color for icon container
 * @param {string} props.title - Section title
 * @param {string} props.content - Section content/description
 * @param {string} props.metric - Optional metric value to highlight
 * @param {string} props.metricLabel - Label for the metric
 * @param {string} props.layout - Layout style: "horizontal" or "vertical"
 * @param {string} props.size - Size variant: "sm", "md", "lg"
 * @param {string} props.className - Additional CSS classes
 */
export const MetricSection = ({ 
  icon,
  iconColor = 'text-blue-700',
  iconBg = 'bg-blue-100',
  title,
  content,
  metric,
  metricLabel,
  layout = 'horizontal',
  size = 'md',
  className = ''
}) => {
  const sizeConfig = {
    sm: {
      iconSize: 'h-10 w-10',
      iconText: 'text-xl',
      titleText: 'text-lg',
      contentText: 'text-sm',
      metricText: 'text-2xl',
      spacing: 'space-y-2'
    },
    md: {
      iconSize: 'h-12 w-12',
      iconText: 'text-2xl',
      titleText: 'text-xl',
      contentText: 'text-base',
      metricText: 'text-3xl',
      spacing: 'space-y-3'
    },
    lg: {
      iconSize: 'h-16 w-16',
      iconText: 'text-3xl',
      titleText: 'text-2xl',
      contentText: 'text-lg',
      metricText: 'text-4xl',
      spacing: 'space-y-4'
    }
  };

  const config = sizeConfig[size];

  if (layout === 'vertical') {
    return (
      <div className={`text-center ${config.spacing} ${className}`}>
        {icon && (
          <div className="flex justify-center mb-4">
            <div className={`${config.iconSize} rounded-full ${iconBg} flex items-center justify-center`}>
              <i className={`${icon} ${config.iconText} ${iconColor}`}></i>
            </div>
          </div>
        )}
        
        {title && (
          <h3 className={`${config.titleText} font-bold text-gray-800`}>
            {title}
          </h3>
        )}
        
        {metric && (
          <div className="my-3">
            <div className={`${config.metricText} font-bold text-blue-700`}>
              {metric}
            </div>
            {metricLabel && (
              <div className="text-sm text-gray-600 mt-1">
                {metricLabel}
              </div>
            )}
          </div>
        )}
        
        {content && (
          <p className={`${config.contentText} text-gray-600`}>
            {content}
          </p>
        )}
      </div>
    );
  }

  // Horizontal layout (default)
  return (
    <div className={`flex items-start ${className}`}>
      {icon && (
        <div className={`${config.iconSize} rounded-full ${iconBg} flex items-center justify-center flex-shrink-0 mr-4`}>
          <i className={`${icon} ${config.iconText} ${iconColor}`}></i>
        </div>
      )}
      
      <div className="flex-1">
        {title && (
          <h3 className={`${config.titleText} font-bold text-gray-800 mb-2`}>
            {title}
          </h3>
        )}
        
        {metric && (
          <div className="mb-3">
            <span className={`${config.metricText} font-bold text-blue-700`}>
              {metric}
            </span>
            {metricLabel && (
              <span className="text-sm text-gray-600 ml-2">
                {metricLabel}
              </span>
            )}
          </div>
        )}
        
        {content && (
          <p className={`${config.contentText} text-gray-600`}>
            {content}
          </p>
        )}
      </div>
    </div>
  );
};

export default MetricSection;