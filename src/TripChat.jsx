import { useState} from "react";
import "./TripChat.css";


function TripChat(){
    const [messages, setMessages] = useState([
        {
            role: "assistant",
            content: "Hello, traveller! 🌎 ✨\n\nReady to relive your beautiful memories? Let's take another trip together, virtually!"
        }
    ]);

    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);

    const sendMessage = async () => {

        if (!input.trim() || loading) return;

        const userMessage = {
            role: "user",
            content: input.trim()
        };

        const updatedMessages = [
            ...messages,
            userMessage
        ];

        setMessages(updatedMessages);
        setInput("");
        setLoading(true);
        try {
            const response = await fetch(
                "http://127.0.0.1:8000/chat",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        messages: updatedMessages
                            .filter(msg => msg.role !== "assistant" ||
                                msg.content !== messages[0].content)
                            .map(msg => ({
                                role: msg.role,
                                content: msg.content
                            }))
                    })
                }
            );

            if (!response.ok) {
                throw new Error("Unable to get AI response");
            }
            const data = await response.json();
            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    content: data.reply
                }
            ]);
        } catch (error) {
            console.error(error);
            setMessages(prev => [
                ...prev,
                {
                    role: "assistant",
                    content: "Sorry! I couldn't connect to my AI brain. Please try again."
                }
            ]);
        } finally {
            setLoading(false);
        }
    };
    
    return(
        <div className="trip-chat">
            <div className="chat-messages">
                  {messages.map((msg, index) => (
                    <div key={index} className={`chat-message ${msg.role}`}>
                        {msg.content}
                    </div>
                ))}
                
                 {loading && (
                    <div className="chat-message assistant">
                        Thinking... ✨
                    </div>
                )}
            </div>

            <div className="chat-input-area">
                  <input type="text" placeholder="Ask about your trips..." value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => {
                        if (e.key === "Enter") sendMessage();
                    }}
                    disabled={loading}
                />
                <button onClick={sendMessage} disabled={loading || !input.trim()} > ➤ </button>
            </div>
        </div>
    );
}

export default TripChat;