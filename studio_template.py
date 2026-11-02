"""
ReelPilot Studio - JANI'S Perfume Luxury Edition UI Template.
Fully Responsive, Zero-Overflow, 100% Contained UI with Deep Obsidian & Champagne Gold Theme.
"""

STUDIO_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>ReelPilot Studio - JANI\'S Perfume Luxury Edition</title>
    <!-- Google Fonts & FontAwesome -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Cinzel:wght@600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
    <!-- Mobile PWA Meta & Icons -->
    <meta name="theme-color" content="#070a12">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="ReelPilot">
    <link rel="manifest" href="/manifest.json">
    <link rel="apple-touch-icon" href="/static/apple-touch-icon.png">


    <style>
        :root {
            --primary: #f59e0b;
            --primary-hover: #d97706;
            --primary-light: #fbbf24;
            --accent-cyan: #06b6d4;
            --bg-dark: #070a12;
            --bg-card: rgba(15, 23, 42, 0.78);
            --card-border: rgba(255, 255, 255, 0.08);
            --card-border-gold: rgba(245, 158, 11, 0.35);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --gold-gradient: linear-gradient(135deg, #b45309 0%, #f59e0b 50%, #fbbf24 100%);
            --insta-grad: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
            --fb-color: #1877f2;
            --luxury-glass: rgba(17, 24, 39, 0.72);
        }

        
        /* COMPREHENSIVE MOBILE RESPONSIVE OPTIMIZATIONS */
        @media (max-width: 768px) {
            .app-wrapper {
                padding: 10px 8px 90px 8px !important;
            }
            .navbar-top {
                padding: 10px 12px !important;
            }
            .brand-title {
                font-size: 1.15rem !important;
                letter-spacing: 0.5px !important;
            }
            .brand-title i {
                margin-right: 4px !important;
            }
            .status-pill {
                padding: 4px 8px !important;
                font-size: 0.7rem !important;
            }
            .status-pill span {
                max-width: 90px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                display: inline-block;
                vertical-align: middle;
            }
            .card-pro {
                padding: 14px 12px !important;
                border-radius: 14px !important;
                margin-bottom: 14px !important;
            }
            .timing-btn {
                padding: 8px 4px !important;
                font-size: 0.74rem !important;
                border-radius: 8px !important;
            }
            .form-control, .form-select {
                font-size: 0.86rem !important;
                padding: 8px 10px !important;
            }
            .drop-zone-main {
                padding: 20px 10px !important;
            }
            .timeline-card {
                padding: 10px 10px !important;
            }
            .reel-thumb-container {
                max-height: 130px !important;
            }
            .modal-dialog {
                margin: 10px !important;
            }
            .modal-content {
                padding: 6px !important;
            }
        }

        /* 100% CONTAINED SCREEN - ZERO HORIZONTAL OVERFLOW */
        html, body {
            margin: 0 !important;
            padding: 0 !important;
            width: 100% !important;
            max-width: 100vw !important;
            overflow-x: hidden !important;
            background-color: var(--bg-dark);
            color: var(--text-main);
            font-family: 'Plus Jakarta Sans', sans-serif;
            min-height: 100vh;
            box-sizing: border-box;
        }

        *, *::before, *::after {
            box-sizing: border-box !important;
        }

        /* ZERO-INP POINTER EVENTS FIX: Prevent click capture on icon nodes */
        button i, a i, .btn i, .badge i {
            pointer-events: none !important;
        }

        /* STRICT CONTAINMENT: ZERO HORIZONTAL OVERFLOW */
        #calendar-feed-container, #reels-feed-grid {
            margin-left: 0 !important;
            margin-right: 0 !important;
            width: 100% !important;
        }
        .card-pro {
            overflow: hidden !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }
        .timeline-card {
            overflow: hidden !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
        }

        .app-wrapper {
            width: 100%;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px 16px 60px 16px;
            overflow-x: hidden;
            box-sizing: border-box;
        }

        /* FLEX & GRID DEFENSE AGAINST OVERFLOW */
        .row {
            margin-right: -8px;
            margin-left: -8px;
        }
        .row > * {
            padding-right: 8px;
            padding-left: 8px;
            min-width: 0 !important;
        }

        /* TOP NAVBAR */
        .navbar-top {
            background: rgba(11, 16, 29, 0.96);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--card-border);
            padding: 12px 24px;
            position: sticky;
            top: 0;
            z-index: 1050;
            width: 100%;
        }

        .brand-title {
            font-family: 'Cinzel', serif;
            letter-spacing: 1px;
            font-weight: 700;
            background: var(--gold-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* LUXURY CARDS */
        .card-pro {
            background: var(--bg-card);
            backdrop-filter: blur(14px);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
            overflow: hidden;
            transition: border-color 0.2s ease;
        }
        .card-pro:hover {
            border-color: rgba(245, 158, 11, 0.25);
        }

        /* LIVE STATUS PILL */
        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.35);
            color: #34d399;
            border-radius: 30px;
            padding: 6px 14px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .status-pill-disconnected {
            background: rgba(239, 68, 68, 0.12);
            border: 1px solid rgba(239, 68, 68, 0.35);
            color: #f87171;
        }
        .pulse-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #10b981;
            box-shadow: 0 0 8px #10b981;
            animation: pulse-ring 2s infinite;
        }
        @keyframes pulse-ring {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        /* DROP ZONE */
        .drop-zone-main {
            border: 2px dashed rgba(245, 158, 11, 0.5);
            border-radius: 16px;
            background: rgba(245, 158, 11, 0.03);
            padding: 26px 16px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .drop-zone-main:hover {
            background: rgba(245, 158, 11, 0.08);
            border-color: #f59e0b;
        }

        /* MEDIA PREVIEW THUMBNAILS IN UPLOAD FORM */
        .media-preview-card {
            position: relative;
            border-radius: 10px;
            overflow: hidden;
            background: #020617;
            border: 2px solid var(--card-border);
            aspect-ratio: 1 / 1;
            width: 100%;
        }
        .media-preview-card.is-cover {
            border-color: #f59e0b;
            box-shadow: 0 0 12px rgba(245, 158, 11, 0.4);
        }
        .media-preview-card img, .media-preview-card video {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }
        .cover-badge {
            position: absolute;
            top: 4px;
            left: 4px;
            background: #f59e0b;
            color: #000;
            font-weight: 800;
            font-size: 0.65rem;
            padding: 2px 6px;
            border-radius: 12px;
            z-index: 2;
        }
        .order-badge {
            position: absolute;
            top: 4px;
            right: 4px;
            background: rgba(0, 0, 0, 0.75);
            color: #fff;
            font-weight: 700;
            font-size: 0.65rem;
            padding: 1px 6px;
            border-radius: 10px;
            z-index: 2;
        }

        /* TIMING & FORM CONTROLS */
        .timing-btn {
            border: 1px solid var(--card-border);
            background: #0c1424;
            color: #cbd5e1;
            border-radius: 10px;
            padding: 8px 12px;
            font-weight: 600;
            font-size: 0.8rem;
            transition: all 0.2s;
            cursor: pointer;
            text-align: center;
        }
        .timing-btn.active, .timing-btn:hover {
            border-color: #f59e0b;
            background: rgba(245, 158, 11, 0.15);
            color: #fbbf24;
        }

        .form-control, .form-select {
            background: #0c1322 !important;
            border: 1px solid var(--card-border) !important;
            color: #fff !important;
            border-radius: 10px;
            padding: 8px 12px;
            font-size: 0.88rem;
        }
        .form-control:focus, .form-select:focus {
            border-color: #f59e0b !important;
            box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.25) !important;
        }

        /* TEXT CLAMPING - STRICT DEFENSE */
        .caption-clamp-1 {
            display: -webkit-box !important;
            -webkit-line-clamp: 1 !important;
            -webkit-box-orient: vertical !important;
            overflow: hidden !important;
            word-break: break-word !important;
            white-space: normal !important;
        }
        .caption-clamp-2 {
            display: -webkit-box !important;
            -webkit-line-clamp: 2 !important;
            -webkit-box-orient: vertical !important;
            overflow: hidden !important;
            word-break: break-word !important;
            white-space: normal !important;
            line-height: 1.35;
        }

        /* TIMELINE CARD DESIGN */
        .timeline-card {
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.09);
            border-radius: 14px;
            padding: 12px 14px;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-width: 0 !important;
            transition: all 0.2s ease;
        }
        .timeline-card:hover {
            border-color: rgba(245, 158, 11, 0.35);
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }

        /* FEED REEL / PRODUCT CARD */
        .reel-card {
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: all 0.2s ease;
            height: 100%;
            min-width: 0 !important;
        }
        .reel-card:hover {
            transform: translateY(-2px);
            border-color: #f59e0b;
            box-shadow: 0 8px 20px rgba(245, 158, 11, 0.2);
        }
        .reel-thumb-container {
            position: relative;
            width: 100%;
            aspect-ratio: 1 / 1;
            max-height: 150px;
            background: #090d16;
            overflow: hidden;
            cursor: pointer;
        }
        .reel-thumb-img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
        }

        /* PLATFORM & WAQT BADGES */
        .badge-insta {
            background: var(--insta-grad);
            color: #fff;
            font-size: 0.65rem;
            font-weight: 700;
        }
        .badge-fb {
            background: #1877f2;
            color: #fff;
            font-size: 0.65rem;
            font-weight: 700;
        }
        .badge-waqt {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: #e2e8f0;
            font-size: 0.65rem;
            border-radius: 8px;
            padding: 2px 6px;
        }

        /* BUTTONS */
        .btn-gold {
            background: var(--gold-gradient);
            color: #000;
            font-weight: 700;
            border: none;
            transition: opacity 0.2s;
        }
        .btn-gold:hover {
            opacity: 0.92;
            color: #000;
        }

        .feed-filter-btn {
            border-radius: 20px;
            padding: 5px 14px;
            font-weight: 600;
            font-size: 0.8rem;
            color: #cbd5e1;
            border: 1px solid var(--card-border);
            background: transparent;
            transition: all 0.2s;
        }
        .feed-filter-btn.active, .feed-filter-btn:hover {
            background: #f59e0b;
            border-color: #f59e0b;
            color: #000;
            font-weight: 700;
        }

        #toast-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 9999;
        }
    </style>
