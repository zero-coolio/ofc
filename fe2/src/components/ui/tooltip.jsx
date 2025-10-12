import React from 'react'
export function TooltipProvider({ children }) { return children }
export function Tooltip({ children }) { return children }
export function TooltipTrigger({ children }) { return children }
export function TooltipContent({ children }) { return <span className="ml-2 text-xs text-slate-500">{children}</span> }
