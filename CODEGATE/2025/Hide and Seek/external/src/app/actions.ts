'use server'

import { redirect } from "next/navigation";

export async function redirectGame() {
  return redirect("/hide-and-seek");
}