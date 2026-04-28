"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  getProfile,
  getBalance,
  getLedger,
  getPayouts,
} from "@/services/dashboardService";

export default function DashboardPage() {
  const { pt_id } = useParams();

  const [profile, setProfile] = useState<any>(null);
  const [balance, setBalance] = useState<any>(null);
  const [ledger, setLedger] = useState<any[]>([]);
  const [payouts, setPayouts] = useState<any[]>([]);

  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  const [loading, setLoading] = useState(true);
  const [showPayouts, setShowPayouts] = useState(false);

  const pageSize = 10;

  const fetchDashboard = async (pageNo: number) => {
    try {
      setLoading(true);

      const [p, b, l] = await Promise.all([
        getProfile(pt_id as string),
        getBalance(pt_id as string),
        getLedger(pt_id as string, pageNo),
      ]);

      setProfile(p);
      setBalance(b);
      setLedger(l.results || []);
      setTotalCount(l.total_count || 0);
    } catch (err) {
      console.error("Dashboard fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPayouts = async () => {
    try {
      const data = await getPayouts(pt_id as string);
      setPayouts(data || []);
    } catch (err) {
      console.error("Payout fetch error:", err);
    }
  };

  useEffect(() => {
    if (pt_id) fetchDashboard(page);
  }, [pt_id, page]);

  if (loading) {
    return <div className="p-6">Loading dashboard...</div>;
  }

  return (
    <div className="p-6 space-y-6">

      <div className="p-4 border rounded-xl">
        <h2 className="text-lg font-bold mb-2">Profile</h2>

        <p>
          <b>Name:</b> {profile?.first_name} {profile?.last_name}
        </p>

        <p>
          <b>PT ID:</b> {profile?.pt_id}
        </p>

        <div className="mt-3 flex gap-3">
          <button className="px-4 py-2 bg-blue-600 text-white rounded">
            Create Payout
          </button>

          <button
            onClick={() => {
              setShowPayouts(true);
              fetchPayouts();
            }}
            className="px-4 py-2 bg-black text-white rounded"
          >
            View Payouts
          </button>
        </div>

        <h3 className="mt-4 font-semibold">Bank Accounts</h3>

        {profile?.bank_accounts?.length === 0 && (
          <p className="text-gray-500">No bank accounts found</p>
        )}

        {profile?.bank_accounts?.map((acc: any) => (
          <div key={acc.id} className="mt-2 p-2 border rounded">
            <p>
              <b>Bank:</b> {acc.bank_name}
            </p>

            <p>
              <b>Branch:</b> {acc.bank_branch}
            </p>

            <p>
              <b>Account:</b> ****{acc.account_number_hash?.slice(-4)}
            </p>
          </div>
        ))}
      </div>

      <div className="p-4 border rounded-xl">
        <h2 className="text-lg font-bold mb-2">Balance</h2>

        <p>
          <b>Available:</b> {balance?.available_balance}
        </p>

        <p>
          <b>Held:</b> {balance?.held_balance}
        </p>
      </div>

      <div className="p-4 border rounded-xl">
        <h2 className="text-lg font-bold mb-3">Ledger</h2>

        {ledger.length === 0 ? (
          <p className="text-gray-500">No transactions found</p>
        ) : (
          <table className="w-full text-sm border">
            <thead>
              <tr className="bg-gray-100">
                <th className="p-2 border">Type</th>
                <th className="p-2 border">Amount</th>
                <th className="p-2 border">Reference</th>
                <th className="p-2 border">Date</th>
              </tr>
            </thead>

            <tbody>
              {ledger.map((entry: any) => (
                <tr key={entry.id}>
                  <td className="p-2 border">{entry.entry_type}</td>

                  <td className="p-2 border">
                    {entry.amount_paise}
                  </td>

                  <td className="p-2 border">
                    {entry.reference_id || "-"}
                  </td>

                  <td className="p-2 border">
                    {new Date(entry.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        <div className="flex justify-between mt-4">
          <button
            disabled={page === 1}
            onClick={() => setPage((p) => p - 1)}
            className="px-4 py-2 border rounded disabled:opacity-50"
          >
            Prev
          </button>

          <span>Page {page}</span>

          <button
            disabled={page * pageSize >= totalCount}
            onClick={() => setPage((p) => p + 1)}
            className="px-4 py-2 border rounded disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>

      {showPayouts && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-xl w-[700px] max-h-[80vh] overflow-y-auto">

            <div className="flex justify-between mb-4">
              <h2 className="text-lg font-bold">Payouts</h2>

              <button
                onClick={() => setShowPayouts(false)}
                className="text-red-500"
              >
                Close
              </button>
            </div>

            {payouts.length === 0 ? (
              <p>No payouts found</p>
            ) : (
              <table className="w-full text-sm border">
                <thead>
                  <tr className="bg-gray-100">
                    <th className="p-2 border">Amount</th>
                    <th className="p-2 border">Status</th>
                    <th className="p-2 border">Bank</th>
                    <th className="p-2 border">Account</th>
                    <th className="p-2 border">Remarks</th>
                    <th className="p-2 border">Date</th>
                  </tr>
                </thead>

                <tbody>
                  {payouts.map((p: any) => (
                    <tr key={p.id}>
                      <td className="p-2 border">
                        {p.amount_paise}
                      </td>

                      <td className="p-2 border">{p.status}</td>

                      <td className="p-2 border">{p.bank_name}</td>

                      <td className="p-2 border">{p.masked_account}</td>

                      <td className="p-2 border">
                        {p.failure_reason || "-"}
                      </td>

                      <td className="p-2 border">
                        {new Date(p.created_at).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      )}
    </div>
  );
}