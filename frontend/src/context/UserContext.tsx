import React, { useState, createContext, ReactNode, useCallback } from 'react';


// Define a type for a chat session
export type ChatSession = {
    id: string;
    chatSessionName: string;
    _ts: number;
};


// Define a type for the user data
export type UserData = {
    firstName: string | null;
    lastName: string | null;
    email: string | null;
    session_id: string | null;
} | null;


// Define a type for the context value
type UserContextValue = {
    userData: UserData;
    setUserData: React.Dispatch<React.SetStateAction<UserData>>;
    chatSessions: ChatSession[];
    setChatSessions: React.Dispatch<React.SetStateAction<ChatSession[]>>;
    refetchUserData: () => void;
    shouldRefetch: boolean;
    setShouldRefetch: React.Dispatch<React.SetStateAction<boolean>>;
    error: string | null;
    setError: React.Dispatch<React.SetStateAction<string | null>>;
};


// Create a default user data object
const defaultUserData: UserData = {
    firstName: null,
    lastName: null,
    email: null,
    session_id: null,
};


// Create the context with a default value
export const UserContext = createContext<UserContextValue | null>(null);


type UserContextProviderProps = {
    children: ReactNode;
};


// Create a provider component
export const UserContextProvider: React.FC<UserContextProviderProps> = ({ children }) => {
    const [userData, setUserData] = useState<UserData>(defaultUserData);
    const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);


    const [shouldRefetch, setShouldRefetch] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);


    const refetchUserData = useCallback(() => {  // define the refetchUserData function using useCallback
        fetch('/check_login')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch user data');
                }
                return response.json();
            })
            .then(data => {
                if (data.isLoggedIn) {
                    setUserData({
                        firstName: data.userData.firstName,
                        lastName: data.userData.lastName,
                        email: data.userData.email,
                        session_id: data.userData.session_id  // or set it to data.session_id if it's returned from the server
                    });
                    setChatSessions(data.chatSessions);
                } else {
                    setUserData(null);
                    setChatSessions([]);
                }
            })
            .catch(error => {
                setError(error.message);
            });
    }, [setError]);


    const value: UserContextValue = {
        userData,
        setUserData,
        chatSessions,
        setChatSessions,
        refetchUserData,
        shouldRefetch,
        setShouldRefetch,
        error,
        setError,
    };


    return (
        <UserContext.Provider value={value}>
            {children}
        </UserContext.Provider>
    );
};



