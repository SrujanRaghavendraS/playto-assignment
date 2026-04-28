import { apiFetch } from "./api";

interface LedgerResponse {
  total_count: number;
  page_no: number;
  results: any[];
}

export const getProfile = async (pt_id: string) => {
  return apiFetch("/profile/", {
    method: "POST",
    body: JSON.stringify({ pt_id }),
  });
};

export const getBalance = async (pt_id: string) => {
  return apiFetch("/balance/", {
    method: "POST",
    body: JSON.stringify({ pt_id }),
  });
};

export const getLedger = async (
  pt_id: string,
  page_no: number = 1
): Promise<LedgerResponse> => {
  return apiFetch("/ledger/", {
    method: "POST",
    body: JSON.stringify({ pt_id, page_no }),
  });
};

export const getPayouts = async (pt_id: string) => {
  return apiFetch("/payouts/list/", {
    method: "POST",
    body: JSON.stringify({ pt_id }),
  });
};