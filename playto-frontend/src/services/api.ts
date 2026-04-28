const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL!;

export const apiFetch = async (url: string, options?: RequestInit) => {
  const res = await fetch(`${BASE_URL}${url}`, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  });

  if (!res.ok) {
    throw new Error("API Error");
  }
  console.log("API Response:", await res.clone().text());

  return res.json();
};