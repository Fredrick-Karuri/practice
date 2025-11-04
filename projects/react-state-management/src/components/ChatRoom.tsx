import { type FC, useEffect, useState } from "react";

export const ChatRoom: FC<{ roomId: string }> = ({ roomId }) => {
    const [messages, setMessages] = useState<string[]>([]);
    useEffect(() => {
        const ws = new WebSocket(`wss://chat.example.com/${roomId}`);
        ws.onmessage = (event) => {
            setMessages((prev) => [...prev, event.data]);
        };
        return () =>{
            ws.close(); //cleanup function
        };
    }, [roomId]);
    return (
    <div>
    {messages.map((m) => <p>{m}</p>)}
    </div>
    );
};