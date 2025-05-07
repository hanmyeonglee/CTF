import React from "react";
import { Link, Outlet } from "react-router-dom";

import { useUser } from "./useUser";

import styles from "./Page.module.scss";

export const Page = () => {
	const { user, logout } = useUser();

	return (
		<div className={styles.page}>
			<div className={styles.header}>
				<Link to="/" className={styles.link + " " + styles.homeLink}>
					The Sundown Vault
				</Link>
				{user.loading ? (
					<div className={styles.user}>Loading...</div>
				) : user.value === undefined ? (
					<Link to="/login" className={styles.link + " " + styles.login}>
						Login
					</Link>
				) : (
					<>
						<Link to="/secret/my" className={styles.link}>
							My Secrets
						</Link>
						<Link to="/secret/create" className={styles.link}>
							Create Secret
						</Link>
						<div className={styles.user}>{user.value.user}</div>
						<div className={styles.link} onClick={logout}>
							Logout
						</div>
					</>
				)}
			</div>
			<div className={styles.content}>
				<Outlet />
			</div>
		</div>
	);
};
