import React from 'react'
export function Switch({ checked=false, onCheckedChange }) {
  return (
    <label className="relative inline-flex items-center cursor-pointer select-none">
      <input type="checkbox" className="sr-only peer" checked={checked} onChange={e=>onCheckedChange?.(e.target.checked)} />
      <div className="w-10 h-6 bg-slate-300 rounded-full peer-checked:bg-slate-900 transition-all"></div>
      <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-4"></div>
    </label>
  )
}
