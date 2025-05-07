import cookieParser from "cookie-parser";
import express from "express";
import "express-async-errors";
import expressWs from "express-ws";
import { ZodError } from "zod";

declare global {
	namespace Express {
		interface Request {
			sundown: {
				user?: string;
			};
		}
	}
}

const { app } = expressWs(express());
app.use(express.json());
app.use(cookieParser());

app.use("/assets", express.static("dist-ui/assets", { maxAge: "1y" }));
app.use((req, res, next) => {
	if (req.path.startsWith("/api")) {
		return next();
	}

	return res.sendFile("dist-ui/index.html", { root: "." });
});

app.use("/api", (await import("./api.js")).apiRouter);

app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
	console.error(err);
	if (err instanceof ZodError) {
		res.status(400).json(err.errors);
	} else {
		res.status(500).send("Internal server error");
	}
});

app.listen(80, () => {
	console.log("Listening on port 80");
});
