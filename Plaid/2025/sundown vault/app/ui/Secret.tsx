import React from "react";
import { Navigate, useParams } from "react-router-dom";

import { useSecret } from "./useSecret";

import styles from "./Secret.module.scss";

export const Secret = () => {
	const { id } = useParams();
	const [copied, setCopied] = React.useState(false);

	if (id === undefined) {
		return <Navigate to="/" />;
	}

	const state = useSecret(id);

	const copyCallback = React.useCallback(() => {
		navigator.clipboard.writeText(window.location.href);
		setCopied(true);
	}, []);

	const copyButton = (
		<a href="#" onClick={copyCallback} className={styles.copyButton}>
			{copied ? "Copied!" : "Copy Link"}
		</a>
	);

	switch (state.kind) {
		case "Connecting":
		case "Connected": {
			return (
				<div className={styles.secret}>
					<h1>...</h1>
					<div className={styles.message}>Loading...</div>
				</div>
			);
		}

		case "Watching": {
			return (
				<div className={styles.secret}>
					<h1>{state.name}</h1>
					<div className={styles.message}>Waiting for reveal</div>
					{copyButton}
				</div>
			);
		}

		case "Waiting": {
			return (
				<div className={styles.secret}>
					<h1>{state.name}</h1>
					<div className={styles.timer}>Will be revealed in {state.time}</div>
					{copyButton}
				</div>
			);
		}

		case "Revealed": {
			return (
				<div className={styles.secret}>
					<h1>{state.name}</h1>
					<div className={styles.content}>{state.secret}</div>
					{copyButton}
				</div>
			);
		}

		default: {
			return (
				<div className={styles.secret}>
					<h1>Error</h1>
					<div className={styles.message}>An error occurred</div>
				</div>
			);
		}
	}
};
