import React from 'react';

/**
 * CTABox - Call-to-action component with button
 * 
 * @param {Object} props
 * @param {string} props.title - CTA title
 * @param {string} props.description - CTA description text
 * @param {string} props.buttonText - Text for the CTA button
 * @param {string} props.buttonIcon - Optional FontAwesome icon for button
 * @param {string} props.backgroundColor - Background color
 * @param {string} props.textColor - Text color
 * @param {string} props.buttonColor - Button background color
 * @param {string} props.buttonTextColor - Button text color
 * @param {React.ReactNode} props.additionalContent - Additional content to render
 * @param {string} props.layout - Layout style: "centered", "left", "right"
 * @param {string} props.size - Size variant: "sm", "md", "lg"
 * @param {Function} props.onButtonClick - Click handler for button
 * @param {string} props.className - Additional CSS classes
 */
export const CTABox = ({ 
  title,
  description,
  buttonText,
  buttonIcon,
  backgroundColor = 'bg-blue-700',
  textColor = 'text-white',
  buttonColor = 'bg-white',
  buttonTextColor = 'text-blue-800',
  additionalContent,
  layout = 'centered',
  size = 'md',
  onButtonClick,
  className = ''
}) => {
  const sizeConfig = {
    sm: {
      padding: 'p-6',
      titleSize: 'text-2xl',
      descriptionSize: 'text-lg',
      buttonPadding: 'py-2 px-4',
      buttonTextSize: 'text-lg'
    },
    md: {
      padding: 'p-8',
      titleSize: 'text-3xl',
      descriptionSize: 'text-xl',
      buttonPadding: 'py-3 px-6',
      buttonTextSize: 'text-xl'
    },
    lg: {
      padding: 'p-12',
      titleSize: 'text-4xl',
      descriptionSize: 'text-2xl',
      buttonPadding: 'py-4 px-8',
      buttonTextSize: 'text-2xl'
    }
  };

  const config = sizeConfig[size];

  const layoutClasses = {
    centered: 'text-center items-center justify-center',
    left: 'text-left items-start justify-start',
    right: 'text-right items-end justify-end'
  };

  return (
    <div className={`${backgroundColor} ${textColor} rounded-lg ${config.padding} flex flex-col ${layoutClasses[layout]} ${className}`}>
      {title && (
        <h3 className={`${config.titleSize} font-bold mb-4`}>
          {title}
        </h3>
      )}
      
      {description && (
        <p className={`${config.descriptionSize} mb-6 opacity-90`}>
          {description}
        </p>
      )}
      
      {buttonText && (
        <button 
          onClick={onButtonClick}
          className={`${buttonColor} ${buttonTextColor} ${config.buttonTextSize} font-bold ${config.buttonPadding} rounded-lg hover:opacity-90 transition-opacity shadow-lg flex items-center ${layout === 'centered' ? 'mx-auto' : ''}`}
        >
          {buttonIcon && (
            <i className={`${buttonIcon} mr-3`}></i>
          )}
          {buttonText}
        </button>
      )}
      
      {additionalContent && (
        <div className="mt-6">
          {additionalContent}
        </div>
      )}
    </div>
  );
};

export default CTABox;