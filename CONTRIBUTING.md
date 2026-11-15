# 🤝 Contributing to SPHEREx Hunter

Thank you for contributing to **SPHEREx Hunter** (Team RIP, NASA Space Apps Challenge 2026)! Whether you are an experienced software engineer, an astrophysics researcher, or a GitHub beginner, your contributions are welcome.

---

## 🚀 Quick Links
- 📘 **Complete GitHub Guide (Beginners & Pros):** [`docs/GITHUB_GUIDE.md`](docs/GITHUB_GUIDE.md)
- 🖥️ **UI & Observatory Guide:** [`docs/UI_GUIDE.md`](docs/UI_GUIDE.md)
- 🛰️ **API & Backend Contract:** [`docs/API_CONTRACT.md`](docs/API_CONTRACT.md)

---

## 🌟 For GitHub Beginners (Newbies)
If you are new to GitHub:
1. You can browse and edit files directly in your browser by pressing the <kbd>.</kbd> key on the main repository page!
2. To report bugs or suggest ideas, open a [GitHub Issue](https://github.com/joker0210G/spherex-hunter/issues) using our pre-built issue templates.
3. Don't worry about breaking anything: the `main` branch is protected, so exploring and learning is completely safe. Check out our [Beginner's Guide in `docs/GITHUB_GUIDE.md`](docs/GITHUB_GUIDE.md#-section-1-the-absolute-beginners-guide-github-newbies) for simple step-by-step instructions.

---

## ⚡ For Developers (GitHub Flow)

### 1. Branch Ownership
Never push directly to `main`. Work on your assigned track branch:
* `coolodu/web-frontend`: User interface, WebGL FITS viewer, HUD telemetry (`frontend/`).
* `darkodu/astro-backend`: FastAPI endpoints, NASA IRSA TAP, Gaia queries (`backend/`).
* `iceodu/image-math-ai`: Co-addition, PSF difference imaging, matrix math (`image_engine/`).
* `astrodu/ui-story-pitch`: Presentation docs, citizen science guide, UI assets (`docs/`).

### 2. Commit Message Standards
We follow [Conventional Commits](https://www.conventionalcommits.org/):
```
feat(scope): add new capability
fix(scope): resolve bug or visual defect
refactor(scope): optimize structure without changing behavior
docs(scope): update documentation or memory sync
test(scope): add automated test assertions
```

### 3. Local Verification Before Pushing
Always verify that the test suite passes locally before pushing or opening a PR:
```powershell
python -m pytest tests/test_ui_contract.py tests/test_golden_suite.py tests/test_viewport_overhaul_v2.py
ruff check backend/
```

### 4. Opening a Pull Request
1. Push your changes to your feature or track branch on GitHub.
2. Open a Pull Request targeting `main`.
3. Provide a clear summary and reference any related GitHub issues.
4. All automated tests must pass 100% green before merging.
