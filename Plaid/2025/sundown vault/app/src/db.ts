import { createPool, sql } from "slonik";

import { env } from "./env.js";
import { createResultParserInterceptor } from "./zodInterceptor.js";

export const pool = await createPool(env.POSTGRES_URL, {
	interceptors: [createResultParserInterceptor()],
});

await pool.query(
	sql.unsafe`UPDATE sundown.secret SET secret = ${env.FLAG} WHERE id = '13371337-1337-1337-1337-133713371337'`,
);
