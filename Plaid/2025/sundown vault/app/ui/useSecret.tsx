import React from "react";

type State =
	| { kind: "Connecting" }
	| { kind: "Connected" }
	| { kind: "Watching"; name: string }
	| { kind: "Waiting"; name: string; time: string }
	| { kind: "Revealed"; name: string; secret: string };

export const useSecret = (id: string) => {
	const [state, setState] = React.useState<State>({ kind: "Connecting" });

	React.useEffect(() => {
		const ws = new WebSocket("/api/ws");

		ws.addEventListener("message", (message) => {
			const data = JSON.parse(message.data);

			if (data.error !== undefined) {
				alert(data.error);
				return;
			}

			switch (data.kind) {
				case "Connected": {
					setState({ kind: "Connected" });
					ws.send(JSON.stringify({ command: "open", id }));
					break;
				}

				case "Watch": {
					setState({ kind: "Watching", name: data.name });
					break;
				}

				case "Update": {
					setState((oldState) => ({
						kind: "Waiting",
						name: "name" in oldState ? oldState.name : "",
						time: data.remaining,
					}));
					break;
				}

				case "Reveal": {
					setState((oldState) => ({
						kind: "Revealed",
						name: "name" in oldState ? oldState.name : "",
						secret: data.secret,
					}));
					break;
				}
			}
		});

		ws.addEventListener("close", () => {
			setState({ kind: "Connecting" });
		});

		return () => {
			ws.close();
		};
	}, [id]);

	return state;
};
