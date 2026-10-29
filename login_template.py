"""
JANI'S Perfume Studio - Luxury Security & Login Template.
Exclusive Owner Portal for Ashir87 with Deep Obsidian & Champagne Gold Theme.
"""

LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Login - JANI'S Perfume Studio</title>
    <!-- Fonts & Icons -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Cinzel:wght@600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">

    <!-- Mobile PWA Meta -->
    <meta name="theme-color" content="#070a12">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="ReelPilot">
    <link rel="manifest" href="/manifest.json">

    <style>
        :root {
            --bg-dark: #070a12;
            --gold-primary: #f59e0b;
            --gold-dark: #d97706;
            --gold-light: #fbbf24;
            --gold-gradient: linear-gradient(135deg, #b45309 0%, #f59e0b 50%, #fbbf24 100%);
            --card-bg: rgba(15, 23, 42, 0.85);
            --card-border: rgba(245, 158, 11, 0.25);
        }

        html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            background-color: var(--bg-dark);
            color: #f8fafc;
            font-family: 'Plus Jakarta Sans', sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            background-image: 
                radial-gradient(circle at 50% 15%, rgba(245, 158, 11, 0.12) 0%, transparent 55%),
                radial-gradient(circle at 80% 85%, rgba(99, 102, 241, 0.08) 0%, transparent 45%);
        }

        .login-wrapper {
            width: 100%;
            max-width: 440px;
            padding: 24px;
            box-sizing: border-box;
        }

        .login-card {
            background: var(--card-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--card-border);
            border-radius: 24px;
            padding: 38px 30px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), 0 0 35px rgba(245, 158, 11, 0.1);
            position: relative;
            transition: all 0.3s ease;
        }

        .login-card.shake {
            animation: shake-card 0.4s ease-in-out;
        }
        @keyframes shake-card {
            0%, 100% { transform: translateX(0); }
            20%, 60% { transform: translateX(-10px); }
            40%, 80% { transform: translateX(10px); }
        }

        .brand-title {
            font-family: 'Cinzel', serif;
            letter-spacing: 1.5px;
            font-weight: 800;
            background: var(--gold-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 1.55rem;
        }

        .crown-logo {
            width: 64px;
            height: 64px;
            border-radius: 50%;
            background: rgba(245, 158, 11, 0.12);
            border: 2px solid rgba(245, 158, 11, 0.35);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 16px auto;
            color: #f59e0b;
            font-size: 1.8rem;
            box-shadow: 0 0 20px rgba(245, 158, 11, 0.25);
        }

        .form-control {
            background: #0c1322 !important;
            border: 1px solid rgba(255, 255, 255, 0.12) !important;
            color: #fff !important;
            border-radius: 12px;
            padding: 12px 14px 12px 42px;
            font-size: 0.92rem;
            transition: all 0.2s;
        }
        .form-control:focus {
            border-color: #f59e0b !important;
            box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.25) !important;
        }

        .input-group-custom {
            position: relative;
            margin-bottom: 18px;
        }
        .input-icon {
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: #94a3b8;
            font-size: 0.95rem;
            z-index: 5;
        }
        .toggle-password {
            position: absolute;
            right: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: #94a3b8;
            cursor: pointer;
            z-index: 5;
            padding: 4px;
        }
        .toggle-password:hover {
            color: #f59e0b;
        }

        .btn-gold {
            background: var(--gold-gradient);
            color: #000;
            font-weight: 800;
            border: none;
            border-radius: 14px;
            padding: 14px;
            font-size: 0.95rem;
            letter-spacing: 0.5px;
            transition: all 0.2s;
            box-shadow: 0 6px 20px rgba(245, 158, 11, 0.35);
        }
        .btn-gold:hover {
            opacity: 0.95;
            transform: translateY(-1px);
            box-shadow: 0 8px 24px rgba(245, 158, 11, 0.45);
            color: #000;
        }

        .security-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(245, 158, 11, 0.08);
            border: 1px solid rgba(245, 158, 11, 0.2);
            color: #fbbf24;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 4px 12px;
            border-radius: 20px;
            margin-bottom: 20px;
        }

        #alert-box {
            display: none;
            border-radius: 10px;
            padding: 10px 14px;
            font-size: 0.82rem;
            font-weight: 600;
            margin-bottom: 16px;
        }
    </style>
