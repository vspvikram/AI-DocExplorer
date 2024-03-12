import React from 'react';
import styles from './ChatHistoryPanel.module.css';
import useLogin from '../../hooks/useLogin';  // Assuming useLogin is located in hooks directory


export const ChatHistoryNoUser: React.FC = () => {
    const handleLogin = useLogin();


    return (
        <div className={styles.container}>
            <div className={styles.messageBox}>
                <p className={styles.message}>Login to see your chat history...</p>
                <button className={styles.loginButton} onClick={handleLogin}>Login</button>
            </div>
        </div>
    );
};


export const ChatHistoryEmpty: React.FC = () => {
    return (
        <div className={styles.containerNoChat}>
            <div className={styles.textContainerNoChat}>
                <p className={styles.textNoChat}>
                    No previous chat sessions found. 
                </p>
                <p className={styles.subTextNoChat}>
                    Start a new chat to see it appear here!
                </p>
            </div>
        </div>
    );
};


// export const ChatHistoryEmpty: React.FC = () => {


//     return (
//         <div className={styles.container}>
//             <div className={styles.messageBox}>
//                 <p className={styles.message}>No previous chat sessions found. Start a new chat to see it appear here!</p>
//             </div>
//         </div>
//     );
// };


// export default ChatHistoryEmpty;



