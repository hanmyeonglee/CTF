import { DateTime } from "luxon";
import React from "react";

import { useUser } from "./useUser";

interface Secret {
	id: string;
	name: string;
	createdAt: string;
	revealAt: string;
}

interface MySecretsContextValue {
	secrets: {
		loading: boolean;
		value?: Secret[];
	};
	createSecret: (name: string, secret: string, revealAt: DateTime) => Promise<string>;
}

const MySecretsContext = React.createContext<MySecretsContextValue | undefined>(undefined);

export const MySecretsProvider = ({ children }: { children: React.ReactNode }) => {
	const { user } = useUser();
	const [secrets, setSecrets] = React.useState<MySecretsContextValue["secrets"]>({ loading: true });

	const refresh = React.useCallback(async () => {
		if (user.loading) {
			setSecrets({ loading: true });
			return;
		}

		if (user.value === undefined) {
			setSecrets({ loading: false });
			return;
		}

		setSecrets({ loading: true });
		const res = await fetch("/api/secrets/my");
		if (res.ok) {
			const { secrets } = await res.json();
			setSecrets({ loading: false, value: secrets });
		} else {
			setSecrets({ loading: false });
		}
	}, [user]);

	const createSecret = React.useCallback(
		async (name: string, secret: string, revealAt: DateTime) => {
			const res = await fetch("/api/secrets/create", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					name,
					secret,
					revealAt: revealAt.setZone("UTC").toISO(),
				}),
			});

			if (res.ok) {
				await refresh();
				const json = await res.json();
				return json.id;
			} else {
				throw new Error("Failed to create secret");
			}
		},
		[refresh],
	);

	React.useEffect(() => {
		refresh();
	}, [refresh]);

	return <MySecretsContext.Provider value={{ secrets, createSecret }}>{children}</MySecretsContext.Provider>;
};

export const useMySecrets = () => {
	const context = React.useContext(MySecretsContext);
	if (context === undefined) {
		throw new Error("useMySecrets must be used within a MySecretsProvider");
	}
	return context;
};
