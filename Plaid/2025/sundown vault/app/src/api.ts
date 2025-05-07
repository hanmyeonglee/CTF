import bcrypt from "@node-rs/bcrypt";
import express from "express";
import { DateTime, Duration } from "luxon";
import { sql } from "slonik";
import { z } from "zod";

import { pool } from "./db.js";

const MaxSecretDate = "2030-01-01T00:00:00.000"; // if you want to keep a secret longer than this, do it yourself >:(

const UpdateIntervals = [
	Duration.fromObject({ years: 2 }).toMillis(),
	Duration.fromObject({ years: 1 }).toMillis(),
	Duration.fromObject({ months: 6 }).toMillis(),
	Duration.fromObject({ months: 2 }).toMillis(),
	Duration.fromObject({ months: 1 }).toMillis(),
	Duration.fromObject({ weeks: 1 }).toMillis(),
	Duration.fromObject({ days: 1 }).toMillis(),
	Duration.fromObject({ hours: 1 }).toMillis(),
	Duration.fromObject({ minutes: 30 }).toMillis(),
	Duration.fromObject({ minutes: 10 }).toMillis(),
	Duration.fromObject({ minutes: 5 }).toMillis(),
	Duration.fromObject({ minutes: 1 }).toMillis(),
	Duration.fromObject({ seconds: 30 }).toMillis(),
	Duration.fromObject({ seconds: 10 }).toMillis(),
	Duration.fromObject({ seconds: 5 }).toMillis(),
	Duration.fromObject({ seconds: 1 }).toMillis(),
	Duration.fromObject({ milliseconds: 500 }).toMillis(),
	Duration.fromObject({ milliseconds: 100 }).toMillis(),
];

function formatDuration(ms: number) {
	if (ms < 1000) {
		return "0s";
	}

	const seconds = Math.floor(ms / 1000);

	if (seconds < 60) {
		return `${seconds}s`;
	}

	const minutes = Math.floor(seconds / 60);

	if (minutes < 60) {
		return `${minutes}m`;
	}

	const hours = Math.floor(minutes / 60);

	if (hours < 24) {
		return `${hours}h`;
	}

	const days = Math.floor(hours / 24);

	if (days < 7) {
		return `${days}d`;
	}

	const weeks = Math.floor(days / 7);

	if (weeks < 4) {
		return `${weeks}w`;
	}

	const months = Math.floor(weeks / 4);

	if (months < 12) {
		return `${months}mo`;
	}

	const years = Math.floor(months / 12);

	return `${years}y`;
}

export const apiRouter = express.Router();

apiRouter.use(async (req, res, next) => {
	req.sundown = {};

	if (typeof req.cookies.session === "string") {
		try {
			req.sundown.user =
				(await pool.maybeOneFirst(sql.type(z.object({ id: z.string() }))`
				SELECT id
				FROM sundown.user
					JOIN sundown.token ON sundown.token.user_id = sundown.user.id
				WHERE sundown.token.token = ${req.cookies.session}
			`)) ?? undefined;
		} catch (err) {
			// Ignore
		}
	}

	next();
});

apiRouter.post("/register", async (req, res) => {
	await pool.transaction(async (tx) => {
		const body = z
			.object({
				username: z.string(),
				password: z.string(),
			})
			.parse(req.body);

		const passwordHash = await bcrypt.hash(body.password, 12);

		await tx.one(sql.unsafe`
			INSERT INTO sundown.user (id, password)
			VALUES (${body.username}, ${passwordHash})
			RETURNING *
		`);

		res.json({ success: true });
	});
});

apiRouter.post("/login", async (req, res) => {
	const body = z
		.object({
			username: z.string(),
			password: z.string(),
		})
		.parse(req.body);

	const user = await pool.maybeOne(sql.type(z.object({ id: z.string(), password: z.string() }))`
		SELECT * FROM sundown.user
		WHERE id = ${body.username}
	`);

	if (user === null) {
		res.status(403).send("Invalid username or password");
		return;
	}

	const passwordOk = await bcrypt.compare(body.password, user.password);

	if (!passwordOk) {
		res.status(403).send("Invalid username or password");
		return;
	}

	const token = await pool.one(sql.type(z.object({ token: z.string() }))`
		INSERT INTO sundown.token (user_id)
		VALUES (${user.id})
		RETURNING token
	`);

	res.cookie("session", token.token, { httpOnly: true });
	res.json({ success: true });
});

apiRouter.post("/logout", async (req, res) => {
	if (req.sundown.user === undefined) {
		res.status(403).send("Not authenticated");
		return;
	}

	await pool.query(sql.unsafe`
		DELETE FROM sundown.token
		WHERE user_id = ${req.sundown.user}
	`);

	res.clearCookie("session");
	res.json({ success: true });
});

apiRouter.get("/me", async (req, res) => {
	if (req.sundown.user === undefined) {
		res.status(403).send("Not authenticated");
		return;
	}

	res.json({ user: req.sundown.user });
});

