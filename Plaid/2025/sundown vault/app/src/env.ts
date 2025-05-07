import { z } from "zod";

export const env = z
	.object({
		POSTGRES_URL: z.string().default("postgres://postgres:postgres@localhost:5432/sundown"),
		FLAG: z.string().default("PCTF{test_flag}"),
	})
	.parse(process.env);
