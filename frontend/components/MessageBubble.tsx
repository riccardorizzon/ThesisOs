import type { ChatMessage } from "@/lib/store";

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[80%] whitespace-pre-wrap rounded-2xl px-4 py-2 text-sm ${
        isUser ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900"}`}>
        {message.content || "…"}
      </div>
    </div>
  );
}
