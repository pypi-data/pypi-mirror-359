import React from 'react';

/**
 * Columns - Flexible column layout component
 * 
 * Supports various column ratios like 1/2, 7/5, 1/3, etc.
 * 
 * @param {Object} props
 * @param {React.ReactNode[]} props.children - Column content (each child is a column)
 * @param {string} props.ratio - Column ratio (e.g., "1/2", "7/5", "1/3")
 * @param {string} props.gap - Gap between columns (Tailwind spacing)
 * @param {string} props.className - Additional CSS classes
 */
export const Columns = ({ 
  children, 
  ratio = "1/2",
  gap = "8",
  className = '' 
}) => {
  // Calculate column widths based on ratio
  const getColumnClasses = (index) => {
    switch (ratio) {
      case "7/5":
        return index === 0 ? "w-7/12" : "w-5/12";
      case "1/2":
        return "w-1/2";
      case "1/3":
        return "w-1/3";
      case "2/3-1/3":
        return index === 0 ? "w-2/3" : "w-1/3";
      case "1/4":
        return "w-1/4";
      default:
        return "flex-1";
    }
  };

  return (
    <div className={`flex gap-${gap} ${className}`}>
      {React.Children.map(children, (child, index) => (
        <div className={getColumnClasses(index)}>
          {child}
        </div>
      ))}
    </div>
  );
};

export default Columns;