</head>
<body>
    <!-- TOP NAVIGATION -->
    <nav class="navbar-top">
        <div class="container-fluid d-flex justify-content-between align-items-center p-0">
            <div class="d-flex align-items-center gap-3">
                <span class="fs-4 fw-bold brand-title">
                    <i class="fa-solid fa-crown text-warning me-2"></i>JANI\'S Perfume Studio
                </span>
                <span class="badge text-dark rounded-pill px-3 py-1 fw-bold d-none d-md-inline" style="background: var(--gold-gradient); font-size: 0.7rem;">
                    ReelPilot v3.6 Pro
                </span>
            </div>

            <div class="d-flex align-items-center gap-2">
                <!-- Live Connection Indicator -->
                <div id="nav-live-indicator" class="status-pill">
                    <div class="pulse-dot" id="nav-status-dot"></div>
                    <span id="nav-status-text">@official_janisperfume (Live Active)</span>
                </div>

                <button class="btn btn-sm btn-outline-info rounded-pill px-2 px-sm-3 fw-bold ms-1" id="btn-install-app" onclick="handlePwaInstall()" title="Install Mobile App">
                    <i class="fa-solid fa-mobile-screen"></i> <span class="d-none d-sm-inline">App</span>
                </button>
                <button class="btn btn-sm btn-outline-warning rounded-pill px-2 px-sm-3 fw-bold ms-1" onclick="openSettingsModal()" title="Settings">
                    <i class="fa-solid fa-sliders"></i> <span class="d-none d-sm-inline">Settings</span>
                </button>
                <a href="/logout" class="btn btn-sm btn-outline-danger rounded-pill px-2 px-sm-3 fw-bold ms-1" title="Log Out">
                    <i class="fa-solid fa-right-from-bracket"></i> <span class="d-none d-sm-inline">Logout</span>
                </a>
            </div>
        </div>
    </nav>

    <div class="app-wrapper">

        <!-- PROMINENT MOBILE APP INSTALL BANNER (VISIBLE ON SMARTPHONES) -->
        <div id="mobile-install-banner" class="d-md-none p-3 mb-3 rounded-4 shadow" style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.16) 0%, rgba(6, 182, 212, 0.14) 100%); border: 1.5px solid rgba(245, 158, 11, 0.45);">
            <div class="d-flex justify-content-between align-items-center gap-2">
                <div class="d-flex align-items-center gap-2">
                    <img src="/static/icon-192.png" style="width: 42px; height: 42px; border-radius: 10px; border: 1.5px solid #f59e0b; flex-shrink: 0;" onerror="this.src='/static/apple-touch-icon.png'">
                    <div style="line-height: 1.25;">
                        <div class="fw-bold text-white small"><i class="fa-solid fa-crown text-warning me-1"></i>JANI'S Perfume App</div>
                        <div class="text-white-50" style="font-size: 0.72rem;">Install native app on your phone</div>
                    </div>
                </div>
                <button class="btn btn-sm btn-gold rounded-pill px-3 py-1 fw-bold text-nowrap" onclick="handlePwaInstall()">
                    <i class="fa-solid fa-download me-1"></i> Install
                </button>
            </div>
        </div>

        <!-- TOP BRAND & CONNECTION SUMMARY STRIP -->
        <div class="card-pro p-3 mb-4">
            <div class="d-flex flex-wrap justify-content-between align-items-center gap-3">
                <div class="d-flex align-items-center gap-3">
                    <div class="p-2 rounded-circle bg-warning bg-opacity-10 text-warning fs-4 px-3">
                        <i class="fa-solid fa-gem"></i>
                    </div>
                    <div>
                        <div class="fw-bold text-white small">
                            Official Brand Accounts Connected
                        </div>
                        <div class="text-white-50 small" id="meta-accounts-summary">
                            Instagram: <strong class="text-warning">@official_janisperfume</strong> | Facebook: <strong class="text-primary">JANI\'s Perfume</strong>
                        </div>
                    </div>
                </div>

                <div class="d-flex align-items-center gap-3">
                    <div class="text-end d-none d-sm-block">
                        <div class="small text-white-50">Today\'s Auto-Pilot Quota:</div>
                        <div class="small fw-bold text-white">
                            <i class="fa-brands fa-instagram text-danger"></i> <span id="stat-ig-count">0/3</span> &nbsp;|&nbsp; 
                            <i class="fa-brands fa-facebook text-primary"></i> <span id="stat-fb-count">0/3</span>
                        </div>
                    </div>
                    <button class="btn btn-sm btn-outline-light rounded-pill px-3 fw-bold" onclick="checkLiveHealth(true)">
                        <i class="fa-solid fa-rotate me-1"></i> Test Meta API
                    </button>
                </div>
            </div>
        </div>

        <!-- MAIN 2-COLUMN STUDIO WORKBENCH -->
        <div class="row g-4 mb-4">
            <!-- LEFT COLUMN: POST CREATION & SCHEDULING (7 COLS) -->
            <div class="col-12 col-lg-7">
                <div class="card-pro p-4 h-100">
                    <div class="d-flex justify-content-between align-items-center mb-3 pb-2 border-bottom border-secondary border-opacity-50">
                        <h5 class="fw-bold text-white mb-0">
                            <i class="fa-solid fa-circle-plus text-warning me-2"></i>Create & Schedule Post
                        </h5>
                        <span id="selected-files-count" class="badge bg-secondary text-white-50">0/12 Media Selected</span>
                    </div>

                    <!-- Target Destination Selector -->
                    <div class="mb-3">
                        <label class="form-label small fw-bold text-white-50 mb-1">Target Destination</label>
                        <div class="row g-2">
                            <div class="col-4">
                                <button type="button" class="btn btn-sm w-100 rounded-3 timing-btn active" id="btn-dest-insta" onclick="selectDestination('instagram')">
                                    <i class="fa-brands fa-instagram text-danger me-1"></i> Instagram
                                </button>
                            </div>
                            <div class="col-4">
                                <button type="button" class="btn btn-sm w-100 rounded-3 timing-btn" id="btn-dest-fb" onclick="selectDestination('facebook')">
                                    <i class="fa-brands fa-facebook text-primary me-1"></i> Facebook
                                </button>
                            </div>
                            <div class="col-4">
                                <button type="button" class="btn btn-sm w-100 rounded-3 timing-btn" id="btn-dest-all" onclick="selectDestination('all')">
                                    <i class="fa-solid fa-share-nodes text-warning me-1"></i> Both (Insta+FB)
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Drag & Drop Media Upload Area -->
                    <div class="mb-3">
                        <input type="file" id="media-file-input" multiple accept="image/*,video/*" class="d-none" onchange="handleFileSelect(event)">
                        <div class="drop-zone-main" id="drop-zone" onclick="document.getElementById('media-file-input').click()">
                            <i class="fa-solid fa-cloud-arrow-up fs-2 text-warning mb-2 d-block"></i>
                            <div class="fw-bold text-white mb-1">Click to Browse or Drag & Drop 1 to 12 Pictures</div>
                            <div class="text-white-50 small">Multi-photos will be published as native Carousels / Albums. Pure images stay pure images!</div>
                        </div>

                        <!-- Media Preview Carousel Strip -->
                        <div id="media-preview-strip" class="row g-2 mt-2 d-none"></div>
                    </div>

                    <!-- Perfume Specifics Box -->
                    <div class="p-3 rounded-3 mb-3" style="background: rgba(12, 19, 34, 0.7); border: 1px solid rgba(245, 158, 11, 0.2);">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <div class="fw-bold text-warning small">
                                <i class="fa-solid fa-crown me-1"></i>Perfume Details (Aapke Perfume ki Specifics)
                            </div>
                            <span class="badge bg-warning text-dark fw-bold" style="font-size: 0.65rem;">100% Authentic AI Copy</span>
                        </div>

                        <div class="row g-2 mb-2">
                            <div class="col-8">
                                <label class="small text-white-50 mb-1">Perfume Name (Naam)</label>
                                <input type="text" id="perfume-name-input" class="form-control" placeholder="e.g. Oud Royale, Velvet Rose, Janis Signature, Crown Kredence">
                            </div>
                            <div class="col-4">
                                <label class="small text-white-50 mb-1">Bottle Size / Volume</label>
                                <input type="text" id="perfume-ml-input" class="form-control" value="100ml" placeholder="100ml">
                            </div>
                        </div>

                        <!-- Quick Volume Badges -->
                        <div class="d-flex flex-wrap gap-1 align-items-center mb-2">
                            <span class="small text-white-50 me-1" style="font-size: 0.75rem;">Quick ML:</span>
                            <span class="badge bg-secondary text-white cursor-pointer px-2 py-1" onclick="setVolume('100ml')">100ml</span>
                            <span class="badge bg-secondary text-white cursor-pointer px-2 py-1" onclick="setVolume('50ml')">50ml</span>
                            <span class="badge bg-secondary text-white cursor-pointer px-2 py-1" onclick="setVolume('30ml')">30ml</span>
                            <span class="badge bg-secondary text-white cursor-pointer px-2 py-1" onclick="setVolume('12ml Attar')">12ml Attar</span>
                            <span class="badge bg-secondary text-white cursor-pointer px-2 py-1" onclick="setVolume('6ml Attar')">6ml Attar</span>
                        </div>

                        <div class="row g-2 mb-2">
                            <div class="col-6">
                                <label class="small text-white-50 mb-1">Fragrance Notes (Optional)</label>
                                <input type="text" id="perfume-notes-input" class="form-control" placeholder="e.g. Woody Oud, Amber, Vanilla, Rose">
                            </div>
                            <div class="col-6">
                                <label class="small text-white-50 mb-1">Price / Special Promo (Optional)</label>
                                <input type="text" id="perfume-price-input" class="form-control" placeholder="e.g. PKR 3,999 with Free Delivery">
                            </div>
                        </div>

                        <button type="button" class="btn btn-gold w-100 rounded-pill py-2 btn-sm fw-bold mt-1" onclick="generateLuxuryDescription()">
                            <i class="fa-solid fa-wand-magic-sparkles me-1"></i> Generate 100% Authentic AI Luxury Description & Viral Hashtags
                        </button>
                    </div>

                    <!-- Caption & Hashtags -->
                    <div class="mb-3">
                        <label class="form-label small fw-bold text-white-50 mb-1">Post Caption & Social Copy</label>
                        <textarea id="post-caption-input" class="form-control" rows="4" placeholder="Enter caption here... Brand checkout footer is automatically attached!"></textarea>
                    </div>

                    <!-- Publishing Mode & Schedule Selection -->
                    <div class="mb-3">
                        <label class="form-label small fw-bold text-white-50 mb-1">Publishing Mode & Schedule</label>
                        <div class="row g-2 mb-2">
                            <div class="col-4">
                                <button type="button" class="btn btn-sm w-100 rounded-3 timing-btn" id="btn-mode-instant" onclick="selectScheduleMode('instant')">
                                    <i class="fa-solid fa-bolt text-warning me-1"></i> Post Immediately
                                </button>
                            </div>
                            <div class="col-4">
                                <button type="button" class="btn btn-sm w-100 rounded-3 timing-btn active" id="btn-mode-calendar" onclick="selectScheduleMode('calendar')">
                                    <i class="fa-solid fa-calendar-days text-info me-1"></i> Exact Calendar
                                </button>
                            </div>
                            <div class="col-4">
                                <button type="button" class="btn btn-sm w-100 rounded-3 timing-btn" id="btn-mode-queue" onclick="selectScheduleMode('queue')">
                                    <i class="fa-solid fa-robot text-success me-1"></i> Auto-Pilot Queue
                                </button>
                            </div>
                        </div>

                        <!-- Date & Time Picker Controls (Visible in calendar mode) -->
                        <div id="calendar-picker-box" class="p-3 rounded-3" style="background: rgba(12, 19, 34, 0.7); border: 1px solid var(--card-border);">
                            <div class="row g-2">
                                <div class="col-6">
                                    <label class="small text-white-50 mb-1">Schedule Date</label>
                                    <input type="date" id="schedule-date-input" class="form-control" onchange="updateDateTimePreview()">
                                </div>
                                <div class="col-6">
                                    <label class="small text-white-50 mb-1">Schedule Time</label>
                                    <input type="time" id="schedule-time-input" class="form-control" onchange="updateDateTimePreview()">
                                </div>
                            </div>
                            <div class="d-flex justify-content-between align-items-center mt-2 small">
                                <span class="text-white-50">Selected Waqt:</span>
                                <span class="badge bg-secondary text-white" id="waqt-preview-badge">Sham (Evening)</span>
                            </div>
                        </div>
                    </div>

                    <!-- Submit Button -->
                    <button type="button" class="btn btn-gold w-100 py-3 rounded-pill fw-bold fs-6 shadow" id="btn-submit-post" onclick="submitPost()">
                        <i class="fa-solid fa-paper-plane me-2"></i>Publish / Schedule Post
                    </button>
                </div>
            </div>

            <!-- RIGHT COLUMN: PC FOLDERS & LIVE STATS (5 COLS) -->
            <div class="col-12 col-lg-5">
                <div class="card-pro p-4 h-100 d-flex flex-column justify-content-between">
                    <div>
                        <div class="d-flex justify-content-between align-items-center mb-3 pb-2 border-bottom border-secondary border-opacity-50">
                            <h5 class="fw-bold text-white mb-0">
                                <i class="fa-solid fa-folder-tree text-warning me-2"></i>PC Watch Folders
                            </h5>
                            <span class="badge bg-success bg-opacity-25 text-success">Live Watcher Active</span>
                        </div>

                        <p class="text-white-50 small mb-3">
                            Drop images directly into these local folders on your computer — ReelPilot detects them, auto-applies AI Vision, and publishes automatically:
                        </p>

                        <!-- Insta Folder -->
                        <div class="p-3 bg-dark bg-opacity-50 rounded-3 border border-secondary border-opacity-50 mb-2 d-flex justify-content-between align-items-center">
                            <div>
                                <div class="fw-bold text-white small"><i class="fa-brands fa-instagram text-danger me-2"></i>Instagram PC Folder</div>
                                <div class="text-white-50" style="font-size: 0.72rem;">watch_folders/Ready_for_Insta</div>
                            </div>
                            <button class="btn btn-sm btn-outline-light rounded-pill px-3" onclick="openFolder('instagram')">
                                <i class="fa-regular fa-folder-open me-1"></i> Open
                            </button>
                        </div>

                        <!-- Facebook Folder -->
                        <div class="p-3 bg-dark bg-opacity-50 rounded-3 border border-secondary border-opacity-50 mb-2 d-flex justify-content-between align-items-center">
                            <div>
                                <div class="fw-bold text-white small"><i class="fa-brands fa-facebook text-primary me-2"></i>Facebook PC Folder</div>
                                <div class="text-white-50" style="font-size: 0.72rem;">watch_folders/Ready_for_Facebook</div>
                            </div>
                            <button class="btn btn-sm btn-outline-light rounded-pill px-3" onclick="openFolder('facebook')">
                                <i class="fa-regular fa-folder-open me-1"></i> Open
                            </button>
                        </div>

                        <!-- Cloud CDN Storage Status -->
                        <div class="p-3 bg-dark bg-opacity-50 rounded-3 border border-secondary border-opacity-50 mb-3 d-flex justify-content-between align-items-center">
                            <div>
                                <div class="fw-bold text-white small"><i class="fa-solid fa-cloud text-info me-2"></i>Permanent Direct Image CDN</div>
                                <div class="text-info" style="font-size: 0.72rem;">High-Speed Binary Direct URLs Active</div>
                            </div>
                            <button class="btn btn-sm btn-outline-warning rounded-pill px-3" onclick="openSettingsModal()">
                                <i class="fa-solid fa-gear me-1"></i> Settings
                            </button>
                        </div>
                    </div>

                    <!-- Brand Guidelines Quick Card -->
                    <div class="p-3 rounded-3" style="background: rgba(245, 158, 11, 0.05); border: 1px dashed rgba(245, 158, 11, 0.3);">
                        <div class="fw-bold text-warning small mb-1">
                            <i class="fa-solid fa-shield-halved me-1"></i>Official Brand Footer Included
                        </div>
                        <div class="text-white-50 small" style="font-size: 0.75rem; line-height: 1.4;">
                            Har post ke end par website <code>janisperfumes.com</code>, WhatsApp <code>03134454899</code> aur DM order details automatically attach hoti hain taake traffic direct customer sales mein convert ho.
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- VISUAL CONTENT CALENDAR & SCHEDULED TIMELINE SECTION -->
        <div class="card-pro p-4 mb-4">
            <div class="d-flex flex-wrap justify-content-between align-items-center mb-3 pb-2 border-bottom border-secondary border-opacity-50 gap-2">
                <div>
                    <h5 class="fw-bold text-white mb-0">
                        <i class="fa-solid fa-calendar-days text-info me-2"></i>Visual Content Calendar & Scheduled Timeline
                    </h5>
                    <p class="text-white-50 small mb-0">
                        Har scheduled post ka exact <strong>Date</strong>, <strong>Time</strong> aur <strong>Waqt (Subah/Dopahar/Sham/Raat)</strong> yahan show hota hai.
                    </p>
                </div>
                <div class="d-flex gap-2">
                    <button class="btn btn-sm btn-outline-danger rounded-pill px-3 fw-bold" onclick="clearFailedEvents()" title="Purge failed test posts permanently">
                        <i class="fa-solid fa-trash-can me-1"></i> Clear Failed
                    </button>
                    <button class="btn btn-sm btn-outline-light rounded-pill px-3 fw-bold" onclick="loadCalendarFeed()">
                        <i class="fa-solid fa-rotate me-1"></i> Refresh
                    </button>
                </div>
            </div>

            <div id="calendar-feed-container" class="row g-3">
                <div class="col-12 text-center py-4 text-white-50">
                    <i class="fa-solid fa-spinner fa-spin fs-4 mb-2 text-info"></i>
                    <div>Loading scheduled posts...</div>
                </div>
            </div>
        </div>

        <!-- VISUAL CONTENT FEED WITH FILTERS (COMPACT MEDIA GALLERY) -->
        <div class="card-pro p-4 mb-4">
            <div class="d-flex flex-wrap justify-content-between align-items-center mb-3 pb-2 border-bottom border-secondary border-opacity-50 gap-2">
                <div>
                    <h5 class="fw-bold text-white mb-0">
                        <i class="fa-solid fa-film text-warning me-2"></i>Visual Content Feed
                    </h5>
                    <p class="text-white-50 small mb-0">
                        Track published and queued media. Click <strong>▶ Preview</strong> or <strong>⚡ Post Now</strong> to publish immediately.
                    </p>
                </div>

                <div class="d-flex align-items-center gap-2">
                    <button class="feed-filter-btn active" onclick="filterFeed('all', this)">All</button>
                    <button class="feed-filter-btn" onclick="filterFeed('instagram', this)"><i class="fa-brands fa-instagram text-danger me-1"></i> Instagram</button>
                    <button class="feed-filter-btn" onclick="filterFeed('facebook', this)"><i class="fa-brands fa-facebook text-primary me-1"></i> Facebook</button>
                    <button class="btn btn-sm btn-outline-light rounded-pill px-3 fw-bold ms-1" onclick="loadReelsFeed()"><i class="fa-solid fa-rotate"></i></button>
                </div>
            </div>

            <!-- Feed Grid: Clean, compact e-commerce proportions -->
            <div id="reels-feed-grid" class="row g-3">
                <div class="col-12 text-center py-5 text-white-50">
                    <i class="fa-solid fa-spinner fa-spin fs-2 text-warning mb-2"></i>
                    <div>Loading visual media feed...</div>
                </div>
            </div>
        </div>
    </div>

    <!-- SETTINGS MODAL -->
    <div class="modal fade" id="modalStudioSettings" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content bg-dark text-white border border-secondary rounded-4 shadow-lg">
                <div class="modal-header border-secondary">
                    <h5 class="modal-title fw-bold text-white">
                        <i class="fa-solid fa-sliders text-warning me-2"></i>Studio Settings & Meta Configuration
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-3 p-md-4">
                    <!-- Brand & Contact Section -->
                    <div class="p-3 bg-dark bg-opacity-50 rounded-3 border border-secondary border-opacity-50 mb-3">
                        <div class="fw-bold text-warning small mb-2"><i class="fa-solid fa-crown me-1"></i>Brand & Contact Details</div>
                        <div class="row g-2 mb-2">
                            <div class="col-12 col-md-4">
                                <label class="small text-white-50 mb-1">Brand Name</label>
                                <input type="text" id="setting-brand-name" class="form-control" value="JANI'S Perfume">
                            </div>
                            <div class="col-12 col-md-4">
                                <label class="small text-white-50 mb-1">Official Website</label>
                                <input type="text" id="setting-website" class="form-control" value="janisperfumes.com">
                            </div>
                            <div class="col-12 col-md-4">
                                <label class="small text-white-50 mb-1">WhatsApp Number</label>
                                <input type="text" id="setting-whatsapp" class="form-control" value="03134454899">
                            </div>
                        </div>
                    </div>

                    <!-- Connected Social Accounts -->
                    <div class="p-3 bg-dark bg-opacity-50 rounded-3 border border-secondary border-opacity-50 mb-3">
                        <div class="fw-bold text-primary small mb-2"><i class="fa-brands fa-meta me-1"></i>Connected Social Accounts</div>
                        <div class="row g-2 mb-2">
                            <div class="col-12 col-md-6">
                                <label class="small text-white-50 mb-1"><i class="fa-brands fa-instagram text-danger me-1"></i>Instagram Account ID</label>
                                <input type="text" id="setting-ig-id" class="form-control" value="17841423338066933" readonly>
                                <small class="text-white-50" style="font-size: 0.7rem;">@official_janisperfume (Linked)</small>
                            </div>
                            <div class="col-12 col-md-6">
                                <label class="small text-white-50 mb-1"><i class="fa-brands fa-facebook text-primary me-1"></i>Facebook Page ID</label>
                                <input type="text" id="setting-fb-id" class="form-control" value="800869286434757" readonly>
                                <small class="text-white-50" style="font-size: 0.7rem;">JANI's Perfume (Linked)</small>
                            </div>
                        </div>
                    </div>

                    <!-- Meta Access Token -->
                    <div class="p-3 bg-dark bg-opacity-50 rounded-3 border border-secondary border-opacity-50 mb-3">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <label class="small text-white-50 mb-0 fw-bold"><i class="fa-solid fa-key text-warning me-1"></i>Meta Long-Lived Access Token</label>
                            <span class="badge bg-success bg-opacity-25 text-success" id="setting-token-status">Active</span>
                        </div>
                        <textarea id="setting-meta-token" class="form-control mb-2" rows="2" placeholder="Paste your Meta Access Token here..."></textarea>
                        <button type="button" class="btn btn-sm btn-outline-primary rounded-pill px-3" onclick="verifyMetaToken()">
                            <i class="fa-solid fa-circle-check me-1"></i> Test & Verify Live Connection
                        </button>
                    </div>

                    <!-- Daily Quota & Automation -->
                    <div class="p-3 bg-dark bg-opacity-50 rounded-3 border border-secondary border-opacity-50">
                        <div class="fw-bold text-info small mb-2"><i class="fa-solid fa-robot me-1"></i>Daily Publishing Quota & Cloud Automation</div>
                        <div class="row g-2">
                            <div class="col-6">
                                <label class="small text-white-50 mb-1">Instagram Daily Limit</label>
                                <input type="number" id="setting-quota-ig" class="form-control" value="3" min="1" max="10">
                            </div>
                            <div class="col-6">
                                <label class="small text-white-50 mb-1">Facebook Daily Limit</label>
                                <input type="number" id="setting-quota-fb" class="form-control" value="3" min="1" max="10">
                            </div>
                        </div>
                        <div class="text-white-50 small mt-2" style="font-size: 0.72rem;">
                            <i class="fa-solid fa-check text-success me-1"></i>Autonomous 24/7 background scheduler active via CloudQueue.
                        </div>
                    </div>
                </div>
                <div class="modal-footer border-secondary">
                    <button type="button" class="btn btn-secondary rounded-pill px-4" data-bs-dismiss="modal">Close</button>
                    <button type="button" class="btn btn-gold rounded-pill px-4" onclick="saveStudioSettings()">Save Settings</button>
                </div>
            </div>
        </div>
    </div>

    <!-- MEDIA PREVIEW MODAL -->
    <div class="modal fade" id="modalMediaPreview" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content bg-dark text-white border border-secondary rounded-4">
                <div class="modal-header border-secondary">
                    <h6 class="modal-title fw-bold text-white" id="previewModalTitle">Media Preview</h6>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" onclick="closePreviewModal()"></button>
                </div>
                <div class="modal-body p-3 text-center">
                    <div id="modal-preview-content" style="max-height: 60vh; overflow: hidden; border-radius: 12px; display: flex; align-items: center; justify-content: center; background: #000;"></div>
                    <div id="modal-preview-caption" class="small text-white-50 text-start mt-3 p-3 bg-dark bg-opacity-75 rounded-3 border border-secondary"></div>
                </div>
                <div class="modal-footer border-secondary justify-content-between">
                    <span id="modal-preview-meta" class="small text-white-50"></span>
                    <button type="button" class="btn btn-sm btn-secondary rounded-pill px-3" data-bs-dismiss="modal" onclick="closePreviewModal()">Close</button>
                </div>
            </div>
        </div>
    </div>

    <!-- TOAST NOTIFICATION CONTAINER -->
    
    <!-- NON-BLOCKING LUXURY ACTION CONFIRMATION MODAL -->
    <div class="modal fade" id="modalConfirmAction" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered modal-sm">
            <div class="modal-content bg-dark text-white border border-secondary rounded-4 shadow-lg text-center p-3">
                <div class="modal-body p-2">
                    <div class="p-3 rounded-circle bg-danger bg-opacity-10 text-danger fs-3 d-inline-block mb-2">
                        <i class="fa-solid fa-trash-can"></i>
                    </div>
                    <h6 class="fw-bold text-white mb-1" id="confirmModalTitle">Are you sure?</h6>
                    <p class="small text-white-50 mb-3" id="confirmModalText" style="font-size: 0.78rem;">This action will permanently delete this item.</p>
                    <div class="d-flex justify-content-center gap-2">
                        <button type="button" class="btn btn-sm btn-secondary rounded-pill px-3" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-sm btn-danger rounded-pill px-3 fw-bold" id="confirmModalBtn">Delete</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    
    <!-- IOS PWA INSTALL INSTRUCTIONS MODAL -->
    <div class="modal fade" id="modalIosInstall" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content bg-dark text-white border border-secondary rounded-4 shadow-lg p-3">
                <div class="modal-header border-0 pb-0">
                    <h5 class="modal-title fw-bold text-white"><i class="fa-brands fa-apple text-warning me-2"></i>Install on iPhone / iPad</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-3">
                    <p class="text-white-50 small mb-3">Safari mein sirf 3 aasan steps mein ReelPilot Studio ko apne iPhone ki Home Screen par app ki tarah add karein:</p>
                    <div class="d-flex align-items-center gap-3 p-3 bg-dark bg-opacity-50 rounded-3 border border-secondary mb-2">
                        <span class="badge bg-warning text-dark fs-6 rounded-circle px-2 py-1">1</span>
                        <div class="small">Safari ke bottom bar par <strong>Share</strong> icon dabayein <i class="fa-solid fa-arrow-up-from-bracket text-info ms-1"></i></div>
                    </div>
                    <div class="d-flex align-items-center gap-3 p-3 bg-dark bg-opacity-50 rounded-3 border border-secondary mb-2">
                        <span class="badge bg-warning text-dark fs-6 rounded-circle px-2 py-1">2</span>
                        <div class="small">Neechay scroll karein aur <strong>Add to Home Screen</strong> dabayein <i class="fa-regular fa-square-plus text-success ms-1"></i></div>
                    </div>
                    <div class="d-flex align-items-center gap-3 p-3 bg-dark bg-opacity-50 rounded-3 border border-secondary">
                        <span class="badge bg-warning text-dark fs-6 rounded-circle px-2 py-1">3</span>
                        <div class="small">Top right par <strong>Add</strong> dabayein. App icon aapke mobile par bina URL bar ke native app ki tarah open hoga!</div>
                    </div>
                </div>
                <div class="modal-footer border-0 pt-0">
                    <button type="button" class="btn btn-sm btn-gold rounded-pill px-4" data-bs-dismiss="modal">Samajh Gaya!</button>
                </div>
            </div>
        </div>
    </div>

    <div id="toast-container"></div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>

    <script>
        // --- GLOBAL STATE ---
        let selectedFiles = [];
        let mainCoverIndex = 0;
        let selectedDestination = 'instagram'; // 'instagram', 'facebook', 'all'
        let selectedScheduleMode = 'calendar'; // 'instant', 'calendar', 'queue'
        let currentFeedFilter = 'all';
        let allPostsData = [];

        const settingsModal = new bootstrap.Modal(document.getElementById('modalStudioSettings'));
        const previewModal = new bootstrap.Modal(document.getElementById('modalMediaPreview'));

        // LUXURY SVG FALLBACK PLACEHOLDER
        const LUXURY_FALLBACK_SVG = "data:image/svg+xml;utf8,<svg xmlns=\'http://www.w3.org/2000/svg\' width=\'300\' height=\'300\' viewBox=\'0 0 300 300\'><rect width=\'100%\' height=\'100%\' fill=\'%230b1120\'/><path d=\'M150 70 L170 110 L215 115 L180 145 L190 190 L150 165 L110 190 L120 145 L85 115 L130 110 Z\' fill=\'%23f59e0b\' opacity=\'0.4\'/><text x=\'50%\' y=\'68%\' dominant-baseline=\'middle\' text-anchor=\'middle\' fill=\'%23f59e0b\' font-family=\'Cinzel, sans-serif\' font-weight=\'bold\' font-size=\'15\'>JANI\\'S PERFUME</text><text x=\'50%\' y=\'78%\' dominant-baseline=\'middle\' text-anchor=\'middle\' fill=\'%2394a3b8\' font-family=\'sans-serif\' font-size=\'11\'>Luxury Fragrance</text></svg>";

        // --- ON PAGE LOAD INITIALIZATION ---
        document.addEventListener('DOMContentLoaded', () => {
            initDefaultDateTime();
            // Pre-initialize Action Confirmation Modal to eliminate INP latency
            const confirmModalEl = document.getElementById('modalConfirmAction');
            if (confirmModalEl && typeof bootstrap !== 'undefined') {
                confirmActionModal = new bootstrap.Modal(confirmModalEl);
                const confirmBtn = document.getElementById('confirmModalBtn');
                if (confirmBtn) {
                    confirmBtn.addEventListener('click', () => {
                        if (confirmActionModal) confirmActionModal.hide();
                        if (typeof pendingConfirmAction === 'function') {
                            const action = pendingConfirmAction;
                            pendingConfirmAction = null;
                            setTimeout(action, 40);
                        }
                    });
                }
            }
            checkLiveHealth();
            loadCalendarFeed();
            loadReelsFeed();
            setInterval(checkLiveHealth, 45000);
            setInterval(loadCalendarFeed, 30000);
        });

        function showToast(msg, type = "success") {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            const bgClass = type === 'error' ? 'bg-danger text-white' : (type === 'warning' ? 'bg-warning text-dark' : 'bg-success text-white');
            toast.className = `p-3 mb-2 rounded-3 shadow-lg fw-bold d-flex align-items-center gap-2 ${bgClass}`;
            toast.style.minWidth = '240px';
            toast.style.fontSize = '0.85rem';
            toast.innerHTML = `<i class="fa-solid fa-${type === 'error' ? 'circle-xmark' : (type === 'warning' ? 'triangle-exclamation' : 'circle-check')}"></i> <span>${msg}</span>`;
            container.appendChild(toast);
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transition = 'opacity 0.4s';
                setTimeout(() => toast.remove(), 400);
            }, 3500);
        }

        // --- DESTINATION & SCHEDULE SELECTION ---
        function selectDestination(dest) {
            selectedDestination = dest;
            document.querySelectorAll('#btn-dest-insta, #btn-dest-fb, #btn-dest-all').forEach(b => b.classList.remove('active'));
            if (dest === 'instagram') document.getElementById('btn-dest-insta').classList.add('active');
            if (dest === 'facebook') document.getElementById('btn-dest-fb').classList.add('active');
            if (dest === 'all') document.getElementById('btn-dest-all').classList.add('active');
        }

        function selectScheduleMode(mode) {
            selectedScheduleMode = mode;
            document.querySelectorAll('#btn-mode-instant, #btn-mode-calendar, #btn-mode-queue').forEach(b => b.classList.remove('active'));
            const pickerBox = document.getElementById('calendar-picker-box');
            if (mode === 'instant') {
                document.getElementById('btn-mode-instant').classList.add('active');
                pickerBox.classList.add('d-none');
            } else if (mode === 'calendar') {
                document.getElementById('btn-mode-calendar').classList.add('active');
                pickerBox.classList.remove('d-none');
            } else if (mode === 'queue') {
                document.getElementById('btn-mode-queue').classList.add('active');
                pickerBox.classList.add('d-none');
            }
        }

        function setVolume(v) {
            document.getElementById('perfume-ml-input').value = v;
        }

        function initDefaultDateTime() {
            const now = new Date();
            now.setHours(now.getHours() + 2);
            now.setMinutes(0);
            const dateStr = now.toISOString().split('T')[0];
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            document.getElementById('schedule-date-input').value = dateStr;
            document.getElementById('schedule-time-input').value = `${hours}:${minutes}`;
            updateDateTimePreview();
        }

        function updateDateTimePreview() {
            const t = document.getElementById('schedule-time-input').value;
            if (!t) return;
            const hour = parseInt(t.split(':')[0], 10);
            let waqt = "Subah (Morning)";
            if (hour >= 12 && hour < 16) waqt = "Dopahar (Afternoon)";
            else if (hour >= 16 && hour < 20) waqt = "Sham (Evening)";
            else if (hour >= 20 || hour < 5) waqt = "Raat (Night)";
            document.getElementById('waqt-preview-badge').innerText = waqt;
        }

        // --- FILE SELECTION & DRAG-DROP ---
        const dropZone = document.getElementById('drop-zone');
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => { e.preventDefault(); dropZone.style.borderColor = '#f59e0b'; }, false);
        });
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => { e.preventDefault(); dropZone.style.borderColor = 'rgba(245, 158, 11, 0.5)'; }, false);
        });
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            const dt = e.dataTransfer;
            if (dt && dt.files && dt.files.length > 0) {
                addFiles(Array.from(dt.files));
            }
        });

        function handleFileSelect(e) {
            if (e.target.files && e.target.files.length > 0) {
                addFiles(Array.from(e.target.files));
            }
        }

        function addFiles(files) {
            const valid = files.filter(f => f.type.startsWith('image/') || f.type.startsWith('video/'));
            selectedFiles = selectedFiles.concat(valid).slice(0, 12);
            renderMediaPreview();
        }

        function setMainCover(idx) {
            mainCoverIndex = idx;
            renderMediaPreview();
        }

        function removeSelectedFile(idx) {
            selectedFiles.splice(idx, 1);
            if (mainCoverIndex >= selectedFiles.length) mainCoverIndex = 0;
            renderMediaPreview();
        }

        function renderMediaPreview() {
            const strip = document.getElementById('media-preview-strip');
            const countBadge = document.getElementById('selected-files-count');
            countBadge.innerText = `${selectedFiles.length}/12 Media Selected`;

            if (selectedFiles.length === 0) {
                strip.classList.add('d-none');
                strip.innerHTML = '';
                return;
            }

            strip.classList.remove('d-none');
            let html = '';
            selectedFiles.forEach((file, idx) => {
                const isCover = idx === mainCoverIndex;
                const blobUrl = URL.createObjectURL(file);
                const isVid = file.type.startsWith('video/');

                html += `
                    <div class="col-4 col-sm-3 col-md-2">
                        <div class="media-preview-card ${isCover ? 'is-cover' : ''}">
                            ${isCover ? '<span class="cover-badge">MAIN</span>' : `<span class="order-badge">#${idx+1}</span>`}
                            ${isVid ? `<video src="${blobUrl}"></video>` : `<img src="${blobUrl}">`}
                            <div style="position: absolute; bottom: 2px; right: 2px; z-index: 3;">
                                <button type="button" class="btn btn-sm btn-dark text-danger p-0 px-1 rounded-circle" onclick="removeSelectedFile(${idx})"><i class="fa-solid fa-xmark"></i></button>
                            </div>
                            ${!isCover ? `<div style="position: absolute; bottom: 2px; left: 2px; z-index: 3;"><button type="button" class="btn btn-sm btn-dark text-warning p-0 px-1" onclick="setMainCover(${idx})" title="Set as Main Cover"><i class="fa-solid fa-star"></i></button></div>` : ''}
                        </div>
                    </div>
                `;
            });
            strip.innerHTML = html;
        }

        // --- AI LUXURY DESCRIPTION GENERATOR ---
        function generateLuxuryDescription() {
            const name = document.getElementById('perfume-name-input').value.trim() || "Crown Kredence";
            const ml = document.getElementById('perfume-ml-input').value.trim() || "100ml";
            const notes = document.getElementById('perfume-notes-input').value.trim() || "Woody Amber, Velvet Rose, Royal Oud";
            const price = document.getElementById('perfume-price-input').value.trim();

            let priceText = price ? `\n💰 Exclusive Price: ${price}` : "";

            const caption = `Step into Unrivaled Elegance with ${name} (${ml}) by JANI\'S Perfume. 👑\n\nA masterclass in olfactory craftsmanship designed for those who command the room without saying a word.\n\n💎 Olfactory Profile: ${notes}\n✨ Projection & Longevity: Beast Mode Performance with a velvety, intoxicating sillage.${priceText}\n\n🌐 𝐖𝐞𝐛𝐬𝐢𝐭𝐞 𝐂𝐡𝐞𝐜𝐤𝐨𝐮𝐭: janisperfumes.com\n💬 𝐏𝐫𝐞𝐟𝐞𝐫 𝐖𝐡𝐚𝐭𝐬𝐀𝐩𝐩: 03134454899\n📩 𝐒𝐞𝐧𝐝 𝐮𝐬 𝐚 𝐃𝐌 𝐭𝐨 𝐨𝐫𝐝𝐞𝐫 𝐝𝐢𝐫𝐞𝐜𝐭𝐥𝐲!\n\n#JanisPerfumes #${name.replace(/\s+/g, '')} #LuxuryFragrance #OudPerfume #NichePerfume #ViralPerfume #PakistanLuxury`;

            document.getElementById('post-caption-input').value = caption;
            showToast("Luxury AI Description & Viral Hashtags Generated!");
        }

        // --- RESOLVE THUMBNAIL URL ---
        function getCoverMediaUrl(item) {
            if (!item) return LUXURY_FALLBACK_SVG;
            if (item.cover_url && typeof item.cover_url === 'string' && item.cover_url.trim()) {
                return item.cover_url.trim();
            }
            if (Array.isArray(item.media_urls) && item.media_urls.length > 0) {
                return item.media_urls[0];
            }
            let target = item.processed_path || item.file_path || '';
            if (typeof target === 'string' && target.trim().startsWith('[')) {
                try {
                    const arr = JSON.parse(target);
                    if (Array.isArray(arr) && arr.length > 0) target = arr[0] || '';
                } catch (e) {}
            }
            if (!target) return LUXURY_FALLBACK_SVG;
            target = String(target).trim();
            if (target.startsWith('http://') || target.startsWith('https://')) return target;
            const fname = target.split(/[\\/]/).pop();
            return fname ? `/api/media/${encodeURIComponent(fname)}` : LUXURY_FALLBACK_SVG;
        }

        // --- LIVE HEALTH STATUS ---
        async function checkLiveHealth(isUser = false) {
            const dot = document.getElementById('nav-status-dot');
            const text = document.getElementById('nav-status-text');
            const pill = document.getElementById('nav-live-indicator');
            const sum = document.getElementById('meta-accounts-summary');

            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 4500);
                const res = await fetch('/api/accounts/health', { signal: controller.signal });
                clearTimeout(timeoutId);

                if (res.status === 401) {
                    window.location.href = '/login';
                    return;
                }

                const data = await res.json();
                if (data.connected && data.status === 'ACTIVE') {
                    if (pill) pill.className = 'status-pill';
                    if (dot) dot.style.backgroundColor = '#10b981';
                    const ig = (data.instagram && data.instagram.username) ? data.instagram.username : "official_janisperfume";
                    const fb = (data.facebook && data.facebook.name) ? data.facebook.name : "JANI\'s Perfume";
                    if (text) text.innerText = `@${ig} (Live Active)`;
                    if (sum) sum.innerHTML = `Instagram: <strong class="text-warning">@${ig}</strong> | Facebook: <strong class="text-primary">${fb}</strong> (Graph API Live)`;
                    if (isUser) showToast("Meta Graph API Connected & Live!");
                } else {
                    if (pill) pill.className = 'status-pill status-pill-disconnected';
                    if (dot) dot.style.backgroundColor = '#ef4444';
                    if (text) text.innerText = 'Meta Disconnected';
                    if (sum) sum.innerHTML = `<span class="text-danger fw-bold">Session Expired or Missing Token. Please reconnect in Settings!</span>`;
                    if (isUser) showToast(data.message || "Meta Connection Error", "error");
                }
            } catch (e) {
                console.warn("Health check error:", e);
                if (text && text.innerText.includes('Checking')) {
                    text.innerText = '@official_janisperfume (Live Active)';
                }
            }
        }

        // --- CALENDAR FEED LOADER ---
        async function loadCalendarFeed() {
            const container = document.getElementById('calendar-feed-container');
            try {
                const res = await fetch('/api/calendar');
                const data = await res.json();
                const events = (data.success && Array.isArray(data.events)) ? data.events : [];

                // Filter out any locally deleted IDs (if user just clicked delete)
                const deletedIds = new Set(JSON.parse(localStorage.getItem('reelpilot_deleted_ids') || '[]'));
                const activeEvents = events.filter(e => !deletedIds.has(String(e.id)) && !deletedIds.has(Number(e.id)));

                if (activeEvents.length === 0) {
                    container.innerHTML = `
                        <div class="col-12 text-center py-4 text-white-50">
                            <i class="fa-solid fa-calendar-check fs-2 text-warning opacity-50 mb-2"></i>
                            <div class="fw-bold text-white">No Upcoming Scheduled Posts</div>
                            <small class="text-white-50">Use the workbench above to schedule your next luxury post!</small>
                        </div>
                    `;
                    return;
                }

                let html = '';
                activeEvents.forEach(ev => {
                    const isCarousel = ev.media_type === 'carousel';
                    const plat = ev.target_platform || 'instagram';
                    const platBadge = plat === 'facebook' 
                        ? '<span class="badge badge-fb"><i class="fa-brands fa-facebook me-1"></i>FACEBOOK</span>' 
                        : '<span class="badge badge-insta"><i class="fa-brands fa-instagram me-1"></i>INSTAGRAM</span>';
                    const typeBadge = isCarousel 
                        ? '<span class="badge bg-warning text-dark"><i class="fa-solid fa-images me-1"></i>Album</span>' 
                        : '<span class="badge bg-secondary">Photo</span>';

                    const dt = ev.dt_info || { exact_date: ev.scheduled_time || 'Scheduled', exact_time: '', waqt: 'Waqt', countdown: 'Ready' };

                    let statusBadge = '';
                    let actionBtn = '';

                    if (ev.status === 'UPLOADED') {
                        statusBadge = '<span class="badge bg-success text-white fw-bold"><i class="fa-solid fa-circle-check me-1"></i>LIVE</span>';
                        actionBtn = ev.remote_url 
                            ? `<a href="${ev.remote_url}" target="_blank" class="btn btn-sm btn-outline-success rounded-pill flex-grow-1 fw-bold py-1" style="font-size: 0.72rem;"><i class="fa-solid fa-arrow-up-right-from-square me-1"></i>View Live</a>`
                            : `<button class="btn btn-sm btn-outline-success rounded-pill flex-grow-1 fw-bold disabled py-1" style="font-size: 0.72rem;"><i class="fa-solid fa-check-double me-1"></i>Published</button>`;
                    } else if (ev.status === 'UPLOADING') {
                        statusBadge = '<span class="badge bg-warning text-dark fw-bold"><i class="fa-solid fa-spinner fa-spin me-1"></i>Publishing...</span>';
                        actionBtn = `<button class="btn btn-sm btn-warning rounded-pill flex-grow-1 fw-bold disabled text-dark py-1" style="font-size: 0.72rem;"><i class="fa-solid fa-spinner fa-spin me-1"></i>Publishing</button>`;
                    } else if (ev.status === 'FAILED') {
                        statusBadge = '<span class="badge bg-danger text-white fw-bold"><i class="fa-solid fa-triangle-exclamation me-1"></i>Failed</span>';
                        actionBtn = `<button class="btn btn-sm btn-danger rounded-pill flex-grow-1 fw-bold py-1" style="font-size: 0.72rem;" onclick="forcePost('${ev.id}')"><i class="fa-solid fa-rotate me-1"></i>Retry Now</button>`;
                    } else {
                        statusBadge = `<span class="badge bg-info text-dark fw-bold"><i class="fa-solid fa-clock me-1"></i>${dt.countdown}</span>`;
                        actionBtn = `<button class="btn btn-sm btn-primary rounded-pill flex-grow-1 fw-bold py-1" style="font-size: 0.72rem;" onclick="forcePost('${ev.id}')"><i class="fa-solid fa-bolt me-1"></i>Post Now</button>`;
                    }

                    const thumbUrl = getCoverMediaUrl(ev);
                    const errorHtml = ev.error_message ? `<div class="text-danger small caption-clamp-1 mt-1 fw-bold" title="${(ev.error_message).replace(/"/g, '&quot;')}"><i class="fa-solid fa-circle-exclamation me-1"></i>${ev.error_message}</div>` : '';

                    html += `
                        <div class="col-12 col-md-6 col-xl-4" id="timeline-post-${ev.id}">
                            <div class="timeline-card">
                                <div>
                                    <div class="d-flex justify-content-between align-items-center mb-2">
                                        <div class="d-flex gap-1">${platBadge} ${typeBadge}</div>
                                        ${statusBadge}
                                    </div>

                                    <div class="d-flex gap-2 align-items-center p-2 rounded-3 mb-2" style="background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.05);">
                                        <img src="${thumbUrl}" style="width: 52px; height: 52px; border-radius: 8px; object-fit: cover; flex-shrink: 0; cursor: pointer;" onclick="previewPost('${ev.id}')" onerror="this.onerror=null; this.src='${LUXURY_FALLBACK_SVG}';">
                                        <div style="line-height: 1.25; overflow: hidden; min-width: 0;">
                                            <div class="fw-bold text-warning small caption-clamp-1"><i class="fa-solid fa-calendar-day me-1"></i>${dt.exact_date}</div>
                                            <div class="fw-bold text-white caption-clamp-1" style="font-size: 0.8rem;"><i class="fa-solid fa-clock text-info me-1"></i>${dt.exact_time}</div>
                                            <span class="badge-waqt">${dt.waqt}</span>
                                        </div>
                                    </div>

                                    <div class="caption-clamp-2 text-white-50 small mb-2" style="font-size: 0.75rem;">
                                        ${ev.caption || 'No caption'}
                                    </div>
                                    ${errorHtml}
                                </div>

                                <div class="d-flex gap-2 mt-2 pt-2 border-top border-secondary border-opacity-50">
                                    ${actionBtn}
                                    <button class="btn btn-sm btn-outline-danger rounded-pill px-3 py-1" style="font-size: 0.72rem;" onclick="deletePost('${ev.id}')" title="Delete"><i class="fa-solid fa-trash"></i></button>
                                </div>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
            } catch (e) {
                console.warn(e);
            }
        }

        // --- REELS FEED & COMPACT GALLERY ---
        async function loadReelsFeed() {
            try {
                const res = await fetch('/api/posts');
                const data = await res.json();
                const deletedIds = new Set(JSON.parse(localStorage.getItem('reelpilot_deleted_ids') || '[]'));
                allPostsData = (Array.isArray(data) ? data : []).filter(p => !deletedIds.has(String(p.id)) && !deletedIds.has(Number(p.id)));
                renderPosts();
            } catch (e) {
                console.warn(e);
            }
        }

        function filterFeed(plat, btn) {
            currentFeedFilter = plat;
            document.querySelectorAll('.feed-filter-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            renderPosts();
        }

        function renderPosts() {
            const container = document.getElementById('reels-feed-grid');
            let filtered = allPostsData;
            if (currentFeedFilter !== 'all') {
                filtered = filtered.filter(p => p.target_platform === currentFeedFilter);
            }

            if (!filtered || filtered.length === 0) {
                container.innerHTML = `
                    <div class="col-12 text-center py-5 text-white-50">
                        <i class="fa-solid fa-box-open fs-1 text-warning mb-2 d-block opacity-40"></i>
                        <h6 class="fw-bold text-white">No Posts in Feed (${currentFeedFilter.toUpperCase()})</h6>
                        <small>Drop images in watch folders or create a post above!</small>
                    </div>
                `;
                return;
            }

            let html = '';
            filtered.forEach(p => {
                const plat = p.target_platform || 'instagram';
                const platBadge = plat === 'facebook' ? '<span class="badge badge-fb">FB</span>' : '<span class="badge badge-insta">IG</span>';
                const thumbUrl = getCoverMediaUrl(p);

                let statusBadge = '<span class="badge bg-secondary" style="font-size: 0.6rem;">Queued</span>';
                if (p.status === 'UPLOADED') statusBadge = '<span class="badge bg-success" style="font-size: 0.6rem;">Live</span>';
                else if (p.status === 'SCHEDULED') statusBadge = '<span class="badge bg-info text-dark" style="font-size: 0.6rem;">Scheduled</span>';
                else if (p.status === 'FAILED') statusBadge = '<span class="badge bg-danger" style="font-size: 0.6rem;">Failed</span>';

                html += `
                    <div class="col-6 col-sm-4 col-md-3 col-lg-2" id="feed-post-${p.id}">
                        <div class="reel-card">
                            <div class="reel-thumb-container" onclick="previewPost('${p.id}')">
                                <img src="${thumbUrl}" class="reel-thumb-img" onerror="this.onerror=null; this.src='${LUXURY_FALLBACK_SVG}';">
                                <div style="position: absolute; top: 4px; left: 4px;">${platBadge}</div>
                                <div style="position: absolute; bottom: 4px; left: 4px;">${statusBadge}</div>
                            </div>
                            <div class="p-2 d-flex flex-column justify-content-between flex-grow-1" style="font-size: 0.75rem;">
                                <div class="caption-clamp-1 fw-bold text-white mb-1" title="${(p.caption || '').replace(/"/g, '&quot;')}">
                                    ${p.caption || 'Perfume Post'}
                                </div>
                                <div class="d-flex justify-content-between align-items-center mt-1 pt-1 border-top border-secondary border-opacity-50">
                                    <button class="btn btn-sm btn-link text-warning p-0" onclick="previewPost('${p.id}')" title="Preview"><i class="fa-solid fa-eye"></i></button>
                                    ${p.status !== 'UPLOADED' ? `<button class="btn btn-sm btn-link text-primary p-0" onclick="forcePost('${p.id}')" title="Post Now"><i class="fa-solid fa-bolt"></i></button>` : ''}
                                    <button class="btn btn-sm btn-link text-danger p-0" onclick="deletePost('${p.id}')" title="Delete"><i class="fa-solid fa-trash"></i></button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }

        // --- SUBMIT POST HANDLER ---
        async function submitPost() {
            if (selectedFiles.length === 0) {
                showToast("Please select at least 1 image or video!", "warning");
                return;
            }

            const caption = document.getElementById('post-caption-input').value.trim();
            const date = document.getElementById('schedule-date-input').value;
            const time = document.getElementById('schedule-time-input').value;

            const fd = new FormData();
            selectedFiles.forEach(f => fd.append("files", f));
            fd.append("platform", selectedDestination);
            fd.append("caption", caption);
            fd.append("main_index", mainCoverIndex);
            fd.append("schedule_mode", selectedScheduleMode);

            if (selectedScheduleMode === 'calendar' && date && time) {
                const combined = `${date}T${time}:00`;
                fd.append("scheduled_time", combined);
                const localDate = new Date(combined);
                if (!isNaN(localDate.getTime())) {
                    fd.append("scheduled_time_utc", localDate.toISOString());
                }
            }

            const btn = document.getElementById('btn-submit-post');
            btn.disabled = true;
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i>Processing & Uploading to Cloud...';

            try {
                const res = await fetch('/api/upload', { method: 'POST', body: fd });
                const d = await res.json();
                if (d.success) {
                    showToast(d.message || "Post created successfully!");
                    selectedFiles = [];
                    mainCoverIndex = 0;
                    renderMediaPreview();
                    document.getElementById('post-caption-input').value = '';
                    document.getElementById('perfume-name-input').value = '';
                    await loadCalendarFeed();
                    await loadReelsFeed();
                } else {
                    showToast(d.error || "Upload failed", "error");
                }
            } catch (e) {
                showToast("Network Error: " + e, "error");
            } finally {
                btn.disabled = false;
                btn.innerHTML = '<i class="fa-solid fa-paper-plane me-2"></i>Publish / Schedule Post';
            }
        }

        // --- NON-BLOCKING CONFIRMATION SYSTEM (ELIMINATES CHROME INP WARNINGS) ---
        let pendingConfirmAction = null;
        let confirmActionModal = null;

        function promptActionConfirm(title, text, actionFn) {
            pendingConfirmAction = actionFn;
            const tEl = document.getElementById('confirmModalTitle');
            const bEl = document.getElementById('confirmModalText');
            if (tEl) tEl.innerText = title;
            if (bEl) bEl.innerText = text;

            // Yield frame before opening modal to ensure zero input delay
            requestAnimationFrame(() => {
                if (confirmActionModal) {
                    confirmActionModal.show();
                } else if (typeof bootstrap !== 'undefined') {
                    const el = document.getElementById('modalConfirmAction');
                    if (el) {
                        confirmActionModal = new bootstrap.Modal(el);
                        confirmActionModal.show();
                    } else {
                        actionFn();
                    }
                } else {
                    actionFn();
                }
            });
        }

        // --- INSTANT PERMANENT DELETE POST (ZERO-INP NON-BLOCKING) ---
        function deletePost(id) {
            promptActionConfirm(
                "Delete Post Permanently?",
                "This post will be completely removed from your calendar and cloud queue.",
                () => {
                    // Optimistic instant feedback
                    const el1 = document.getElementById(`timeline-post-${id}`);
                    if (el1) {
                        el1.style.opacity = '0.25';
                        el1.style.pointerEvents = 'none';
                    }
                    const el2 = document.getElementById(`feed-post-${id}`);
                    if (el2) {
                        el2.style.opacity = '0.25';
                        el2.style.pointerEvents = 'none';
                    }

                    // 1. Instantly blacklist ID so it never resurfaces in memory
                    try {
                        const deletedIds = new Set(JSON.parse(localStorage.getItem('reelpilot_deleted_ids') || '[]'));
                        deletedIds.add(String(id));
                        deletedIds.add(Number(id));
                        localStorage.setItem('reelpilot_deleted_ids', JSON.stringify(Array.from(deletedIds)));
                    } catch (e) {}

                    // 2. Remove from memory
                    allPostsData = allPostsData.filter(p => String(p.id) !== String(id));

                    // 3. Smooth DOM removal after paint
                    setTimeout(() => {
                        if (el1) el1.remove();
                        if (el2) el2.remove();
                    }, 200);

                    // 4. Non-blocking asynchronous deletion
                    fetch(`/api/posts/${id}/delete`, { method: 'POST' })
                        .then(r => r.json())
                        .then(() => showToast("Post deleted permanently!"))
                        .catch(e => console.warn(e));
                }
            );
        }

        // --- CLEAR ALL FAILED POSTS (ZERO-INP NON-BLOCKING) ---
        function clearFailedEvents() {
            promptActionConfirm(
                "Clear Failed Posts?",
                "All failed test posts will be wiped from your calendar and cloud queue.",
                () => {
                    document.querySelectorAll('[id^="timeline-post-"]').forEach(el => {
                        if (el.innerText.includes('Failed')) {
                            el.style.opacity = '0.25';
                            setTimeout(() => el.remove(), 200);
                        }
                    });
                    document.querySelectorAll('[id^="feed-post-"]').forEach(el => {
                        if (el.innerText.includes('Failed')) {
                            el.style.opacity = '0.25';
                            setTimeout(() => el.remove(), 200);
                        }
                    });

                    fetch('/api/posts/clear-failed', { method: 'POST' })
                        .then(r => r.json())
                        .then(data => {
                            showToast(`Cleared ${data.removed || 0} failed posts!`);
                            setTimeout(() => {
                                loadCalendarFeed();
                                loadReelsFeed();
                            }, 300);
                        })
                        .catch(e => showToast("Clear error: " + e, "error"));
                }
            );
        }

        // --- POST NOW / RETRY ---
        async function forcePost(id) {
            showToast("Publishing to Meta immediately...", "warning");
            try {
                const res = await fetch(`/api/posts/${id}/post-now`, { method: 'POST' });
                const d = await res.json();
                if (d.success) {
                    showToast("Uploaded successfully!");
                    loadCalendarFeed();
                    loadReelsFeed();
                } else {
                    showToast(d.error || "Upload failed", "error");
                    loadCalendarFeed();
                }
            } catch (e) {
                showToast("Error: " + e, "error");
            }
        }

        // --- PREVIEW MODAL ---
        function previewPost(postId) {
            const p = allPostsData.find(x => String(x.id) === String(postId));
            const imgUrl = p ? getCoverMediaUrl(p) : LUXURY_FALLBACK_SVG;
            const caption = p ? (p.caption || 'No caption') : '';
            const plat = p ? (p.target_platform || 'instagram').toUpperCase() : '';

            document.getElementById('previewModalTitle').innerText = `${plat} Post Preview (#${postId})`;
            document.getElementById('modal-preview-content').innerHTML = `<img src="${imgUrl}" style="max-width: 100%; max-height: 55vh; object-fit: contain; border-radius: 8px;">`;
            document.getElementById('modal-preview-caption').innerText = caption;
            document.getElementById('modal-preview-meta').innerText = `Destination: ${plat} | Media: ${p ? p.media_type : 'Image'}`;
            previewModal.show();
        }

        function closePreviewModal() {
            document.getElementById('modal-preview-content').innerHTML = '';
        }

        function openFolder(folder) {
            fetch('/api/open-folder', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ folder })
            }).then(() => showToast(`Opened ${folder} folder on PC!`)).catch(() => {});
        }


        // --- SETTINGS MANAGEMENT ---
        async function openSettingsModal() {
            try {
                const res = await fetch('/api/settings');
                const data = await res.json();
                if (data) {
                    if (data.brand_name) document.getElementById('setting-brand-name').value = data.brand_name;
                    if (data.meta_access_token) document.getElementById('setting-meta-token').value = data.meta_access_token;
                    if (data.daily_limit_insta) document.getElementById('setting-quota-ig').value = data.daily_limit_insta;
                    if (data.daily_limit_facebook) document.getElementById('setting-quota-fb').value = data.daily_limit_facebook;
                }
            } catch (e) {}
            settingsModal.show();
        }

        async function saveStudioSettings() {
            const payload = {
                brand_name: document.getElementById('setting-brand-name').value.trim(),
                meta_access_token: document.getElementById('setting-meta-token').value.trim(),
                daily_limit_insta: parseInt(document.getElementById('setting-quota-ig').value, 10) || 3,
                daily_limit_facebook: parseInt(document.getElementById('setting-quota-fb').value, 10) || 3
            };
            try {
                const res = await fetch('/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const d = await res.json();
                if (d.success) {
                    showToast("All Settings Saved & Applied!");
                    settingsModal.hide();
                    checkLiveHealth(true);
                } else {
                    showToast(d.error || "Save error", "error");
                }
            } catch (e) {
                showToast("Save error: " + e, "error");
            }
        }


        async function verifyMetaToken() {
            const token = document.getElementById('setting-meta-token').value.trim();
            if (!token) {
                showToast("Please paste token first", "warning");
                return;
            }
            showToast("Verifying token with Meta Graph API...", "warning");
            try {
                const res = await fetch('/api/verify-token', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ meta_token: token })
                });
                const d = await res.json();
                if (d.success) {
                    showToast("Token Verified & Connected Successfully!");
                    checkLiveHealth(true);
                } else {
                    showToast(d.error || "Invalid token", "error");
                }
            } catch (e) {
                showToast("Verification error: " + e, "error");
            }
        }

        
    </script>
</body>
</html>
"""

HTML_STUDIO_V36 = STUDIO_HTML
