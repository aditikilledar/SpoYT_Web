import { useEffect } from "react";

const GoogleLoginButton = ({ onLogin }) => {
    useEffect(() => {
        /* Initialize Google Sign-In */
        window.google.accounts.id.initialize({
            client_id: "510736806416-gv18frl89imv6o4jacc3lvl10d8pmn6p.apps.googleusercontent.com",
            callback: handleCredentialResponse
        });

        /* Render the Google Sign-In button */
        window.google.accounts.id.renderButton(
            document.getElementById("googleSignInDiv"),
            { theme: "outline", size: "large" }
        );
    }, []);

    /* Handle Sign-In Response */
    const handleCredentialResponse = (response) => {
        console.log("Google Login Token:", response.credential);
        onLogin(response.credential); // Pass token to parent component for authentication
    };

    return <div id="googleSignInDiv"></div>;
};

export default GoogleLoginButton;
