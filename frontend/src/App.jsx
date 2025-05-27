import React from "react";
import { Chat } from "./components/Chat";



//  defining the root application component
//  the entry point for React component
function App() {
  return (
    <div style={{ fontFamily: "sans-serif", padding: 20 }}>
      {/* rendering Chat component to handles the chat UI and logic */}
      <Chat /> 
    </div>
  );
}

export default App;