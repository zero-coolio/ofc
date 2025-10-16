// src/components/Banner.tsx
import React from "react";

export default function Banner(){
  return (
    <div className="relative" style={{padding:"3rem 1rem", textAlign:"center",
      background:"linear-gradient(135deg,#e9f7f5 0%,#c8eee9 35%,#e9f7f5 100%)"}}>
      <h1 style={{fontSize:32, fontWeight:600, color:"#0f766e", margin:0}}>Overseas Food Trading</h1>
      <p style={{color:"#145e5b", opacity:.85, marginTop:6}}>Demo financial transactions dashboard</p>
    </div>
  );
}
