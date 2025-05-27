// import React, { useState, useEffect, useRef } from "react";

// export function Chat() {
//   const [messages, setMessages] = useState([]);
//   const [input, setInput]       = useState("");
//   const bottomRef = useRef(null);

//   useEffect(() => {
//     if (bottomRef.current) {
//       bottomRef.current.scrollIntoView({ behavior: "smooth" });
//     }
//   }, [messages]);

//   const sendMessage = async (e) => {
//     e.preventDefault();
//     if (!input.trim()) return;
//     const userMsg = input.trim();
//     setMessages(ms => [...ms, { from: "user", text: userMsg }]);
//     setInput("");

//     const res = await fetch("http://localhost:8000/api/chat/", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ message: userMsg, session_id: "default" }),
//     });
//     const { reply } = await res.json();
//     setMessages(ms => [...ms, { from: "bot", text: reply }]);
//   };

//   return (
//     <div style={{ maxWidth: 600, margin: "auto" }}>
//       <h1>📬 Spencer Email-DB Assistant</h1>
//       <div
//         style={{
//           border: "1px solid #ccc",
//           borderRadius: 8,
//           minHeight: 300,
//           padding: 12,
//           overflowY: "auto",
//           marginBottom: 12,
//         }}
//       >
//         {messages.map((m, i) => (
//           <div
//             key={i}
//             style={{
//               textAlign: m.from === "user" ? "right" : "left",
//               margin: "8px 0",
//             }}
//           >
//             <strong>{m.from === "user" ? "You" : "Bot"}:</strong> {m.text}
//           </div>
//         ))}
//         <div ref={bottomRef} />
//       </div>

//       <form onSubmit={sendMessage} style={{ display: "flex" }}>
//         <input
//           style={{ flex: 1, padding: 8, fontSize: 16 }}
//           value={input}
//           onChange={(e) => setInput(e.target.value)}
//           placeholder="Ask about your email database…"
//         />
//         <button style={{ marginLeft: 8, padding: "0 16px" }}>
//           Send
//         </button>
//       </form>
//     </div>
//   );
// }


import React, { useState, useEffect, useRef } from "react";

export function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput]       = useState("");
  const bottomRef = useRef(null);

  // scroll down on new message
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = input.trim();
    // add user message
    setMessages(ms => [...ms, { from: "user", text: userMsg }]);
    setInput("");

    try {
      const res = await fetch("http://localhost:8000/api/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg, session_id: "default" }),
      });
      // const { reply, accuracy } = await res.json();
      const { reply: rawReply, accuracy } = await res.json();

      // strip any literal ``` fences or trailing whitespace
      const reply = rawReply.replace(/```/g, "").trim();

      // adding chatbot reply + accuracy (confidence score)
      setMessages(ms => [
        ...ms,
        { from: "bot", text: reply, accuracy }
      ]);
    } catch (err) {
      console.error(err);
      setMessages(ms => [
        ...ms,
        { from: "bot", text: "Error: failed to fetch reply." }
      ]);
    }
  };

  return (
    <div style={{ maxWidth: 600, margin: "auto" }}>
      <h1 style={{textAlign:"center"}}>Experimental Database Assistant Chatbot</h1>

      <div
        style={{
          border: "1px solid #ccc",
          borderRadius: 8,
          minHeight: 300,
          padding: 12,
          overflowY: "auto",
          marginBottom: 12,
        }}
      >
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              textAlign: m.from === "user" ? "right" : "left",
              margin: "8px 0",
            }}
          >
            <strong>{m.from === "user" ? "You" : "Bot"}:</strong> {m.text}
            {m.from === "bot" && m.accuracy != null && (
              <div style={{ fontSize: 12, color: "#666", marginTop: 4 }}>
                Confidence score: {(m.accuracy * 100).toFixed(2)}%
              </div>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={sendMessage} style={{ display: "flex" }}>
        <input
          style={{ flex: 1, padding: 8, fontSize: 16 }}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="How can I help you today?" 
        />
        <button style={{ marginLeft: 8, padding: "0 16px" }}>
          Send
        </button>
      </form>
    </div>
  );
}

