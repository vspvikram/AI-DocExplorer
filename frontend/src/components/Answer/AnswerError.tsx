import { Stack, PrimaryButton } from "@fluentui/react";
import { ErrorCircle24Regular } from "@fluentui/react-icons";


import styles from "./Answer.module.css";
import useLogin from "../../hooks/useLogin";


interface Props {
    error: string;
    onRetry: () => void;
}


export const AnswerError = ({ error, onRetry }: Props) => {
    const handleLogin = useLogin();
    const isLoginRequired = error.includes('login_required');


    return (
        <Stack className={styles.answerContainer} verticalAlign="space-between">
            <ErrorCircle24Regular aria-hidden="true" aria-label="Error icon" primaryFill="red" />


            <Stack.Item grow>
                <p className={styles.answerText}>{error}</p>
            </Stack.Item>


            {isLoginRequired ? (
                <PrimaryButton className={styles.retryButton} onClick={handleLogin} text="Login" />
            ) : (
                <PrimaryButton className={styles.retryButton} onClick={onRetry} text="Retry" />
            )}
        </Stack>
    );
};



