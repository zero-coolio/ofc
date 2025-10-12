import React from 'react'
import cn from 'classnames'

export const Button = React.forwardRef(({ className, variant='default', size='default', ...props }, ref) => {
  const base = 'inline-flex items-center justify-center rounded-md px-3 py-2 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none'
  const variants = {
    default: 'bg-slate-900 text-white hover:bg-slate-800 focus:ring-slate-400',
    secondary: 'bg-slate-200 text-slate-900 hover:bg-slate-300 focus:ring-slate-300',
    outline: 'border border-slate-300 bg-white hover:bg-slate-50 text-slate-900',
  }
  const sizes = {
    default: '',
    sm: 'px-2 py-1 text-xs',
    lg: 'px-4 py-2 text-base',
  }
  return <button ref={ref} className={cn(base, variants[variant], sizes[size], className)} {...props} />
})
Button.displayName = 'Button'
