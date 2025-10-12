import React from 'react'
import cn from 'classnames'
export const Input = React.forwardRef(({ className='', ...props }, ref) => {
  return <input ref={ref} className={cn('w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-slate-400', className)} {...props} />
})
Input.displayName = 'Input'
