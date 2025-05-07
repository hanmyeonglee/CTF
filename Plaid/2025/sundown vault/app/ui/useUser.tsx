import React from "react";

interface User {
	user: string;
}

interface UserContextValue {
	user: {
		loading: boolean;
		value?: User;
	};
	login: (username: string, password: string) => Promise<boolean>;
	register: (username: string, password: string) => Promise<boolean>;
	logout: () => void;
}

const UserContext = React.createContext<UserContextValue | undefined>(undefined);

export const UserProvider = ({ children }: { children: React.ReactNode }) => {
	const [user, setUser] = React.useState<UserContextValue["user"]>({
		loading: true,
	});

	const refresh = React.useCallback(async () => {
		setUser({ loading: true });
		const res = await fetch("/api/me");
		if (res.ok) {
			const user = await res.json();
			setUser({ loading: false, value: user });
		} else {
			setUser({ loading: false });
		}
	}, []);

	const login = React.useCallback(
		async (username: string, password: string) => {
			const res = await fetch("/api/login", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ username, password }),
			});

			if (res.ok) {
				await refresh();
				return true;
			} else {
				return false;
			}
		},
		[refresh],
	);

	const register = React.useCallback(
		async (username: string, password: string) => {
			const res = await fetch("/api/register", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ username, password }),
			});

			if (res.ok) {
				return true;
			} else {
				return false;
			}
		},
		[refresh],
	);

	const logout = React.useCallback(async () => {
		const res = await fetch("/api/logout", {
			method: "POST",
		});

		if (res.ok) {
			await refresh();
		}
	}, [refresh]);

	React.useEffect(() => {
		refresh();
	}, [refresh]);

	return <UserContext.Provider value={{ user, login, register, logout }}>{children}</UserContext.Provider>;
};

export const useUser = () => {
	const context = React.useContext(UserContext);
	if (!context) {
		throw new Error("useUser must be used within a UserProvider");
	}
	return context;
};
