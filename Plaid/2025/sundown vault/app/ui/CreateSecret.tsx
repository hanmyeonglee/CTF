import { DateTime } from "luxon";
import React from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { Callout } from "./Callout";
import { useMySecrets } from "./useMySecrets";
import { useUser } from "./useUser";

import styles from "./CreateSecret.module.scss";

export const CreateSecret = () => {
	const { user } = useUser();
	const { createSecret } = useMySecrets();
	const navigate = useNavigate();
	const [name, setName] = React.useState("");
	const [secret, setSecret] = React.useState("");
	const [revealAt, setRevealAt] = React.useState(DateTime.now().toFormat("yyyy-MM-dd'T'HH:mm"));
	const [submitting, setSubmitting] = React.useState(false);
	const [failed, setFailed] = React.useState(false);
	const [now, setNow] = React.useState(DateTime.now());

	React.useEffect(() => {
		const interval = setInterval(() => {
			setNow(DateTime.now());
		}, 250);
		return () => clearInterval(interval);
	});

	if (user.loading) {
		return <div>Loading...</div>;
	} else if (user.value === undefined) {
		return <Navigate to="/login" />;
	}

	const revealTimeValid = DateTime.fromISO(revealAt) > now;

	return (
		<>
			<h1>Create Secret</h1>
			<form
				className={styles.form}
				onSubmit={async (e) => {
					e.preventDefault();
					if (submitting) {
						return;
					}
					setSubmitting(true);
					try {
						const id = await createSecret(name, secret, DateTime.fromISO(revealAt));
						navigate(`/secret/${id}`);
					} catch (error) {
						setFailed(true);
						setSubmitting(false);
					}
				}}
			>
				{failed && <Callout>Failed to create secret</Callout>}
				<label>
					<span>Name</span>
					<input type="text" value={name} onChange={(e) => setName(e.target.value)} />
				</label>
				<label>
					<span>Secret</span>
					<input type="text" value={secret} onChange={(e) => setSecret(e.target.value)} />
				</label>
				<label>
					<span>Reveal At</span>
					<input type="datetime-local" value={revealAt} onChange={(e) => setRevealAt(e.target.value)} />
				</label>
				<label>
					<span></span>
					{revealTimeValid ? (
						<span className={styles.relative}>{DateTime.fromISO(revealAt).toRelative()}</span>
					) : (
						<span className={styles.relative + " " + styles.error}>Reveal time must be in the future</span>
					)}
				</label>
				<input type="submit" value="Create" disabled={!revealTimeValid} />
			</form>
		</>
	);
};
