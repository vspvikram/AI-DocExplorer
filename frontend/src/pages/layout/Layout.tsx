import React, { useState, useEffect, useContext } from "react"; // vik
import { Outlet, NavLink, Link, useNavigate } from "react-router-dom";
import { UserContext } from "../../context/UserContext"; // vik
import LoginButton from "../../components/LoginButton/LoginButton";


// import github from "../../assets/github.svg";


import styles from "./Layout.module.css";


function useVersion() {
    const [version, setVersion] = React.useState<string>('');


    useEffect(() => {
        fetch('/version')
            .then(response => response.json())
            .then(data => {
                setVersion(data.version);
            });
    }, []);


    return version;
}


function getCookie(name: string): string | null {
    const value = "; " + document.cookie;
    const parts = value.split("; " + name + "=");
    if (parts.length === 2) {
        const cookieValue = parts.pop();
        if (cookieValue) {
            return cookieValue.split(";").shift() || null;
        }
    }
    return null;
}


function checkShouldRefetch(): boolean {
    const shouldRefetchCookie = getCookie('shouldRefetch');
    return shouldRefetchCookie === 'true';
}


function setCookie(name: string, value: string, days: number): void {
    const date = new Date();
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
    const expires = "; expires=" + date.toUTCString();
    document.cookie = name + "=" + value + expires + "; path=/";
}


const Layout = () => {
    const version = useVersion(); // vik: adding version number to the header
    const contextValue = useContext(UserContext); // vik: adding user context
    const navigate = useNavigate();


    // const [shouldFetch, setShouldFetch] = useState(true);  // Initialize shouldFetch flag to true


    // useEffect(() => {
    //     if (contextValue && contextValue.shouldRefetch) {
    //         contextValue.refetchUserData();
    //         contextValue.setShouldRefetch(false);  // Set shouldFetch to false after fetching
    //     }
    // }, [contextValue]);
    useEffect(() => {
        // checkShouldRefetch is a function that checks the session or cookie for the flag
        const shouldRefetchFromSession = checkShouldRefetch();
        if (shouldRefetchFromSession && contextValue) {
            contextValue.setShouldRefetch(true);
            setCookie('shouldRefetch', 'false', 10);  // Reset flag after fetching
        }
    }, [contextValue]);
    
    useEffect(() => {
        if (contextValue && contextValue.shouldRefetch) {
            contextValue.refetchUserData();
            contextValue.setShouldRefetch(false);  // Reset flag after fetching
        }
    }, [contextValue]);


    const { refetchUserData } = useContext(UserContext) || {};  // vik: adding user context
    useEffect(() => {
        if (refetchUserData) {
        refetchUserData();
        }
    }, [refetchUserData]);


    // const handleLogin = () => {
    //     if (!contextValue || !contextValue.userData || !contextValue.userData.email) {
    //         navigate('/login');
    //     }
    // };
    // const handleLogin = () => {
    //     if (!contextValue || !contextValue.userData || !contextValue.userData.email) {
    //         const currentUrl = encodeURIComponent(window.location.href);
    //         fetch(`/login?referrer=${currentUrl}`, {
    //             method: 'GET',
    //             redirect: 'manual'
    //         })
    //         .then(response => {
    //             if (response.ok) {
    //                 if (contextValue) {
    //                     contextValue.setShouldRefetch(true);
    //                 }
    //             } else {
    //                 console.error('Failed to initiate login process:', response.statusText);
    //             }
    //         });
    //     }
    // };


    let userGreeting;
    if (contextValue && contextValue.userData) {
        const { firstName, lastName } = contextValue.userData;
        userGreeting = firstName && lastName ? `Hi ${firstName} ${lastName}` : null;  // set to null if names are not available
    } 
    
    return (
        <div className={styles.layout}>
        <header className={styles.header} role={"banner"}>
            <div className={styles.headerLeft}>
                <h3 className={styles.headerTitle}>Quantum AI Search Assistant - QASA</h3>
                <div className={styles.version}>(version: {version})</div>
            </div>
            <nav className={styles.nav}>
                <ul className={styles.headerNavList}>
                    <li>
                        <NavLink to="/" className={({ isActive }) => (isActive ? styles.headerNavPageLinkActive : styles.headerNavPageLink)}>
                            <div className={styles.logoIcon}></div>
                        </NavLink>
                    </li>
                </ul>
            </nav>
            <div className={styles.userGreeting}>
                {userGreeting}
            </div>
        </header>
            <Outlet />
        </div>
    );
};


export default Layout;



