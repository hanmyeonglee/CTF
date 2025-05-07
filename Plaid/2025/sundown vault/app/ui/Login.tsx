import React from "react";
import { Link, useNavigate } from "react-router-dom";

import { Callout } from "./Callout";
import { useUser } from "./useUser";

export const Login = () => {
	const { login } = useUser();
	const navigate = useNavigate();
	const [username, setUsername] = React.useState("");
	const [password, setPassword] = React.useState("");
	const [submitting, setSubmitting] = React.useState(false);
	const [failed, setFailed] = React.useState(false);

	return (
		<>
			<h1>Login</h1>
			<form
				onSubmit={async (e) => {
					e.preventDefault();
					if (submitting) {
						return;
					}
					setSubmitting(true);
					setFailed(false);
					const ok = await login(username, password);
					setSubmitting(false);
					if (ok) {
						navigate("/");
					} else {
						setFailed(true);
					}
				}}
			>
				{failed && <Callout>Invalid username or password</Callout>}
				<label>
					<span>Username</span>
					<input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
				</label>
				<label>
					<span>Password</span>
					<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
				</label>
				<input type="submit" value="Login" />
				<Link to="/register">Need an account?</Link>
			</form>
		</>
	);
};
