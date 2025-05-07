import React from "react";

import styles from "./Callout.module.scss";

interface Props {
	children: React.ReactNode;
}

export const Callout = (props: Props) => <div className={styles.callout}>{props.children}</div>;
