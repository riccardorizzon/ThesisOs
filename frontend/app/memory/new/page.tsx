"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { MemoryErrorBanner } from "@/components/MemoryErrorBanner";
import { MemoryForm } from "@/components/MemoryForm";
import { useMemoryStore } from "@/lib/memoryStore";

export default function MemoryCreatePage() {
  const router = useRouter();
  const { loading, error, errorCode, errorStatus, create, clearError } = useMemoryStore();

  async function handleCreate(input: Parameters<typeof create>[0]) {
    try {
      const created = await create(input);
      router.push(`/memory/${created.id}`);
    } catch {
      // error shown via store banner
    }
  }

  return (
    <section className="mx-auto max-w-2xl space-y-6">
      <div>
        <Link href="/memory" className="text-sm text-gray-500 hover:underline">
          ← Back to list
        </Link>
        <h1 className="mt-2 text-2xl font-semibold">Create memory</h1>
      </div>

      <MemoryErrorBanner message={error} code={errorCode} status={errorStatus} />
      {error && (
        <button type="button" onClick={clearError} className="text-xs text-gray-500 underline">
          Dismiss
        </button>
      )}

      <MemoryForm mode="create" onSubmit={handleCreate} loading={loading} />
    </section>
  );
}
