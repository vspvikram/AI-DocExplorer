import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom"; // BrowserRouter as Router instead of HashRouter
import { initializeIcons } from "@fluentui/react";


import "./index.css";


import Layout from "./pages/layout/Layout";
import NoPage from "./pages/NoPage";
import Chat from "./pages/chat/Chat";


// vik: import the context provider
import { UserContextProvider } from "./context/UserContext";


initializeIcons();


export default function App() {
    return (
        <React.StrictMode>
            <UserContextProvider>  {/* Wrap your components with UserContextProvider */}
                <BrowserRouter>
                    <Routes>
                        <Route path="/" element={<Layout />}>
                            <Route index element={<Chat />} />
                            {/* Vik: New Route for chat sessions */}
                            <Route path="chatSession/:sessionId" element={<Chat />} />
                            <Route path="*" element={<NoPage />} />
                        </Route>
                    </Routes>
                </BrowserRouter>
            </UserContextProvider>
        </React.StrictMode>
    );
}


ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);



