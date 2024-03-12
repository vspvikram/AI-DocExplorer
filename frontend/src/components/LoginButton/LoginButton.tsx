// LoginButton.tsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import useLogin from '../../hooks/useLogin';


const LoginButton: React.FC = () => {
  const handleLogin = useLogin();
  // const navigate = useNavigate();


  // const handleLoginClick = () => {
  //   navigate('/login');
  // };


  return (
    <button className='loginButton' onClick={handleLogin}>Login</button>
  );
};


export default LoginButton;



