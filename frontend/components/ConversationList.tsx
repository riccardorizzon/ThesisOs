export function ConversationList({ activeId }: { activeId: string | null }) {
  return (
    <aside className="w-56 shrink-0 border-r p-3 text-sm">
      <div className="mb-2 font-medium text-gray-500">Conversazioni</div>
      <div className="rounded-lg bg-gray-100 px-3 py-2">
        {activeId ? "Conversazione corrente" : "New Conversation"}
      </div>
    </aside>
  );
}
