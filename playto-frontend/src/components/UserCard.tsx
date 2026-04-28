"use client";

import { useRouter } from "next/navigation";
import { User } from "@/types/user";

export default function UserCard({ user }: { user: User }) {
  const router = useRouter();

  return (
    <div className="p-5 border rounded-xl shadow hover:shadow-lg transition">
      <h2 className="text-lg font-semibold">
        {user.first_name} {user.last_name}
      </h2>

      <p className="text-sm text-gray-500 mt-1">
        ID: {user.pt_id.slice(0, 8)}...
      </p>

      <button
        onClick={() => router.push(`/dashboard/${user.pt_id}`)}
        className="mt-4 px-4 py-2 bg-black text-white rounded-lg w-full"
      >
        View Dashboard →
      </button>
    </div>
  );
}