import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./login.css";
function Login() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: "",
    password: ""
  });

  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (data.error) {
        setError(data.error);
      } else {
        if (data.user?.username) {
          localStorage.setItem("auth_username", data.user.username);
        }
        navigate("/analyze");
      }

    } catch (err) {
      setError("Server error");
    }
  };

  return (
    <div className="auth-bg">
      <div className="auth-container">
        <div className="auth-card">

          <div className="auth-left">

            <div className="auth-logo">
              <i className="fa-solid fa-burger"></i> System logo
            </div>

            <h2 className="auth-title">Welcome to login system</h2>
            <p className="auth-subtitle">
              Sign in by entering the information below
            </p>

            {error && (
              <div style={{color:"#f857a6",textAlign:"center",marginBottom:"12px"}}>
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="auth-form">

              <div className="auth-input-group">
                <i className="fa fa-user"></i>
                <input
                  type="text"
                  name="username"
                  placeholder="Username or Email"
                  required
                  onChange={handleChange}
                />
              </div>

              <div className="auth-input-group">
                <i className="fa fa-lock"></i>
                <input
                  type="password"
                  name="password"
                  placeholder="Password"
                  required
                  onChange={handleChange}
                />
                <i className="fa fa-eye auth-eye"></i>
              </div>

              <div className="auth-options">
                <label className="auth-remember">
                  <input type="checkbox" name="remember" /> Remember me
                </label>

                <a href="#" className="auth-forgot">
                  Forgot Password?
                </a>
              </div>

              <button type="submit" className="auth-btn">
                Login
              </button>

            </form>

            <div className="auth-social">
              <a href="#" className="auth-social-btn fb">
                <i className="fab fa-facebook-f"></i>
              </a>

              <a href="#" className="auth-social-btn tw">
                <i className="fab fa-twitter"></i>
              </a>

              <a href="#" className="auth-social-btn gg">
                <i className="fab fa-google-plus-g"></i>
              </a>
            </div>

            <div className="auth-switch">
              Don't have an account? <a href="/signup">Sign up</a>
            </div>

          </div>

          <div className="auth-right">
            <div className="auth-bg-logo">
              <i className="fa-solid fa-burger"></i>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

export default Login;