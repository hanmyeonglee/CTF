import { DateTime } from "luxon";
import React from "react";
import { Link, Navigate } from "react-router-dom";

import { useMySecrets } from "./useMySecrets";
import { useUser } from "./useUser";

import styles from "./MySecrets.module.scss";

export const MySecrets = () => {
	const { user } = useUser();
	const { secrets } = useMySecrets();

	if (user.loading) {
		return <div>Loading...</div>;
	} else if (user.value === undefined) {
		return <Navigate to="/login" />;
	} else if (secrets.loading) {
		return <div>Loading...</div>;
	} else if (secrets.value === undefined) {
		return <div>Error</div>;
	}

	return (
		<>
			<h1>My Secrets</h1>
			<div className={styles.list}>
				{secrets.value.length === 0 ? (
					<div className={styles.empty}>
						No secrets yet. <Link to="/secret/create">Create one here.</Link>
					</div>
				) : (
					<>
						<div className={styles.header}>
							<div className={styles.name}>Secret</div>
							<div className={styles.revealAt}>Reveal At</div>
							<div className={styles.createdAt}>Created At</div>
						</div>
						{secrets.value.map((secret) => (
							<Link to={`/secret/${secret.id}`} className={styles.secret} key={secret.id}>
								<div className={styles.name}>{secret.name}</div>
								<div className={styles.revealAt}>
									{DateTime.fromISO(secret.revealAt)
										.setZone("local")
										.toLocaleString(DateTime.DATETIME_SHORT)}
								</div>
								<div className={styles.createdAt}>
									{DateTime.fromISO(secret.createdAt)
										.setZone("local")
										.toLocaleString(DateTime.DATETIME_SHORT)}
								</div>
							</Link>
						))}
					</>
				)}
			</div>
		</>
	);
};
