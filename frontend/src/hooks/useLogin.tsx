// hooks/useLogin.js
import { useCallback, useContext } from 'react';
import { UserContext } from '../context/UserContext';


const useLogin = () => {
  const contextValue = useContext(UserContext);


//   const handleLogin = useCallback(() => {
//     if (!contextValue || !contextValue.userData || !contextValue.userData.email) {
//       const currentUrl = encodeURIComponent(window.location.href);
//       fetch(`/login?referrer=${currentUrl}`, {
//           method: 'GET',
//           redirect: 'manual'
//       })
//       .then(response => {
//           if (response.ok) {
//               if (contextValue) {
//                   contextValue.setShouldRefetch(true);
//               }
//           } else {
//               console.error('Failed to initiate login process:', response.statusText);
//           }
//       });
//     }
//   }, []);  // Empty dependencies array
    const handleLogin = () => {
        if (!contextValue || !contextValue.userData || !contextValue.userData.email) {
            const currentUrl = encodeURIComponent(window.location.href);
            // Using window.location to navigate
            window.location.href = `/login?referrer=${currentUrl}`;
        }
    };


    return handleLogin;
};


export default useLogin;



