import React from 'react';

export const ThinkerIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg 
    xmlns="http://www.w3.org/2000/svg" 
    viewBox="0 0 24 24" 
    fill="currentColor" 
    className={className}
    aria-hidden="true"
  >
    {/* Head/Face */}
    <path d="M12 2C9.24 2 7 4.24 7 7c0 2.1.8 4.03 2.12 5.47-.08.17-.12.37-.12.53v2.5c0 .83.67 1.5 1.5 1.5h3c.83 0 1.5-.67 1.5-1.5V13c0-.16-.04-.36-.12-.53C16.2 11.03 17 9.1 17 7c0-2.76-2.24-5-5-5zm0 10c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3z" opacity="0.9" />
    {/* Bust/Shoulders */}
    <path d="M16.5 17h-9c-2.21 0-4 1.79-4 4v1h17v-1c0-2.21-1.79-4-4-4z" />
  </svg>
);

export default ThinkerIcon;
