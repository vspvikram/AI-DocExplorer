// ChatHistoryPanel.tsx
import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
// import chatSessionIcon from '../../assets/chatSessionIcon.svg';
import styles from './ChatHistoryPanel.module.css';
import { UserContext } from '../../context/UserContext';
import { ChatHistoryNoUser, ChatHistoryEmpty } from './ChatHistoryEmpty';


export type ChatSession = {
    id: string;
    chatSessionName: string;
};


type Props = {
    // chatSessions: ChatSession[];
    handleSessionClick: (sessionId: string) => void;
};




const ChatHistoryPanel: React.FC<Props> = ({ handleSessionClick }) => {
    const userContext = useContext(UserContext);


    if (!userContext) {
        throw new Error('UserContext not provided');
    }


    const { chatSessions, userData } = userContext;


    return (
        <div className={styles.chatHistoryPanel}>
            <h2 className={styles.chatHistoryHeading}>Chat Sessions</h2>
            {userData?.email ? (
                <div className={styles.chatSessionListContainer}>
                    {chatSessions.length > 0 ? (
                        <ul className={styles.chatSessionList}>
                            {chatSessions.map(session => (
                                <li key={session.id} className={styles.chatSessionItem}>
                                    <Link 
                                        to={`/chatSession/${session.id}`} 
                                        onClick={() => handleSessionClick(session.id)}
                                        className={styles.chatSessionLink}
                                    >
                                        <div className={styles.chatIcon}></div>
                                        <div className={`${styles.sessionName} ${styles.truncate}`}>
                                            {session.chatSessionName}
                                        </div>
                                    </Link>
                                </li>
                            ))}
                        </ul>
                    ) : (
                        <ChatHistoryEmpty/>
                    )}
                </div>
            ) : (<ChatHistoryNoUser/>)
            }
        </div>
    );
};


export default ChatHistoryPanel;