apiRouter.get("/secrets/my", async (req, res) => {
	if (req.sundown.user === undefined) {
		res.status(403).send("Not authenticated");
		return;
	}

	const secrets = await pool.any(sql.type(
		z.object({
			id: z.string(),
			name: z.string(),
			reveal_at: z.number(),
			created_at: z.number(),
		}),
	)`
		SELECT id, name, timestamp_to_ms(reveal_at) AS reveal_at, timestamp_to_ms(created_at) AS created_at
		FROM sundown.secret
		WHERE owner_id = ${req.sundown.user}
	`);

	res.json({
		secrets: secrets.map((secret) => ({
			id: secret.id,
			name: secret.name,
			revealAt: DateTime.fromMillis(secret.reveal_at, { zone: "UTC" }).toISO(),
			createdAt: DateTime.fromMillis(secret.created_at, {
				zone: "UTC",
			}).toISO(),
		})),
	});
});

apiRouter.post("/secrets/create", async (req, res) => {
	const body = z
		.object({
			secret: z.string().min(1).max(1000),
			name: z.string().min(1).max(100),
			revealAt: z.string().transform((s, ctx) => {
				const date = DateTime.fromISO(s);

				if (!date.isValid) {
					ctx.addIssue({ code: "custom", message: "Invalid date" });
					return z.NEVER;
				}

				if (s > MaxSecretDate) {
					ctx.addIssue({
						code: "custom",
						message: "Reveal date too far in the future",
					});
					return z.NEVER;
				}

				return date;
			}),
		})
		.parse(req.body);

	if (req.sundown.user === undefined) {
		res.status(403).send("Not authenticated");
		return;
	}

	const id = await pool.oneFirst(sql.type(z.object({ id: z.string() }))`
		INSERT INTO sundown.secret (owner_id, name, secret, reveal_at)
		VALUES (${req.sundown.user}, ${body.name}, ${body.secret}, ms_to_timestamp(${body.revealAt.toMillis()}))
		RETURNING id
	`);

	res.json({ id });
});

apiRouter.ws("/ws", (ws, req) => {
	let secretId: string | undefined;
	let secret: string | undefined;
	let timeout: NodeJS.Timeout | undefined;
	let remaining: number | undefined;
	let timeoutDuration: number | undefined;

	function revealSecret() {
		if (secretId === undefined || secret === undefined) {
			return;
		}

		ws.send(JSON.stringify({ kind: "Reveal", id: secretId, secret }));
		secretId = undefined;
		secret = undefined;
		timeout = undefined;
		remaining = undefined;
	}

	function updateTimeoutDuration() {
		console.log('update', remaining);
		timeoutDuration = UpdateIntervals.find((interval) => interval <= remaining! / 100) ?? 100;
		console.log('update', timeoutDuration);
	}

	function updateTimeout() {
		console.log('updateTimeout', remaining, )
		if (remaining === undefined) {
			return;
		}

		if (timeout !== undefined) {
			clearTimeout(timeout);
		}

		ws.send(JSON.stringify({ kind: "Update", remaining: formatDuration(remaining) }));

		timeout = setTimeout(() => {
			console.log('settimeout', remaining, timeoutDuration);
			remaining! -= timeoutDuration!;
			if (remaining! <= 0) {
				revealSecret();
			} else {
				updateTimeoutDuration();
				updateTimeout();
			}
		}, timeoutDuration);
	}

	ws.on("close", () => {
		if (timeout !== undefined) {
			clearTimeout(timeout);
		}
	});

	ws.on("message", async (message) => {
		try {
			let data: { command: "open"; id: string };
			console.log('request', remaining, timeoutDuration);

			try {
				let rawData: unknown;

				if (typeof message === "string") {
					rawData = JSON.parse(message);
				} else {
					rawData = JSON.parse(message.toString());
				}

				data = z
					.object({
						command: z.literal("open"),
						id: z.string(),
					})
					.parse(rawData);
			} catch (err) {
				ws.send(JSON.stringify({ error: "Failed to parse command" }));
				return;
			}

			const secretData = await pool.maybeOne(sql.type(
				z.object({
					id: z.string(),
					owner_id: z.string(),
					name: z.string(),
					secret: z.string(),
					reveal_at: z.number(),
					created_at: z.number(),
				}),
			)`
				SELECT id, owner_id, name, secret, timestamp_to_ms(reveal_at) AS reveal_at, timestamp_to_ms(created_at) AS created_at
				FROM sundown.secret
				WHERE id = ${data.id}
			`);

			if (secretData === null) {
				ws.send(JSON.stringify({ error: "Secret not found" }));
				return;
			}

			secretId = secretData.id;
			secret = secretData.secret;
			ws.send(JSON.stringify({ kind: "Watch", id: secretId, name: secretData.name }));
			remaining = new Date(secretData.reveal_at).getTime() - Date.now();
			
			if (remaining <= 0) {
				revealSecret();
			} else {
				if (timeoutDuration === undefined) {
					updateTimeoutDuration();
					console.log('undefined timeoutDuration', remaining, timeoutDuration)
				}
				updateTimeout();
			}
		} catch (err) {
			console.error("Unexpected error", err);
			ws.close();
		}
	});

	ws.send(JSON.stringify({ kind: "Connected" }));
});
