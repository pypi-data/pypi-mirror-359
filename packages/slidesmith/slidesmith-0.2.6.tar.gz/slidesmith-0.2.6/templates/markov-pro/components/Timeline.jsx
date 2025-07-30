import React from 'react';

/**
 * Timeline - Responsive timeline component
 * 
 * @param {Object} props
 * @param {Array<Object>} props.items - Timeline items with date, title, description, and optional icon
 * @param {string} props.orientation - "horizontal" or "vertical"
 * @param {string} props.lineColor - Color of the timeline line
 * @param {string} props.dotColor - Color of timeline dots
 * @param {boolean} props.showIcons - Whether to show icons in timeline items
 * @param {string} props.className - Additional CSS classes
 */
export const Timeline = ({ 
  items = [],
  orientation = 'horizontal',
  lineColor = 'border-blue-300',
  dotColor = 'bg-blue-700',
  showIcons = true,
  className = ''
}) => {
  if (orientation === 'vertical') {
    return (
      <div className={`relative ${className}`}>
        {/* Vertical line */}
        <div className={`absolute left-6 top-0 bottom-0 w-0.5 ${lineColor}`}></div>
        
        {/* Timeline items */}
        <div className="space-y-8">
          {items.map((item, index) => (
            <div key={index} className="relative flex items-start">
              {/* Dot and icon */}
              <div className="relative z-10 flex items-center justify-center">
                <div className={`w-12 h-12 rounded-full ${dotColor} flex items-center justify-center shadow-lg`}>
                  {showIcons && item.icon ? (
                    <i className={`${item.icon} text-white text-lg`}></i>
                  ) : (
                    <span className="text-white font-bold">{index + 1}</span>
                  )}
                </div>
              </div>
              
              {/* Content */}
              <div className="ml-8 flex-1">
                <div className="bg-white rounded-lg shadow-md p-6">
                  <div className="text-sm font-semibold text-blue-600 mb-1">
                    {item.date}
                  </div>
                  <h4 className="text-xl font-bold text-gray-800 mb-2">
                    {item.title}
                  </h4>
                  {item.description && (
                    <p className="text-gray-600">
                      {item.description}
                    </p>
                  )}
                  {item.details && (
                    <ul className="mt-3 space-y-1">
                      {item.details.map((detail, detailIndex) => (
                        <li key={detailIndex} className="text-gray-600 text-sm flex items-start">
                          <i className="fas fa-check text-green-500 mr-2 mt-0.5"></i>
                          <span>{detail}</span>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Horizontal timeline
  return (
    <div className={`relative ${className}`}>
      {/* Horizontal line */}
      <div className={`absolute top-6 left-0 right-0 h-0.5 ${lineColor}`}></div>
      
      {/* Timeline items */}
      <div className="flex justify-between">
        {items.map((item, index) => (
          <div key={index} className="relative flex-1 flex flex-col items-center">
            {/* Dot and icon */}
            <div className="relative z-10 mb-4">
              <div className={`w-12 h-12 rounded-full ${dotColor} flex items-center justify-center shadow-lg`}>
                {showIcons && item.icon ? (
                  <i className={`${item.icon} text-white text-lg`}></i>
                ) : (
                  <span className="text-white font-bold">{index + 1}</span>
                )}
              </div>
            </div>
            
            {/* Content */}
            <div className="text-center px-4">
              <div className="text-sm font-semibold text-blue-600 mb-1">
                {item.date}
              </div>
              <h4 className="text-lg font-bold text-gray-800 mb-2">
                {item.title}
              </h4>
              {item.description && (
                <p className="text-sm text-gray-600">
                  {item.description}
                </p>
              )}
            </div>
            
            {/* Connector line to next item */}
            {index < items.length - 1 && (
              <div className={`absolute top-6 left-1/2 w-full h-0.5 ${lineColor}`} 
                   style={{ transform: 'translateX(50%)' }}></div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default Timeline;