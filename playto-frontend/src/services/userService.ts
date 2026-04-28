import { apiFetch } from "./api";
import { User } from "@/types/user";

export const getUsers = async (): Promise<User[]> => {
  return apiFetch("/users/");
};