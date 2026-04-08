import React, { useState } from "react";
import "./signup.css";

function Signup() {

  const [formData, setFormData] = useState({
    username: "",
    email: "",
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
      const response = await fetch("http://localhost:5000/signup", {
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
        alert("Signup Successful");
      }

    } catch (err) {
      setError("Server Error");
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

            <h2 className="auth-title">Create your account</h2>
            <p className="auth-subtitle">
              Sign up by entering the information below
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
                  placeholder="Username"
                  required
                  onChange={handleChange}
                />
              </div>

              <div className="auth-input-group">
                <i className="fa fa-envelope"></i>
                <input
                  type="email"
                  name="email"
                  placeholder="Email"
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

              <button type="submit" className="auth-btn">
                Sign Up
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
              Already have an account? <a href="/login">Login</a>
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

export default Signup;