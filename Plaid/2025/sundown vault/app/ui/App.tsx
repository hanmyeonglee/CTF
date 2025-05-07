import React from "react";
import { RouterProvider, createBrowserRouter } from "react-router-dom";

import { CreateSecret } from "./CreateSecret";
import { Home } from "./Home";
import { Login } from "./Login";
import { MySecrets } from "./MySecrets";
import { Page } from "./Page";
import { Register } from "./Register";
import { Secret } from "./Secret";
import { MySecretsProvider } from "./useMySecrets";
import { UserProvider } from "./useUser";

const router = createBrowserRouter([
	{
		Component: Page,
		children: [
			{
				path: "/",
				Component: Home,
			},
			{
				path: "/login",
				Component: Login,
			},
			{
				path: "/register",
				Component: Register,
			},
			{
				path: "/secret/create",
				Component: CreateSecret,
			},
			{
				path: "/secret/my",
				Component: MySecrets,
			},
			{
				path: "/secret/:id",
				Component: Secret,
			},
			{
				path: "*",
				Component: () => <h1>Not Found</h1>,
			},
		],
	},
]);

export const App = () => (
	<UserProvider>
		<MySecretsProvider>
			<RouterProvider router={router} />
		</MySecretsProvider>
	</UserProvider>
);
