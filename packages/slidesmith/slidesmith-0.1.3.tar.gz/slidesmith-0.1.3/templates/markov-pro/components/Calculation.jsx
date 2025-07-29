import React from 'react';

/**
 * Calculation - Math-style calculation display component
 * 
 * @param {Object} props
 * @param {Array<Object>} props.steps - Calculation steps with label and value
 * @param {Object} props.result - Final result with label and value
 * @param {string} props.title - Optional title for the calculation
 * @param {boolean} props.showCurrency - Whether to show currency symbol
 * @param {string} props.currency - Currency symbol to use
 * @param {string} props.size - Size variant: "sm", "md", "lg"
 * @param {string} props.className - Additional CSS classes
 */
export const Calculation = ({ 
  steps = [],
  result,
  title,
  showCurrency = true,
  currency = '€',
  size = 'md',
  className = ''
}) => {
  const sizeConfig = {
    sm: {
      titleSize: 'text-lg',
      stepSize: 'text-base',
      resultSize: 'text-2xl',
      spacing: 'space-y-2',
      padding: 'p-4'
    },
    md: {
      titleSize: 'text-xl',
      stepSize: 'text-lg',
      resultSize: 'text-3xl',
      spacing: 'space-y-3',
      padding: 'p-6'
    },
    lg: {
      titleSize: 'text-2xl',
      stepSize: 'text-xl',
      resultSize: 'text-4xl',
      spacing: 'space-y-4',
      padding: 'p-8'
    }
  };

  const config = sizeConfig[size];

  const formatValue = (value) => {
    if (typeof value === 'number') {
      const formatted = value.toLocaleString('en-US');
      return showCurrency ? `${currency}${formatted}` : formatted;
    }
    return value;
  };

  return (
    <div className={`bg-gray-50 rounded-lg ${config.padding} ${className}`}>
      {title && (
        <h3 className={`${config.titleSize} font-bold text-gray-800 mb-4`}>
          {title}
        </h3>
      )}
      
      <div className={`${config.spacing}`}>
        {/* Calculation steps */}
        {steps.map((step, index) => (
          <div key={index} className="flex items-center justify-between">
            <div className="flex items-center">
              {index > 0 && (
                <span className="text-gray-400 mr-3">+</span>
              )}
              <span className={`${config.stepSize} text-gray-700`}>
                {step.label}
              </span>
            </div>
            <span className={`${config.stepSize} font-semibold text-gray-800`}>
              {formatValue(step.value)}
            </span>
          </div>
        ))}
        
        {/* Separator line */}
        {steps.length > 0 && result && (
          <div className="border-t-2 border-gray-300 my-3"></div>
        )}
        
        {/* Result */}
        {result && (
          <div className="flex items-center justify-between">
            <span className={`${config.resultSize} font-bold text-blue-800`}>
              {result.label || 'Total'}
            </span>
            <span className={`${config.resultSize} font-bold text-blue-700`}>
              {formatValue(result.value)}
            </span>
          </div>
        )}
      </div>
      
      {/* Optional note */}
      {result?.note && (
        <div className="mt-4 text-sm text-gray-600 italic">
          {result.note}
        </div>
      )}
    </div>
  );
};

export default Calculation;