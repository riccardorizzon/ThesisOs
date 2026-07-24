"use client";
import { useState } from "react";

const MAX_MESSAGE_LENGTH = 32_000;

type InputBoxProps = {
  disabled: boolean;
  onSend: (text: string) => void;
  streaming?: boolean;
  onCancel?: () => void;
};

export function InputBox({
  disabled,
  onSend,
  streaming = false,
  onCancel,
}: InputBoxProps) {
  const [text, setText] = useState("");
  const submit = () => { const t = text.trim(); if (t && !disabled) { onSend(t); setText(""); } };
  return (
    <div className="border-t p-3">
      <div className="flex gap-2">
        <textarea
          className="flex-1 resize-none rounded-lg border p-2 text-sm"
          rows={1}
          value={text}
          maxLength={MAX_MESSAGE_LENGTH}
          disabled={disabled || streaming}
          placeholder="Scrivi un messaggio…"
          onChange={(e) => setText(e.target.value.slice(0, MAX_MESSAGE_LENGTH))}
          onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); } }}
        />
        {streaming ? (
          <button
            type="button"
            className="rounded-lg border border-border px-4 text-sm font-medium text-ink hover:bg-surface-muted"
            onClick={onCancel}
          >
            Interrompi
          </button>
        ) : (
          <button
            type="button"
            className="rounded-lg bg-accent px-4 text-sm text-ink-inverse disabled:opacity-50"
            disabled={disabled}
            onClick={submit}
          >
            Invia
          </button>
        )}
      </div>
      {text.length >= MAX_MESSAGE_LENGTH ? (
        <p className="mt-1 text-xs text-warning" role="status">
          Limite di 32.000 caratteri raggiunto.
        </p>
      ) : null}
    </div>
  );
}
