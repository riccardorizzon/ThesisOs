"use client";
import { useState } from "react";

export function InputBox({ disabled, onSend }: { disabled: boolean; onSend: (t: string) => void }) {
  const [text, setText] = useState("");
  const submit = () => { const t = text.trim(); if (t && !disabled) { onSend(t); setText(""); } };
  return (
    <div className="flex gap-2 border-t p-3">
      <textarea
        className="flex-1 resize-none rounded-lg border p-2 text-sm"
        rows={1}
        value={text}
        placeholder="Scrivi un messaggio…"
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); } }}
      />
      <button className="rounded-lg bg-accent px-4 text-sm text-ink-inverse disabled:opacity-50"
              disabled={disabled} onClick={submit}>Invia</button>
    </div>
  );
}
