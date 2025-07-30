import React from 'react';

/**
 * CardGrid - Three-card layout for steps or features
 * 
 * @param {Object} props
 * @param {Array} props.cards - Array of card objects with title, icon, subtitle, and items
 * @param {string} props.className - Additional CSS classes
 */
export const CardGrid = ({ cards = [], className = '' }) => {
  return (
    <div className={`flex justify-between ${className}`}>
      {cards.map((card, index) => (
        <div 
          key={index} 
          className={`w-1/3 ${index === 0 ? 'pr-6' : index === cards.length - 1 ? 'pl-6' : 'px-3'}`}
        >
          <div className="bg-white border border-gray-200 rounded-lg shadow-lg h-full">
            <div className="p-6">
              <div className="flex items-center mb-4">
                <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center mr-4">
                  <i className={`${card.icon} text-2xl text-blue-700`}></i>
                </div>
                <h3 className="text-2xl font-bold text-blue-800">{card.title}</h3>
              </div>
              {card.subtitle && (
                <div className="flex items-center text-lg text-blue-700 font-semibold mb-4">
                  {card.subtitleIcon && <i className={`${card.subtitleIcon} mr-2`}></i>}
                  <span>{card.subtitle}</span>
                </div>
              )}
              {card.items && (
                <ul className="space-y-4 mt-6">
                  {card.items.map((item, itemIndex) => (
                    <li key={itemIndex} className="flex items-start">
                      <i className="fas fa-check-circle text-blue-600 mt-1 mr-3"></i>
                      <span className="text-gray-700">{item}</span>
                    </li>
                  ))}
                </ul>
              )}
              {card.content && (
                <div className="mt-6 text-gray-700">
                  {card.content}
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default CardGrid;