</head>
<body>
    <div class="login-wrapper">
        <div class="login-card" id="loginCard">
            <div class="text-center">
                <div class="crown-logo">
                    <i class="fa-solid fa-crown"></i>
                </div>
                <h1 class="brand-title mb-1">JANI'S PERFUME</h1>
                <div class="text-white-50 small mb-2">ReelPilot Studio • Executive Portal</div>
                <div class="security-badge">
                    <i class="fa-solid fa-lock"></i> Restricted Access • Authorized Owner Only
                </div>
            </div>

            <!-- Dynamic Alert Box -->
            <div id="alert-box" class="alert alert-danger bg-danger bg-opacity-10 text-danger border-danger"></div>

            <form id="loginForm" onsubmit="handleLogin(event)">
                <div class="input-group-custom">
                    <i class="fa-solid fa-user input-icon"></i>
                    <input type="text" id="username" class="form-control" placeholder="Enter Username" required autofocus autocomplete="username">
                </div>

                <div class="input-group-custom">
                    <i class="fa-solid fa-key input-icon"></i>
                    <input type="password" id="password" class="form-control" placeholder="Enter Password" required autocomplete="current-password">
                    <i class="fa-solid fa-eye toggle-password" id="togglePassword" onclick="togglePasswordVisibility()"></i>
                </div>

                <div class="d-flex justify-content-between align-items-center mb-4 text-white-50" style="font-size: 0.8rem;">
                    <label class="d-flex align-items-center gap-2 cursor-pointer mb-0">
                        <input type="checkbox" id="rememberMe" checked class="form-check-input bg-dark border-secondary">
                        <span>Remember on this device</span>
                    </label>
                    <span class="text-warning"><i class="fa-solid fa-shield-halved me-1"></i>256-bit Encrypted</span>
                </div>

                <button type="submit" class="btn btn-gold w-100" id="loginBtn">
                    <i class="fa-solid fa-shield-check me-2"></i>Sign In to Studio
                </button>
            </form>

            <div class="text-center mt-4">
                <small class="text-white-50" style="font-size: 0.72rem;">
                    © 2026 JANI'S Perfume. Protected Social Automation Vault.
                </small>
            </div>
        </div>
    </div>

    <script>
        function togglePasswordVisibility() {
            const pwd = document.getElementById('password');
            const icon = document.getElementById('togglePassword');
            if (pwd.type === 'password') {
                pwd.type = 'text';
                icon.className = 'fa-solid fa-eye-slash toggle-password';
            } else {
                pwd.type = 'password';
                icon.className = 'fa-solid fa-eye toggle-password';
            }
        }

        async function handleLogin(e) {
            e.preventDefault();
            const u = document.getElementById('username').value.trim();
            const p = document.getElementById('password').value;
            const btn = document.getElementById('loginBtn');
            const card = document.getElementById('loginCard');
            const alertBox = document.getElementById('alert-box');

            alertBox.style.display = 'none';
            btn.disabled = true;
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i>Verifying Credentials...';

            try {
                const res = await fetch('/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: u, password: p })
                });
                const data = await res.json();

                if (data.success) {
                    btn.className = 'btn btn-success w-100 fw-bold';
                    btn.innerHTML = '<i class="fa-solid fa-check-double me-2"></i>Access Granted! Opening Studio...';
                    setTimeout(() => {
                        window.location.href = data.redirect || '/';
                    }, 600);
                } else {
                    btn.disabled = false;
                    btn.className = 'btn btn-gold w-100';
                    btn.innerHTML = '<i class="fa-solid fa-shield-check me-2"></i>Sign In to Studio';

                    alertBox.className = 'alert alert-danger bg-danger bg-opacity-20 text-danger border-danger';
                    alertBox.innerText = data.error || "Access Denied: Invalid Username or Password!";
                    alertBox.style.display = 'block';

                    card.classList.add('shake');
                    setTimeout(() => card.classList.remove('shake'), 450);
                    document.getElementById('password').value = '';
                    document.getElementById('password').focus();
                }
            } catch (err) {
                btn.disabled = false;
                btn.innerHTML = '<i class="fa-solid fa-shield-check me-2"></i>Sign In to Studio';
                alertBox.innerText = "Network error connecting to verification server.";
                alertBox.style.display = 'block';
            }
        }
    </script>
</body>
</html>
"""
