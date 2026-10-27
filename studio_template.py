HTML_STUDIO_V36 = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ReelPilot Studio v3.6 - Multi-Media Automation & Worldwide Music Hub</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --accent: #06b6d4;
            --bg-dark: #070d18;
            --card-bg: #0f172a;
            --card-border: #1e293b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --insta-grad: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
            --tiktok-grad: linear-gradient(45deg, #00f2fe 0%, #4facfe 100%);
            --fb-color: #1877f2;
            --gemini-grad: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #9333ea 100%);
        }

        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            font-family: 'Plus Jakarta Sans', sans-serif;
            margin: 0;
            padding: 0;
            min-height: 100vh;
        }

        .navbar-top {
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--card-border);
            padding: 14px 24px;
            position: sticky;
            top: 0;
            z-index: 1000;
        }

        .card-pro {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        }

        .account-chip {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 30px;
            padding: 6px 14px;
            font-size: 0.85rem;
            transition: all 0.2s ease;
        }
        .account-chip:hover {
            border-color: var(--primary);
            transform: translateY(-1px);
        }

        .drop-zone-main {
            border: 2px dashed #6366f1;
            border-radius: 20px;
            background: rgba(99, 102, 241, 0.05);
            padding: 35px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .drop-zone-main:hover {
            background: rgba(99, 102, 241, 0.1);
            border-color: #818cf8;
        }

        .media-preview-card {
            position: relative;
            border-radius: 12px;
            overflow: hidden;
            background: #020617;
            border: 2px solid var(--card-border);
            aspect-ratio: 1 / 1;
            transition: all 0.2s;
        }
        .media-preview-card.is-cover {
            border-color: #f59e0b;
            box-shadow: 0 0 15px rgba(245, 158, 11, 0.35);
        }
        .media-preview-card img, .media-preview-card video {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .cover-badge {
            position: absolute;
            top: 6px;
            left: 6px;
            background: #f59e0b;
            color: #000;
            font-weight: 800;
            font-size: 0.68rem;
            padding: 3px 8px;
            border-radius: 20px;
            z-index: 2;
        }
        .order-badge {
            position: absolute;
            top: 6px;
            right: 6px;
            background: rgba(0, 0, 0, 0.7);
            color: #fff;
            font-weight: bold;
            font-size: 0.7rem;
            padding: 2px 7px;
            border-radius: 12px;
            z-index: 2;
        }
        .media-card-actions {
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            background: linear-gradient(transparent, rgba(0,0,0,0.85));
            padding: 6px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 2;
        }

        .reel-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: all 0.2s;
        }
        .reel-card:hover {
            transform: translateY(-3px);
            border-color: var(--primary);
            box-shadow: 0 12px 30px rgba(99, 102, 241, 0.15);
        }
        .reel-thumb-container {
            position: relative;
            width: 100%;
            padding-top: 110%;
            background: #000;
            overflow: hidden;
            cursor: pointer;
        }
        .reel-thumb-img {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .reel-play-btn {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 48px;
            height: 48px;
            background: rgba(0, 0, 0, 0.65);
            border: 2px solid #fff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            font-size: 1.2rem;
            backdrop-filter: blur(4px);
        }

        .form-control, .form-select {
            background: #0c1424;
            border: 1px solid var(--card-border);
            color: #fff;
            border-radius: 12px;
            padding: 10px 14px;
        }
        .form-control:focus, .form-select:focus {
            background: #0c1424;
            border-color: #6366f1;
            color: #fff;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25);
        }

        .timing-btn {
            border: 1px solid var(--card-border);
            background: #0c1424;
            color: #cbd5e1;
            border-radius: 12px;
            padding: 10px 14px;
            font-weight: 600;
            font-size: 0.85rem;
            transition: all 0.2s;
            cursor: pointer;
            text-align: center;
        }
        .timing-btn.active, .timing-btn:hover {
            border-color: var(--primary);
            background: rgba(99, 102, 241, 0.15);
            color: #fff;
        }

        .feed-filter-btn {
            border-radius: 20px;
            padding: 6px 16px;
            font-weight: 600;
            font-size: 0.85rem;
            color: #cbd5e1;
            border: 1px solid var(--card-border);
            background: transparent;
            transition: all 0.2s;
        }
        .feed-filter-btn.active, .feed-filter-btn:hover {
            background: #6366f1;
            border-color: #6366f1;
            color: #fff;
        }

        #toast-container {
            position: fixed;
            bottom: 25px;
            right: 25px;
            z-index: 9999;
        }
    </style>
</head>
<body>
    <!-- TOP NAVIGATION -->
    <nav class="navbar-top">
        <div class="container-fluid d-flex justify-content-between align-items-center">
            <div class="d-flex align-items-center gap-3">
                <span class="fs-4 fw-bold text-white">
                    <i class="fa-solid fa-wand-magic-sparkles text-primary me-2"></i>ReelPilot Studio
                </span>
                <span class="badge text-white rounded-pill px-3 py-1 fw-bold d-none d-md-inline" style="background: var(--gemini-grad); font-size: 0.72rem;">
                    <i class="fa-solid fa-bolt me-1"></i> Dual-AI + Multi-Media v3.6
                </span>
            </div>

            <div class="d-flex align-items-center gap-2">
                <!-- Instagram -->
                <div class="account-chip" onclick="openLoginModal('instagram')" style="cursor: pointer;">
                    <i class="fa-brands fa-instagram text-danger"></i>
                    <span id="chip-insta" class="fw-bold">@official_janisperfume</span>
                    <span class="badge bg-success rounded-pill" style="font-size: 0.65rem;">Live</span>
                </div>
                <!-- Facebook -->
                <div class="account-chip" onclick="openLoginModal('facebook')" style="cursor: pointer;">
                    <i class="fa-brands fa-facebook text-primary"></i>
                    <span id="chip-fb" class="fw-bold">JANI's Perfume</span>
                    <span class="badge bg-success rounded-pill" style="font-size: 0.65rem;">Live</span>
                </div>

                <button class="btn btn-outline-light rounded-pill px-3 py-2 btn-sm fw-bold ms-1" onclick="openSettingsModal()">
                    <i class="fa-solid fa-sliders text-warning me-1"></i> Settings & Storage
                </button>
            </div>
        </div>
    </nav>

    <div class="container-fluid px-4 py-4">
        <!-- HERO STATUS BANNER -->
        <div class="card card-pro p-3 mb-4">
            <div class="d-flex flex-wrap justify-content-between align-items-center gap-3">
                <div class="d-flex align-items-center gap-3">
                    <div class="p-3 rounded-circle text-white fs-4" style="background: var(--gemini-grad);">
                        <i class="fa-solid fa-camera-retro"></i>
                    </div>
                    <div>
                        <div class="fw-bold fs-6 text-white d-flex align-items-center gap-2">
                            <span>1-12 Multi-Image Albums & Native Media Engine:</span>
                            <span class="badge bg-success rounded-pill px-3 py-1">No Video Conversion For Photos</span>
                        </div>
                        <div class="text-white small mt-1" style="opacity: 0.9;">
                            Active Brand: <strong id="hero-brand-name" class="text-warning">JANI's Perfume</strong>.
                            Upload 1 to 12 pictures to publish native multi-photo Facebook albums and Instagram Carousels. Choose your Main Cover image, pick worldwide background music, or schedule for future dates!
                        </div>
                    </div>
                </div>

                <div class="d-flex align-items-center gap-3 bg-dark bg-opacity-50 p-2 px-3 rounded-4 border border-secondary">
                    <div class="text-end">
                        <div class="fw-bold text-white small">Auto-Pilot Engine</div>
                        <small class="text-muted" id="autopilot-mode-label">Anti-Spam 2-3h Delay</small>
                    </div>
                    <div class="form-check form-switch fs-4 mb-0">
                        <input class="form-check-input" type="checkbox" id="switch-autopilot-main" checked onchange="toggleAutoPilot(this)">
                    </div>
                </div>
            </div>
        </div>

        <!-- MAIN POST CREATOR & PC FOLDERS ROW -->
        <div class="row g-4 mb-4">
            <!-- Left: Studio Post Composer -->
            <div class="col-lg-7">
                <div class="card card-pro p-4 h-100">
                    <h4 class="fw-bold text-white mb-3 d-flex justify-content-between align-items-center">
                        <span><i class="fa-solid fa-plus-circle text-primary me-2"></i>Create & Schedule Post</span>
                        <span id="selected-files-count" class="badge bg-secondary rounded-pill fw-normal fs-6">0 / 12 Media Selected</span>
                    </h4>

                    <!-- Platform Selector -->
                    <div class="mb-3">
                        <label class="form-label small fw-bold text-white">Target Destination</label>
                        <div class="row g-2">
                            <div class="col-4">
                                <input type="radio" class="btn-check" name="post-platform" id="plat-insta" value="instagram" checked>
                                <label class="btn btn-outline-light w-100 py-2 fw-bold rounded-3 small" for="plat-insta">
                                    <i class="fa-brands fa-instagram text-danger me-1"></i> Instagram
                                </label>
                            </div>
                            <div class="col-4">
                                <input type="radio" class="btn-check" name="post-platform" id="plat-fb" value="facebook">
                                <label class="btn btn-outline-light w-100 py-2 fw-bold rounded-3 small" for="plat-fb">
                                    <i class="fa-brands fa-facebook text-primary me-1"></i> Facebook
                                </label>
                            </div>
                            <div class="col-4">
                                <input type="radio" class="btn-check" name="post-platform" id="plat-all" value="all">
                                <label class="btn btn-outline-light w-100 py-2 fw-bold rounded-3 small" for="plat-all">
                                    <i class="fa-solid fa-share-nodes text-warning me-1"></i> Both (Insta + FB)
                                </label>
                            </div>
                        </div>
                    </div>

                    <!-- Multi-Image Drop Zone -->
                    <div class="drop-zone-main mb-3" onclick="document.getElementById('file-post-input').click()">
                        <i class="fa-solid fa-cloud-arrow-up fs-2 text-primary mb-2"></i>
                        <h5 class="fw-bold text-white mb-1">Click to Browse or Drag & Drop 1 to 12 Pictures / Videos</h5>
                        <p class="text-white small mb-0" style="opacity: 0.85;">
                            Multi-photos will be published as native Carousels / Albums. Pure images stay pure images!
                        </p>
                        <input type="file" id="file-post-input" class="d-none" accept="image/*,video/*" multiple onchange="handleFilesSelected(this)">
                    </div>

                    <!-- 1 to 12 Media Thumbnail Grid -->
                    <div id="media-grid-container" class="mb-3 d-none">
                        <div class="d-flex justify-content-between align-items-center mb-2">
                            <label class="form-label small fw-bold text-warning mb-0">
                                <i class="fa-solid fa-layer-group me-1"></i> Media Album Items (Click ★ to choose Main Cover)
                            </label>
                            <button type="button" class="btn btn-sm btn-outline-danger py-0 px-2 small" onclick="clearAllSelectedMedia()">Clear All</button>
                        </div>
                        <div id="selected-media-grid" class="row g-2"></div>
                    </div>

                    <!-- Worldwide Music Attachment Pill -->
                    <div class="p-3 bg-dark bg-opacity-50 rounded-3 border border-secondary mb-3 d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center gap-3">
                            <div id="attached-music-art" class="rounded bg-secondary d-flex align-items-center justify-content-center text-white" style="width: 44px; height: 44px; overflow: hidden;">
                                <i class="fa-solid fa-music"></i>
                            </div>
                            <div>
                                <div id="attached-music-title" class="fw-bold text-white small">No Audio Attached (Optional)</div>
                                <div id="attached-music-subtitle" class="text-secondary small">Pick from 100M+ global songs with custom trim</div>
                            </div>
                        </div>
                        <div class="d-flex gap-2">
                            <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-3 fw-bold" onclick="openMusicModal()">
                                <i class="fa-solid fa-magnifying-glass me-1"></i> Global Music Hub
                            </button>
                            <button type="button" id="btn-remove-music" class="btn btn-sm btn-outline-danger rounded-pill px-2 d-none" onclick="removeAttachedMusic()" title="Remove music">
                                <i class="fa-solid fa-xmark"></i>
                            </button>
                        </div>
                    </div>

                    <!-- Post Timing & Calendar Scheduling -->
                    <div class="mb-3">
                        <label class="form-label small fw-bold text-white">Publishing Mode & Schedule</label>
                        <div class="row g-2 mb-2">
                            <div class="col-4">
                                <div class="timing-btn active" id="timing-btn-instant" onclick="setScheduleMode('instant')">
                                    <i class="fa-solid fa-bolt text-warning me-1"></i> Post Immediately
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="timing-btn" id="timing-btn-calendar" onclick="setScheduleMode('calendar')">
                                    <i class="fa-solid fa-calendar-days text-info me-1"></i> Calendar Schedule
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="timing-btn" id="timing-btn-queue" onclick="setScheduleMode('queue')">
                                    <i class="fa-solid fa-robot text-primary me-1"></i> Auto-Pilot Queue
                                </div>
                            </div>
                        </div>

                        <!-- Calendar DateTime Picker -->
                        <div id="calendar-picker-box" class="p-3 bg-dark bg-opacity-50 rounded-3 border border-info mb-2 d-none">
                            <div class="d-flex justify-content-between align-items-center mb-2">
                                <label class="small fw-bold text-info"><i class="fa-solid fa-clock me-1"></i> Select Date & Time for Scheduled Publishing:</label>
                                <span class="badge bg-info text-dark fw-bold">Live Meta Auto-Schedule</span>
                            </div>
                            <input type="datetime-local" id="custom-schedule-datetime" class="form-control form-control-lg mb-2">
                            <!-- Quick Presets -->
                            <div class="d-flex flex-wrap gap-1">
                                <button type="button" class="btn btn-sm btn-outline-light rounded-pill px-2 py-0" onclick="setQuickTime(30)">+30 Mins</button>
                                <button type="button" class="btn btn-sm btn-outline-light rounded-pill px-2 py-0" onclick="setQuickTime(60)">+1 Hour</button>
                                <button type="button" class="btn btn-sm btn-outline-light rounded-pill px-2 py-0" onclick="setQuickTime(180)">+3 Hours</button>
                                <button type="button" class="btn btn-sm btn-outline-light rounded-pill px-2 py-0" onclick="setTomorrowTime(10)">Tomorrow 10:00 AM</button>
                                <button type="button" class="btn btn-sm btn-outline-light rounded-pill px-2 py-0" onclick="setTomorrowTime(20)">Tomorrow 8:00 PM</button>
                            </div>
                        </div>
                    </div>

                    <!-- Custom Caption & Hashtags -->
                    <div class="mb-3">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                            <label class="form-label small fw-bold text-white mb-0">Caption & AI Vision Hook</label>
                            <button type="button" class="btn btn-sm btn-outline-info rounded-pill px-2 py-0 fw-bold" onclick="generateAICaptionForMedia()">
                                <i class="fa-solid fa-wand-magic-sparkles me-1"></i> Generate with AI
                            </button>
                        </div>
                        <textarea id="post-caption-input" class="form-control" rows="2" placeholder="Write custom caption or leave blank for automatic AI Vision generation..."></textarea>
                    </div>

                    <div class="mb-4">
                        <label class="form-label small fw-bold text-white mb-1">Hashtags</label>
                        <input type="text" id="post-hashtags-input" class="form-control" placeholder="#JanisPerfume #LuxuryFragrance #Trending">
                    </div>

                    <!-- Action Button -->
                    <button class="btn btn-success w-100 py-3 rounded-pill fw-bold fs-5 shadow" id="btn-submit-post" onclick="submitPostAction()">
                        <i class="fa-solid fa-rocket me-2"></i>Publish Immediately
                    </button>
                </div>
            </div>

            <!-- Right: Watch Folders & Publishing Quotas -->
            <div class="col-lg-5">
                <div class="card card-pro p-4 h-100 d-flex flex-column justify-content-between">
                    <div>
                        <h4 class="fw-bold text-white mb-2">
                            <i class="fa-regular fa-folder-open text-warning me-2"></i>PC Watch Folders
                        </h4>
                        <p class="text-white small mb-3" style="opacity: 0.85;">
                            Drop files directly into these local folders on your computer — the background watcher detects them, applies AI Vision, and publishes automatically:
                        </p>

                        <!-- Insta Folder -->
                        <div class="p-3 bg-dark bg-opacity-50 rounded-3 border border-secondary mb-2 d-flex justify-content-between align-items-center">
                            <div>
                                <div class="fw-bold text-white small"><i class="fa-brands fa-instagram text-danger me-2"></i>Instagram PC Folder</div>
                                <div class="small font-monospace text-secondary text-truncate" style="max-width: 200px;">Ready_for_Insta</div>
                            </div>
                            <button class="btn btn-sm btn-outline-light rounded-pill px-3 fw-bold" onclick="openFolder('insta')">
                                <i class="fa-regular fa-folder-open me-1"></i> Open on PC
                            </button>
                        </div>

                        <!-- Facebook Folder -->
                        <div class="p-3 bg-dark bg-opacity-50 rounded-3 border border-secondary mb-2 d-flex justify-content-between align-items-center">
                            <div>
                                <div class="fw-bold text-white small"><i class="fa-brands fa-facebook text-primary me-2"></i>Facebook PC Folder</div>
                                <div class="small font-monospace text-secondary text-truncate" style="max-width: 200px;">Ready_for_Facebook</div>
                            </div>
                            <button class="btn btn-sm btn-outline-light rounded-pill px-3 fw-bold" onclick="openFolder('facebook')">
                                <i class="fa-regular fa-folder-open me-1"></i> Open on PC
                            </button>
                        </div>

                        <!-- Cloudflare R2 Cloud Status -->
                        <div class="p-3 bg-dark bg-opacity-50 rounded-3 border border-secondary mb-2 d-flex justify-content-between align-items-center">
                            <div>
                                <div class="fw-bold text-white small"><i class="fa-solid fa-cloud text-warning me-2"></i>Cloudflare R2 Object Storage</div>
                                <div id="label-r2-status" class="small text-info text-truncate" style="max-width: 200px;">Free 10GB Active / Fallback ready</div>
                            </div>
                            <button class="btn btn-sm btn-outline-warning rounded-pill px-3 fw-bold" onclick="openSettingsModal()">
                                <i class="fa-solid fa-gear me-1"></i> Configure
                            </button>
                        </div>
                    </div>

                    <!-- Quota Breakdown -->
                    <div class="p-3 bg-dark bg-opacity-50 rounded-3 border border-secondary small text-white mt-3">
                        <div class="fw-bold mb-1">Today's Publishing Quota:</div>
                        <div class="d-flex justify-content-between text-secondary">
                            <span><i class="fa-brands fa-instagram text-danger me-1"></i> Insta: <strong id="stat-ig-count" class="text-white">0/3</strong></span>
                            <span><i class="fa-brands fa-facebook text-primary me-1"></i> FB: <strong id="stat-fb-count" class="text-white">0/3</strong></span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- VISUAL CONTENT CALENDAR & SCHEDULED TIMELINE SECTION -->
        <div class="card card-pro p-4 mb-4">
            <div class="d-flex flex-wrap justify-content-between align-items-center mb-3 pb-2 border-bottom border-secondary gap-2">
                <div>
                    <h4 class="fw-bold text-white mb-0">
                        <i class="fa-solid fa-calendar-days text-info me-2"></i>Visual Content Calendar & Scheduled Timeline
                    </h4>
                    <p class="text-white small mb-0" style="opacity: 0.85;">
                        View upcoming scheduled posts organized chronologically. Posts execute automatically at the exact chosen date and time.
                    </p>
                </div>
                <button class="btn btn-sm btn-outline-light rounded-pill px-3 fw-bold" onclick="loadCalendarFeed()">
                    <i class="fa-solid fa-rotate me-1"></i> Refresh Calendar
                </button>
            </div>

            <div id="calendar-feed-container" class="row g-3">
                <div class="col-12 text-center py-4 text-secondary">
                    <i class="fa-solid fa-spinner fa-spin fs-4 mb-2"></i>
                    <div>Loading scheduled posts...</div>
                </div>
            </div>
        </div>

        <!-- VISUAL CONTENT FEED WITH FILTERS -->
        <div class="card card-pro p-4 mb-4">
            <div class="d-flex flex-wrap justify-content-between align-items-center mb-4 pb-2 border-bottom border-secondary gap-2">
                <div>
                    <h4 class="fw-bold text-white mb-0">
                        <i class="fa-solid fa-film text-primary me-2"></i>Visual Content Feed
                    </h4>
                    <p class="text-white small mb-0" style="opacity: 0.85;">
                        Track published and queued media. Click <strong>▶ Watch</strong> to preview. Click <strong>⚡ Post Now</strong> to publish immediately.
                    </p>
                </div>

                <!-- Platform Filter Tabs -->
                <div class="d-flex gap-2">
                    <button class="feed-filter-btn active" onclick="filterFeed('all', this)">All</button>
                    <button class="feed-filter-btn" onclick="filterFeed('instagram', this)"><i class="fa-brands fa-instagram text-danger me-1"></i> Instagram</button>
                    <button class="feed-filter-btn" onclick="filterFeed('facebook', this)"><i class="fa-brands fa-facebook text-primary me-1"></i> Facebook</button>
                    <button class="btn btn-sm btn-outline-light rounded-pill px-3 fw-bold ms-2" onclick="loadReelsFeed()"><i class="fa-solid fa-rotate"></i></button>
                </div>
            </div>

            <!-- Feed Grid -->
            <div id="reels-feed-grid" class="row g-4">
                <div class="col-12 text-center py-5 text-white">
                    <i class="fa-solid fa-spinner fa-spin fs-2 text-primary mb-2"></i>
                    <div>Loading visual media feed...</div>
                </div>
            </div>
        </div>
    </div>

    <!-- WORLDWIDE MUSIC SEARCH & TRIMMER MODAL -->
    <div class="modal fade" id="modalWorldwideMusic" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content bg-dark text-white border border-secondary rounded-4 shadow-lg">
                <div class="modal-header border-secondary">
                    <h5 class="modal-title fw-bold text-white">
                        <i class="fa-solid fa-music text-info me-2"></i>Worldwide Music Engine & Audio Trimmer
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-4">
                    <p class="text-secondary small mb-3">
                        Search across 100M+ songs worldwide (Bollywood, Pakistani, Hollywood, Arabic, Trending). Listen to the live stream preview and pick your trim offset (15s, 30s, 60s).
                    </p>

                    <!-- Search Input -->
                    <div class="input-group mb-3">
                        <span class="input-group-text bg-dark border-secondary text-info"><i class="fa-solid fa-magnifying-glass"></i></span>
                        <input type="text" id="music-search-query" class="form-control" placeholder="Search song name or artist (e.g. Atif Aslam, The Weeknd, Kesariya, Drake...)" onkeydown="if(event.key==='Enter') executeMusicSearch()">
                        <button class="btn btn-primary fw-bold px-4" type="button" onclick="executeMusicSearch()">
                            Search Songs
                        </button>
                    </div>

                    <!-- Audio Trimmer Options -->
                    <div class="p-3 bg-dark bg-opacity-50 rounded-3 border border-secondary mb-3">
                        <div class="row g-2 align-items-center">
                            <div class="col-md-6">
                                <label class="small fw-bold text-warning mb-1 d-flex justify-content-between">
                                    <span><i class="fa-solid fa-sliders me-1"></i> Start Offset (Trim Start):</span>
                                    <span id="label-trim-start" class="badge bg-warning text-dark">0s</span>
                                </label>
                                <input type="range" class="form-range" id="slider-trim-start" min="0" max="30" value="0" oninput="document.getElementById('label-trim-start').innerText = this.value + 's'">
                            </div>
                            <div class="col-md-6">
                                <label class="small fw-bold text-info mb-1"><i class="fa-solid fa-stopwatch me-1"></i> Duration Length:</label>
                                <div class="d-flex gap-2">
                                    <button type="button" class="btn btn-sm btn-outline-info active flex-grow-1" id="btn-dur-15" onclick="setTrimDuration(15)">15s</button>
                                    <button type="button" class="btn btn-sm btn-outline-info flex-grow-1" id="btn-dur-30" onclick="setTrimDuration(30)">30s</button>
                                    <button type="button" class="btn btn-sm btn-outline-info flex-grow-1" id="btn-dur-60" onclick="setTrimDuration(60)">60s</button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Search Results -->
                    <div id="music-search-results" style="max-height: 380px; overflow-y: auto;">
                        <div class="text-center py-4 text-secondary">
                            <i class="fa-solid fa-headphones fs-3 mb-2 opacity-50"></i>
                            <div>Type any artist or song title above and click Search!</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- SETTINGS & CLOUDFLARE R2 MODAL -->
    <div class="modal fade" id="modalStudioSettings" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content bg-dark text-white border border-secondary rounded-4 shadow-lg">
                <div class="modal-header border-secondary">
                    <h5 class="modal-title fw-bold text-white">
                        <i class="fa-solid fa-sliders text-warning me-2"></i>Studio Settings & Cloudflare R2 Storage
                    </h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-4">
                    <!-- Brand Name -->
                    <div class="mb-4 p-3 bg-dark bg-opacity-50 rounded-3 border border-secondary">
                        <label class="form-label small fw-bold text-warning">
                            <i class="fa-solid fa-tag me-1"></i> Your Brand Name (Included in AI Captions & Prompts)
                        </label>
                        <input type="text" id="setting-brand-name" class="form-control" placeholder="e.g. JANI's Perfume">
                    </div>

                    <!-- Cloudflare R2 Storage (Free 10GB S3 Compatible) -->
                    <h6 class="fw-bold text-white border-bottom border-secondary pb-2 mb-3">
                        <i class="fa-solid fa-cloud text-warning me-2"></i>Cloudflare R2 Object Storage (Free 10GB for Instagram & Multi-Media)
                    </h6>
                    <div class="p-3 bg-dark bg-opacity-50 rounded-3 border border-secondary mb-4">
                        <div class="row g-2 mb-2">
                            <div class="col-md-6">
                                <label class="small text-white fw-bold">Cloudflare Account ID</label>
                                <input type="text" id="setting-r2-account-id" class="form-control" placeholder="e.g. 78a9c402...">
                            </div>
                            <div class="col-md-6">
                                <label class="small text-white fw-bold">R2 Bucket Name</label>
                                <input type="text" id="setting-r2-bucket-name" class="form-control" placeholder="e.g. reelpilot-media">
                            </div>
                            <div class="col-md-6">
                                <label class="small text-white fw-bold">R2 Access Key ID</label>
                                <input type="password" id="setting-r2-access-key" class="form-control" placeholder="Access Key">
                            </div>
                            <div class="col-md-6">
                                <label class="small text-white fw-bold">R2 Secret Access Key</label>
                                <input type="password" id="setting-r2-secret-key" class="form-control" placeholder="Secret Key">
                            </div>
                            <div class="col-12">
                                <label class="small text-white fw-bold">Public Domain / Custom URL (Optional)</label>
                                <input type="text" id="setting-r2-public-domain" class="form-control" placeholder="https://pub-xxxx.r2.dev">
                            </div>
                        </div>
                        <small class="text-white-50"><i class="fa-solid fa-circle-info text-info me-1"></i> Agar ye empty ho, to system automatic instant free cloud hosting fallback use karta hai, taake Instagram post direct live ho sake bina rukawat ke!</small>
                    </div>

                    <!-- Dual AI Vision Keys -->
                    <h6 class="fw-bold text-white border-bottom border-secondary pb-2 mb-3">
                        <i class="fa-solid fa-brain text-info me-2"></i>Dual-AI Vision Configuration
                    </h6>
                    <div class="row g-3 mb-4">
                        <div class="col-md-6">
                            <label class="small text-white fw-bold">
                                <i class="fa-brands fa-google text-danger me-1"></i> Google Gemini API Key
                            </label>
                            <input type="password" id="setting-gemini-key" class="form-control" placeholder="AIzaSy...">
                            <small class="text-secondary">Free tier with multimodal vision at <a href="https://aistudio.google.com" target="_blank" class="text-info">aistudio.google.com</a></small>
                        </div>
                        <div class="col-md-6">
                            <label class="small text-white fw-bold">
                                <i class="fa-solid fa-robot text-success me-1"></i> OpenAI API Key
                            </label>
                            <input type="password" id="setting-openai-key" class="form-control" placeholder="sk-...">
                            <small class="text-secondary">GPT-4o Vision key from <a href="https://platform.openai.com" target="_blank" class="text-info">platform.openai.com</a></small>
                        </div>
                    </div>

                    <!-- Meta Access Token -->
                    <h6 class="fw-bold text-white border-bottom border-secondary pb-2 mb-3">
                        <i class="fa-brands fa-meta text-primary me-2"></i>Meta Graph Access Token (Instagram & Facebook)
                    </h6>
                    <div class="mb-3">
                        <div class="input-group">
                            <input type="password" id="setting-meta-token" class="form-control" placeholder="Paste EAAB... token here">
                            <button class="btn btn-primary fw-bold px-3" type="button" onclick="verifyMetaToken()">
                                <i class="fa-solid fa-link me-1"></i> Connect & Sync
                            </button>
                        </div>
                    </div>
                </div>
                <div class="modal-footer border-secondary">
                    <button type="button" class="btn btn-secondary rounded-pill px-4 fw-bold" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary rounded-pill px-4 fw-bold" onclick="saveSettings()">Save Changes</button>
                </div>
            </div>
        </div>
    </div>

    <!-- DIRECT LOGIN MODAL -->
    <div class="modal fade" id="modalDirectLogin" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content bg-dark text-white border border-secondary rounded-4 shadow-lg">
                <div class="modal-header border-secondary">
                    <h5 class="modal-title fw-bold text-white"><i class="fa-solid fa-right-to-bracket text-primary me-2"></i>Direct Account Login</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body p-4 text-center">
                    <p class="text-white small mb-3">Paste your Meta Access Token to sync Instagram & Facebook:</p>
                    <input type="password" id="login-meta-token" class="form-control mb-3" placeholder="EAAB... token">
                    <button class="btn btn-primary w-100 rounded-pill py-2 fw-bold" onclick="directLoginMeta()">Sync Accounts</button>
                </div>
            </div>
        </div>
    </div>

    <!-- MEDIA PREVIEW MODAL -->
    <div class="modal fade" id="modalVideoPlayer" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered modal-lg">
            <div class="modal-content bg-dark text-white border border-secondary rounded-4 shadow-lg">
                <div class="modal-header border-secondary">
                    <h5 class="modal-title fw-bold text-white"><i class="fa-solid fa-eye text-primary me-2"></i>Media Preview</h5>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" onclick="killVideoPlayback()"></button>
                </div>
                <div class="modal-body text-center p-3">
                    <div id="media-viewer-container" style="max-height: 550px; display: flex; justify-content: center; align-items: center; background: #000; border-radius: 12px; overflow: hidden;">
                        <video id="preview-video-element" controls style="max-height: 520px; max-width: 100%; display: none;"></video>
                        <img id="preview-image-element" style="max-height: 520px; max-width: 100%; display: none; object-fit: contain;">
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Toast Notifications -->
    <div id="toast-container"></div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        let settingsModal = null;
        let videoModal = null;
        let loginModal = null;
        let musicModal = null;
        let currentFeedFilter = "all";
        let allPostsData = [];

        // Multi-image selection state
        let selectedMediaFiles = []; // Array of File objects
        let coverIndex = 0;          // Index of chosen cover in selectedMediaFiles
        let attachedAudio = null;     // { title, artist, preview_url, start_sec, duration_sec, artwork }
        let currentScheduleMode = 'instant'; // 'instant', 'calendar', 'queue'
        let currentTrimDuration = 30;

        document.addEventListener("DOMContentLoaded", () => {
            settingsModal = new bootstrap.Modal(document.getElementById('modalStudioSettings'));
            videoModal = new bootstrap.Modal(document.getElementById('modalVideoPlayer'));
            loginModal = new bootstrap.Modal(document.getElementById('modalDirectLogin'));
            musicModal = new bootstrap.Modal(document.getElementById('modalWorldwideMusic'));

            document.getElementById('modalVideoPlayer').addEventListener('hidden.bs.modal', killVideoPlayback);

            loadInitialData();
            setInterval(refreshStatus, 4000);
            setInterval(loadReelsFeed, 5000);
            setInterval(loadCalendarFeed, 7000);
        });

        function showToast(msg, type = "success") {
            const container = document.getElementById("toast-container");
            const toast = document.createElement("div");
            toast.className = `alert alert-${type === "error" ? "danger" : (type === "warning" ? "warning" : "success")} text-white shadow-lg border-0 d-flex align-items-center gap-2 mb-2`;
            toast.style.background = type === "error" ? "rgba(220, 38, 38, 0.95)" : (type === "warning" ? "rgba(217, 119, 6, 0.95)" : "rgba(16, 185, 129, 0.95)");
            toast.style.backdropFilter = "blur(8px)";
            toast.style.borderRadius = "12px";
            toast.innerHTML = `<i class="fa-solid fa-${type === "error" ? "circle-xmark" : (type === "warning" ? "circle-exclamation" : "circle-check")}"></i> <div>${msg}</div>`;
            container.appendChild(toast);
            setTimeout(() => { toast.remove(); }, 4000);
        }

        // --- MULTI-IMAGE & COVER MANAGEMENT (1 to 12 Photos) ---
        function handleFilesSelected(input) {
            if (!input.files || input.files.length === 0) return;

            const newFiles = Array.from(input.files);
            for (let f of newFiles) {
                if (selectedMediaFiles.length >= 12) {
                    showToast("Maximum 12 pictures allowed per post!", "warning");
                    break;
                }
                selectedMediaFiles.push(f);
            }
            input.value = '';
            renderSelectedMediaGrid();
        }

        function renderSelectedMediaGrid() {
            const grid = document.getElementById('selected-media-grid');
            const container = document.getElementById('media-grid-container');
            const countLabel = document.getElementById('selected-files-count');

            if (selectedMediaFiles.length === 0) {
                container.classList.add('d-none');
                countLabel.innerText = '0 / 12 Media Selected';
                return;
            }

            container.classList.remove('d-none');
            countLabel.innerText = `${selectedMediaFiles.length} / 12 Media Selected`;

            if (coverIndex >= selectedMediaFiles.length) {
                coverIndex = 0;
            }

            let html = '';
            selectedMediaFiles.forEach((file, idx) => {
                const isCover = (idx === coverIndex);
                const isVideo = file.type.startsWith('video/');
                const objUrl = URL.createObjectURL(file);

                html += `
                    <div class="col-4 col-sm-3 col-md-2">
                        <div class="media-preview-card ${isCover ? 'is-cover' : ''}">
                            ${isCover ? '<span class="cover-badge"><i class="fa-solid fa-star me-1"></i>Cover #1</span>' : ''}
                            <span class="order-badge">#${idx + 1}</span>
                            ${isVideo ? 
                                `<video src="${objUrl}" muted></video>` : 
                                `<img src="${objUrl}">`
                            }
                            <div class="media-card-actions">
                                ${!isCover ? 
                                    `<button type="button" class="btn btn-warning py-0 px-1" style="font-size: 0.65rem;" onclick="setCoverIndex(${idx})" title="Make this image the cover">★ Cover</button>` : 
                                    `<span class="badge bg-warning text-dark py-0 px-1" style="font-size: 0.65rem;">Main</span>`
                                }
                                <button type="button" class="btn btn-danger py-0 px-1" style="font-size: 0.65rem;" onclick="removeSelectedFile(${idx})" title="Remove">✕</button>
                            </div>
                        </div>
                    </div>
                `;
            });

            grid.innerHTML = html;
        }

        function setCoverIndex(idx) {
            coverIndex = idx;
            renderSelectedMediaGrid();
            showToast(`Photo #${idx + 1} set as Main Cover (Item #1)!`);
        }

        function removeSelectedFile(idx) {
            selectedMediaFiles.splice(idx, 1);
            if (coverIndex >= selectedMediaFiles.length) coverIndex = 0;
            renderSelectedMediaGrid();
        }

        function clearAllSelectedMedia() {
            selectedMediaFiles = [];
            coverIndex = 0;
            renderSelectedMediaGrid();
        }

        // --- PUBLISHING TIMING MODES & CALENDAR ---
        function setScheduleMode(mode) {
            currentScheduleMode = mode;
            document.getElementById('timing-btn-instant').classList.remove('active');
            document.getElementById('timing-btn-calendar').classList.remove('active');
            document.getElementById('timing-btn-queue').classList.remove('active');

            const calBox = document.getElementById('calendar-picker-box');
            const submitBtn = document.getElementById('btn-submit-post');

            if (mode === 'instant') {
                document.getElementById('timing-btn-instant').classList.add('active');
                calBox.classList.add('d-none');
                submitBtn.innerHTML = '<i class="fa-solid fa-rocket me-2"></i>Publish Immediately Right Now';
                submitBtn.className = 'btn btn-success w-100 py-3 rounded-pill fw-bold fs-5 shadow';
            } else if (mode === 'calendar') {
                document.getElementById('timing-btn-calendar').classList.add('active');
                calBox.classList.remove('d-none');
                setQuickTime(60); // default to 1 hr in future
                submitBtn.innerHTML = '<i class="fa-solid fa-calendar-check me-2"></i>Schedule Post on Calendar';
                submitBtn.className = 'btn btn-info text-dark w-100 py-3 rounded-pill fw-bold fs-5 shadow';
            } else {
                document.getElementById('timing-btn-queue').classList.add('active');
                calBox.classList.add('d-none');
                submitBtn.innerHTML = '<i class="fa-solid fa-clock me-2"></i>Add to Auto-Pilot Queue (Smart Delay)';
                submitBtn.className = 'btn btn-primary w-100 py-3 rounded-pill fw-bold fs-5 shadow';
            }
        }

        function setQuickTime(mins) {
            const d = new Date(Date.now() + mins * 60000);
            d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
            document.getElementById('custom-schedule-datetime').value = d.toISOString().slice(0, 16);
        }

        function setTomorrowTime(hour) {
            const d = new Date();
            d.setDate(d.getDate() + 1);
            d.setHours(hour, 0, 0, 0);
            d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
            document.getElementById('custom-schedule-datetime').value = d.toISOString().slice(0, 16);
        }

        // --- WORLDWIDE MUSIC SEARCH & TRIMMER ---
        function openMusicModal() {
            musicModal.show();
            if (!document.getElementById('music-search-query').value) {
                document.getElementById('music-search-query').value = 'Trending Hits';
                executeMusicSearch();
            }
        }

        function setTrimDuration(dur) {
            currentTrimDuration = dur;
            ['15', '30', '60'].forEach(d => {
                document.getElementById(`btn-dur-${d}`).classList.remove('active');
            });
            document.getElementById(`btn-dur-${dur}`).classList.add('active');
        }

        async function executeMusicSearch() {
            const query = document.getElementById('music-search-query').value.trim() || 'Trending Hits';
            const container = document.getElementById('music-search-results');
            container.innerHTML = '<div class="text-center py-4 text-info"><i class="fa-solid fa-spinner fa-spin fs-4 mb-2"></i><div>Searching 100M+ global songs...</div></div>';

            try {
                const res = await fetch(`/api/audio/search?q=${encodeURIComponent(query)}&limit=25`);
                const data = await res.json();
                if (data.success && data.tracks && data.tracks.length > 0) {
                    let html = '';
                    data.tracks.forEach(t => {
                        const escapedTitle = (t.title || '').replace(/"/g, '&quot;');
                        const escapedArtist = (t.artist || '').replace(/"/g, '&quot;');
                        html += `
                            <div class="p-3 bg-dark bg-opacity-75 rounded-3 border border-secondary mb-2 d-flex justify-content-between align-items-center gap-3">
                                <div class="d-flex align-items-center gap-3">
                                    <img src="${t.artwork || 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=100'}" style="width: 50px; height: 50px; border-radius: 8px; object-fit: cover;">
                                    <div>
                                        <div class="fw-bold text-white small text-truncate" style="max-width: 260px;">${escapedTitle}</div>
                                        <div class="text-secondary small text-truncate" style="max-width: 260px;">${escapedArtist}</div>
                                        <audio controls src="${t.preview_url}" style="height: 28px; width: 220px; margin-top: 4px;"></audio>
                                    </div>
                                </div>
                                <button type="button" class="btn btn-sm btn-primary rounded-pill px-3 fw-bold" onclick="selectMusicTrack('${t.id}', '${escapedTitle}', '${escapedArtist}', '${t.preview_url}', '${t.artwork}')">
                                    <i class="fa-solid fa-check me-1"></i> Attach
                                </button>
                            </div>
                        `;
                    });
                    container.innerHTML = html;
                } else {
                    container.innerHTML = '<div class="text-center py-4 text-secondary">No songs found for that search query. Try another artist or track name!</div>';
                }
            } catch (e) {
                container.innerHTML = `<div class="text-center py-4 text-danger">Search error: ${e}</div>`;
            }
        }

        function selectMusicTrack(id, title, artist, previewUrl, artwork) {
            const startSec = parseInt(document.getElementById('slider-trim-start').value || '0');
            attachedAudio = {
                id: id,
                title: title,
                artist: artist,
                preview_url: previewUrl,
                artwork: artwork,
                start_sec: startSec,
                duration_sec: currentTrimDuration
            };

            document.getElementById('attached-music-title').innerText = title;
            document.getElementById('attached-music-subtitle').innerText = `${artist} (Trim: ${startSec}s - ${currentTrimDuration}s)`;
            document.getElementById('attached-music-art').innerHTML = `<img src="${artwork}" style="width: 100%; height: 100%; object-fit: cover;">`;
            document.getElementById('btn-remove-music').classList.remove('d-none');

            musicModal.hide();
            showToast(`Attached song: ${title} (${currentTrimDuration}s trim)`);
        }

        function removeAttachedMusic() {
            attachedAudio = null;
            document.getElementById('attached-music-title').innerText = "No Audio Attached (Optional)";
            document.getElementById('attached-music-subtitle').innerText = "Pick from 100M+ global songs with custom trim";
            document.getElementById('attached-music-art').innerHTML = '<i class="fa-solid fa-music"></i>';
            document.getElementById('btn-remove-music').classList.add('d-none');
        }

        // --- AI VISION CAPTION GENERATION ---
        async function generateAICaptionForMedia() {
            if (selectedMediaFiles.length === 0) {
                showToast("Please choose at least 1 photo first to analyze with AI Vision!", "warning");
                return;
            }

            const primaryFile = selectedMediaFiles[coverIndex] || selectedMediaFiles[0];
            showToast("Gemini 1.5 & GPT-4o Vision inspecting product photo...", "warning");
            const fd = new FormData();
            fd.append("file", primaryFile);

            try {
                const res = await fetch('/api/ai/analyze-media', { method: 'POST', body: fd });
                const d = await res.json();
                if (d.success) {
                    if (d.caption) document.getElementById('post-caption-input').value = d.caption;
                    if (d.hashtags) document.getElementById('post-hashtags-input').value = d.hashtags;
                    showToast("AI Vision Hook & Hashtags generated successfully!");
                } else {
                    showToast(d.error || "AI Vision failed", "error");
                }
            } catch (e) {
                showToast("AI Vision error: " + e, "error");
            }
        }

        // --- SUBMIT POST (1-12 PHOTOS, COVER, SCHEDULER, CAROUSEL) ---
        async function submitPostAction() {
            if (selectedMediaFiles.length === 0) {
                showToast("Please select at least 1 image or video to post!", "warning");
                return;
            }

            const platform = document.querySelector('input[name="post-platform"]:checked').value;
            const caption = document.getElementById('post-caption-input').value.trim();
            const hashtags = document.getElementById('post-hashtags-input').value.trim();
            const schedTime = document.getElementById('custom-schedule-datetime').value;

            if (currentScheduleMode === 'calendar' && !schedTime) {
                showToast("Please pick a date and time on the calendar!", "warning");
                return;
            }

            const fd = new FormData();
            selectedMediaFiles.forEach(f => {
                fd.append('files', f);
            });
            fd.append('main_index', coverIndex);
            fd.append('platform', platform);
            fd.append('caption', caption);
            fd.append('hashtags', hashtags);
            fd.append('schedule_mode', currentScheduleMode);
            fd.append('scheduled_time', schedTime);
            if (attachedAudio) {
                fd.append('custom_audio_url', attachedAudio.preview_url);
                fd.append('audio_trim_start', attachedAudio.start_sec);
                fd.append('audio_trim_duration', attachedAudio.duration_sec);
            }

            showToast("Processing media and configuring multi-platform upload...", "warning");

            try {
                const res = await fetch('/api/upload', { method: 'POST', body: fd });
                const d = await res.json();
                if (d.success) {
                    showToast(d.message || "Post created successfully!");
                    clearAllSelectedMedia();
                    removeAttachedMusic();
                    document.getElementById('post-caption-input').value = '';
                    loadReelsFeed();
                    loadCalendarFeed();
                } else {
                    showToast("Error: " + (d.error || "Upload failed"), "error");
                }
            } catch (e) {
                showToast("Upload error: " + e, "error");
            }
        }

        // --- CALENDAR FEED LOADER ---
        async function loadCalendarFeed() {
            const container = document.getElementById('calendar-feed-container');
            try {
                const res = await fetch('/api/calendar');
                const data = await res.json();
                if (!data.success || !data.events || data.events.length === 0) {
                    container.innerHTML = `
                        <div class="col-12 text-center py-4 text-secondary">
                            <i class="fa-solid fa-calendar-check fs-2 text-info opacity-50 mb-2"></i>
                            <div class="fw-bold text-white">No Upcoming Scheduled Posts</div>
                            <small>Use "Calendar Schedule" above to plan posts for exact future dates & times!</small>
                        </div>
                    `;
                    return;
                }

                let html = '';
                data.events.forEach(ev => {
                    const isCarousel = ev.media_type === 'carousel';
                    const plat = ev.target_platform || 'instagram';
                    let platBadge = '<span class="badge" style="background: var(--insta-grad);">INSTAGRAM</span>';
                    if (plat === 'facebook') platBadge = '<span class="badge bg-primary">FACEBOOK</span>';

                    let typeBadge = isCarousel ? '<span class="badge bg-warning text-dark"><i class="fa-solid fa-images me-1"></i>Album</span>' : '<span class="badge bg-secondary">Single</span>';

                    html += `
                        <div class="col-md-6 col-lg-4">
                            <div class="p-3 bg-dark bg-opacity-75 rounded-3 border border-secondary d-flex flex-column justify-content-between h-100">
                                <div>
                                    <div class="d-flex justify-content-between align-items-center mb-2">
                                        <div class="d-flex gap-1">${platBadge} ${typeBadge}</div>
                                        <span class="badge bg-info text-dark fw-bold"><i class="fa-solid fa-clock me-1"></i>${ev.scheduled_countdown || 'Scheduled'}</span>
                                    </div>
                                    <div class="small text-white fw-bold text-truncate mb-1">${ev.caption || 'No caption'}</div>
                                    <div class="small text-secondary font-monospace" style="font-size: 0.75rem;">Time: ${ev.scheduled_time || 'Queue'}</div>
                                </div>
                                <div class="d-flex gap-2 mt-3 pt-2 border-top border-secondary">
                                    <button class="btn btn-sm btn-success rounded-pill flex-grow-1 fw-bold" onclick="forcePost(${ev.id})">
                                        <i class="fa-solid fa-bolt me-1"></i> Post Now
                                    </button>
                                    <button class="btn btn-sm btn-outline-danger rounded-pill px-3" onclick="deletePost(${ev.id})">
                                        <i class="fa-solid fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                });
                container.innerHTML = html;
            } catch (e) {}
        }

        // --- REELS FEED & STATUS ---
        async function loadReelsFeed() {
            try {
                const res = await fetch('/api/posts');
                allPostsData = await res.json();
                renderPosts();
            } catch (e) {}
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
                filtered = allPostsData.filter(p => p.target_platform === currentFeedFilter);
            }

            if (!filtered || filtered.length === 0) {
                container.innerHTML = `
                    <div class="col-12 text-center py-5">
                        <i class="fa-solid fa-film fs-1 text-primary mb-3 d-block opacity-50"></i>
                        <h5 class="fw-bold text-white">No Posts Found for ${currentFeedFilter.toUpperCase()}</h5>
                        <p class="text-white small mb-3" style="opacity: 0.8;">Upload media above or drop into watch folders!</p>
                    </div>
                `;
                return;
            }

            let html = '';
            filtered.forEach(p => {
                const plat = p.target_platform || 'instagram';
                let platBadge = '<span class="badge" style="background: var(--insta-grad);">INSTAGRAM</span>';
                if (plat === 'facebook') platBadge = '<span class="badge bg-primary">FACEBOOK</span>';

                const isCarousel = p.media_type === 'carousel';
                const isImage = p.media_type === 'image';
                let typeBadge = '<span class="badge bg-secondary"><i class="fa-solid fa-video me-1"></i>Reel</span>';
                if (isCarousel) typeBadge = '<span class="badge bg-warning text-dark"><i class="fa-solid fa-images me-1"></i>Album</span>';
                if (isImage) typeBadge = '<span class="badge bg-info text-dark"><i class="fa-solid fa-image me-1"></i>Photo</span>';

                let statusBadge = '<span class="badge bg-warning text-dark fw-bold">Processing...</span>';
                if (p.status === 'SCHEDULED') {
                    statusBadge = `<span class="badge bg-primary text-white fw-bold"><i class="fa-solid fa-clock me-1"></i> ${p.scheduled_countdown || 'Ready'}</span>`;
                } else if (p.status === 'UPLOADED') {
                    statusBadge = `<span class="badge bg-success text-white fw-bold"><i class="fa-solid fa-check me-1"></i> Live</span>`;
                } else if (p.status === 'FAILED') {
                    statusBadge = `<span class="badge bg-danger text-white fw-bold"><i class="fa-solid fa-triangle-exclamation me-1"></i> Failed</span>`;
                }

                // Resolve preview filename
                let previewFile = '';
                if (p.processed_path) {
                    previewFile = p.processed_path.split(/[\\\\/]/).pop();
                } else if (p.file_path) {
                    if (p.file_path.trim().startsWith('[')) {
                        try {
                            const arr = JSON.parse(p.file_path);
                            previewFile = (arr[0] || '').split(/[\\\\/]/).pop();
                        } catch (e) {}
                    } else {
                        previewFile = p.file_path.split(/[\\\\/]/).pop();
                    }
                }

                const thumbUrl = previewFile ? `/api/media/${previewFile}` : 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=500';

                html += `
                    <div class="col-md-6 col-lg-4">
                        <div class="reel-card">
                            <div class="reel-thumb-container" onclick="previewMediaItem('${previewFile}')">
                                <img src="${thumbUrl}" class="reel-thumb-img" onerror="this.src='https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=500'">
                                <div class="reel-play-btn"><i class="fa-solid fa-${p.media_type === 'video' ? 'play' : 'eye'} ms-1"></i></div>
                                <div style="position: absolute; top: 12px; left: 12px; display: flex; gap: 4px;">${platBadge} ${typeBadge}</div>
                                <div style="position: absolute; bottom: 12px; left: 12px;">${statusBadge}</div>
                            </div>
                            <div class="p-3 d-flex flex-column justify-content-between flex-grow-1">
                                <div>
                                    <div class="text-white fw-bold small mb-2" style="display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">
                                        ${p.caption || 'Product post'}
                                    </div>
                                    <div class="text-info small fw-semibold text-truncate mb-3">${p.hashtags || '#viral'}</div>
                                    ${p.status === 'FAILED' && p.error_message ? `<div class="alert alert-danger p-2 small mb-2 text-truncate" style="font-size:0.75rem;">${p.error_message}</div>` : ''}
                                </div>
                                <div class="d-flex gap-2 pt-2 border-top border-secondary">
                                    ${(p.status === 'SCHEDULED' || p.status === 'QUEUED') ? 
                                        `<button class="btn btn-sm btn-success rounded-pill flex-grow-1 fw-bold" onclick="forcePost(${p.id})"><i class="fa-solid fa-bolt me-1"></i> Post Now</button>` : 
                                        (p.remote_url ? `<a href="${p.remote_url}" target="_blank" class="btn btn-sm btn-outline-info rounded-pill flex-grow-1 fw-bold"><i class="fa-solid fa-arrow-up-right-from-square me-1"></i> View Live</a>` : '')
                                    }
                                    <button class="btn btn-sm btn-outline-light rounded-pill px-3" onclick="previewMediaItem('${previewFile}')"><i class="fa-solid fa-eye"></i></button>
                                    <button class="btn btn-sm btn-outline-danger rounded-pill px-3" onclick="deletePost(${p.id})"><i class="fa-solid fa-trash"></i></button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            container.innerHTML = html;
        }

        function previewMediaItem(filename) {
            if (!filename) return;
            const videoElem = document.getElementById('preview-video-element');
            const imgElem = document.getElementById('preview-image-element');

            const isVideo = ['.mp4', '.mov', '.webm'].some(ext => filename.toLowerCase().endsWith(ext));
            const mediaUrl = `/api/media/${filename}`;

            if (isVideo) {
                imgElem.style.display = 'none';
                videoElem.style.display = 'block';
                videoElem.src = mediaUrl;
                videoElem.play().catch(e => {});
            } else {
                videoElem.pause();
                videoElem.style.display = 'none';
                imgElem.style.display = 'block';
                imgElem.src = mediaUrl;
            }
            videoModal.show();
        }

        function killVideoPlayback() {
            const v = document.getElementById('preview-video-element');
            if (v) {
                v.pause();
                v.src = "";
            }
        }

        async function forcePost(id) {
            showToast("Publishing post immediately...", "warning");
            try {
                const res = await fetch(`/api/posts/${id}/post-now`, { method: 'POST' });
                const d = await res.json();
                if (d.success) {
                    showToast("Upload triggered!");
                    loadReelsFeed();
                    loadCalendarFeed();
                } else {
                    showToast(d.error || "Failed", "error");
                }
            } catch (e) {
                showToast("Error: " + e, "error");
            }
        }

        async function deletePost(id) {
            if (!confirm("Are you sure you want to delete this post?")) return;
            try {
                await fetch(`/api/posts/${id}/delete`, { method: 'POST' });
                showToast("Post deleted");
                loadReelsFeed();
                loadCalendarFeed();
            } catch (e) {}
        }

        async function openFolder(f) {
            try {
                await fetch('/api/open-folder', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ folder: f })
                });
                showToast(`Opened ${f} folder on PC!`);
            } catch (e) {}
        }

        // --- ACCOUNTS & SETTINGS ---
        function openSettingsModal() {
            settingsModal.show();
        }

        function openLoginModal() {
            loginModal.show();
        }

        async function directLoginMeta() {
            const token = document.getElementById('login-meta-token').value.trim();
            if (!token) return;
            showToast("Connecting Meta token...", "warning");
            try {
                const res = await fetch('/api/accounts/connect-meta', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ token: token })
                });
                const d = await res.json();
                if (d.success) {
                    showToast(d.message || "Connected!");
                    loginModal.hide();
                    loadAccounts();
                } else {
                    showToast(d.error || "Connection failed", "error");
                }
            } catch (e) {
                showToast("Error: " + e, "error");
            }
        }

        async function verifyMetaToken() {
            const token = document.getElementById('setting-meta-token').value.trim();
            if (!token) return;
            showToast("Verifying Meta access token...", "warning");
            try {
                const res = await fetch('/api/accounts/connect-meta', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ token: token })
                });
                const d = await res.json();
                if (d.success) {
                    showToast(d.message || "Meta token verified & synced!");
                    loadAccounts();
                } else {
                    showToast("Meta error: " + (d.error || "Failed"), "error");
                }
            } catch (e) {
                showToast("Verification error: " + e, "error");
            }
        }

        async function saveSettings() {
            const body = {
                brand_name: document.getElementById('setting-brand-name').value.trim(),
                gemini_api_key: document.getElementById('setting-gemini-key').value.trim(),
                openai_api_key: document.getElementById('setting-openai-key').value.trim(),
                meta_access_token: document.getElementById('setting-meta-token').value.trim(),
                r2_account_id: document.getElementById('setting-r2-account-id').value.trim(),
                r2_bucket_name: document.getElementById('setting-r2-bucket-name').value.trim(),
                r2_access_key_id: document.getElementById('setting-r2-access-key').value.trim(),
                r2_secret_access_key: document.getElementById('setting-r2-secret-key').value.trim(),
                r2_public_domain: document.getElementById('setting-r2-public-domain').value.trim()
            };

            try {
                const res = await fetch('/api/settings', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(body)
                });
                const d = await res.json();
                if (d.success) {
                    showToast("Settings saved successfully!");
                    settingsModal.hide();
                    loadInitialData();
                } else {
                    showToast("Error saving: " + d.error, "error");
                }
            } catch (e) {
                showToast("Save error: " + e, "error");
            }
        }

        async function loadInitialData() {
            try {
                const sRes = await fetch('/api/settings');
                const s = await sRes.json();
                if (s.brand_name) {
                    document.getElementById('setting-brand-name').value = s.brand_name;
                    document.getElementById('hero-brand-name').innerText = s.brand_name;
                }
                if (s.gemini_api_key) document.getElementById('setting-gemini-key').value = s.gemini_api_key;
                if (s.openai_api_key) document.getElementById('setting-openai-key').value = s.openai_api_key;
                if (s.meta_access_token) document.getElementById('setting-meta-token').value = s.meta_access_token;
                if (s.r2_account_id) document.getElementById('setting-r2-account-id').value = s.r2_account_id;
                if (s.r2_bucket_name) document.getElementById('setting-r2-bucket-name').value = s.r2_bucket_name;
                if (s.r2_access_key_id) document.getElementById('setting-r2-access-key').value = s.r2_access_key_id;
                if (s.r2_secret_access_key) document.getElementById('setting-r2-secret-key').value = s.r2_secret_access_key;
                if (s.r2_public_domain) document.getElementById('setting-r2-public-domain').value = s.r2_public_domain;

                loadAccounts();
                loadReelsFeed();
                loadCalendarFeed();
            } catch (e) {}
        }

        async function loadAccounts() {
            try {
                const res = await fetch('/api/accounts');
                const data = await res.json();
                if (data.instagram && data.instagram.username) {
                    document.getElementById('chip-insta').innerText = '@' + data.instagram.username;
                }
                if (data.facebook && data.facebook.page_name) {
                    document.getElementById('chip-fb').innerText = data.facebook.page_name;
                }
            } catch (e) {}
        }

        async function refreshStatus() {
            try {
                const res = await fetch('/api/status');
                const d = await res.json();
                if (d.daily_counts) {
                    document.getElementById('stat-ig-count').innerText = `${d.daily_counts.instagram || 0}/3`;
                    document.getElementById('stat-fb-count').innerText = `${d.daily_counts.facebook || 0}/3`;
                }
            } catch (e) {}
        }

        async function toggleAutoPilot(checkbox) {
            const mode = checkbox.checked ? 'human_delay' : 'instant';
            try {
                await fetch('/api/scheduler/mode', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ mode: mode })
                });
                document.getElementById('autopilot-mode-label').innerText = checkbox.checked ? 'Anti-Spam 2-3h Delay' : 'Instant Publishing';
                showToast(`Auto-Pilot mode set to: ${mode}`);
            } catch (e) {}
        }
    </script>
</body>
</html>
"""
