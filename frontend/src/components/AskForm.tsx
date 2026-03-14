import { useState } from "react";

export default function Chat() {

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);

  const ask = async () => {

    const res = await fetch("http://127.0.0.1:8000/api/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ question })
    });

    const data = await res.json();

    setMessages([
      ...messages,
      { role: "user", text: question },
      { role: "assistant", text: data.answer }
    ]);

    setQuestion("");
  };

  return (
    <div className="w-full">

      <div>
        {messages.map((m, i) => (
          <div key={i}>
            <b>{m.role}:</b> {m.text}
          </div>
        ))}
      </div>

      <input
        className="border border-white inline-96"
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />

      <button onClick={ask}>
        Preguntar
      </button>

    </div>
  );
}