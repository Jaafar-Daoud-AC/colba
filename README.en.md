<div align="center">

# 🏪 COLBA

**A web app for inventory and accounting management in small and medium shops and warehouses**

*It started as a desktop program I used to learn programming, version after version, and grew into a full web application deployed online*

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase&logoColor=white)
![PWA](https://img.shields.io/badge/PWA-Installable-5A0FC8?logo=pwa&logoColor=white)
![Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?logo=render&logoColor=white)
![Release](https://img.shields.io/github/v/release/Jaafar-Daoud-AC/colba?label=release)

[🇬🇧 English](README.en.md) · [🇸🇦 العربية](README.md)

### 🔗 [Live app: colba.onrender.com](https://colba.onrender.com)

</div>

---

> [!WARNING]
> ## ⚠️ **IMPORTANT: Database notice**
> **The database is Supabase (free tier), which is automatically paused after one week of inactivity.**
> **Because of this, the live demo may not work as it would in real use (you may see errors or empty data).**
> The link is meant for browsing the interface and design. If the data fails to load, this is most likely the reason, not a bug in the code.
>
> *Also:* the free Render server sleeps when idle, so the first page load can take about a minute.

---

## 📖 About

**COLBA** manages shops and warehouses: inventory, receiving invoices, stocktaking, expenses, a cash box, and statistics and analytics, all in an Arabic (RTL), mobile-first interface that can be installed on a phone as an app (PWA).

> ✅ **It was designed for a specific private business, has been tested in real use with excellent performance, and suits small and medium shops and warehouses.**

The core idea: **no manual editing of quantities or sales.** Every stock increase goes through an invoice, every sale is derived from stocktake differences, and every cash withdrawal requires a written reason, so every number leaves a documented trail.

---

## 🌐 Try it

| | |
|---|---|
| **Link** | **[colba.onrender.com](https://colba.onrender.com)** |
| **Best on** | A phone (Chrome) or any modern browser |
| **Heads up** | See the database warning above |

---

## ✨ Features

### Main screens

| Screen | What it does |
|--------|--------------|
| 🏠 **Home** | Capital, total and actual returns, costs, taxes and wages, cash box balance, and cash surplus/deficit |
| 📦 **Products** | Unlimited list, categories, add/edit/delete, and invoices per product |
| 📊 **Stats** | Daily statistics, end-of-day closing, and cash count history |
| 📝 **Stocktake** | Start/end stocktake sessions; the difference is recorded as a sale automatically |
| 📈 **Analytics** | Time series, top sellers, highest/lowest quantities sold, and buy/sell price changes |

### Accounting logic

- 🧾 **Invoice-driven stock:** quantities are never edited by hand; every invoice is kept in a permanent, sortable history (date, cost, quantity).
- 🔄 **Revaluation:** when an invoice arrives with a different purchase price, the effect on the existing quantity is computed automatically as a gain or loss and stored in its own log.
- 💸 **Documented daily expenses:** each expense has a category and a reason, and is deducted from the cash box automatically.
- 💰 **Cash count:** enter the real amount in the box; the system compares it with the expected amount and stores the surplus or deficit over time.
- 🔐 **Mandatory note on withdrawals:** no withdrawal without a reason.
- 🧮 **Server-side calculations:** every figure is computed from the actual data in the database.

### Experience and tech

- 📱 **Installable app (PWA)** on Android, no app store needed.
- 🌙 **Arabic RTL interface** with the Tajawal font, fully responsive.
- ⚡ **Service Worker** for faster loading and partial offline support.
- 🩺 **Health check** endpoint at `/api/health`.
- 🗄️ **SQLite locally and PostgreSQL in production**, switched automatically through `DATABASE_URL`.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.11, Flask 3.0, Flask-SQLAlchemy 3.1 |
| **Database** | SQLite (local), PostgreSQL on Supabase (production) via psycopg 3 |
| **Frontend** | Vanilla HTML + CSS + JavaScript (no framework) |
| **App** | PWA: Web App Manifest + Service Worker |
| **Server & deploy** | Gunicorn, Render |

---

## 📁 Project Structure

```
colba/
├── app.py              # Backend + API + models
├── requirements.txt    # Dependencies
├── render.yaml         # Render deployment config
├── CHANGELOG.md        # Changes between versions
└── frontend/
    ├── index.html
    ├── styles.css
    ├── app.js
    ├── manifest.json   # PWA settings
    ├── sw.js           # Service Worker
    └── icons/
```

### Database models

`Category` · `Product` · `Costs` · `SaleRecord` · `BoxTransaction` · `StocktakeSession` · `Invoice` · `InvoiceItem` · `PriceChangeLog` · `CashCount`

---

## 🚀 Run Locally

```bash
git clone https://github.com/Jaafar-Daoud-AC/colba.git
cd colba
pip install -r requirements.txt
python3 app.py
```

Opens at `http://localhost:5000`. A local SQLite database (`colba.db`) is created automatically and is not tracked by Git.

### Using PostgreSQL / Supabase

Set the `DATABASE_URL` environment variable to your connection string before starting; the app detects it automatically:

```bash
export DATABASE_URL="postgresql://USER:PASSWORD@HOST:5432/DBNAME"
python3 app.py
```

> 🔒 **Never commit your connection string to GitHub**, since it contains the database password. Keep it in environment variables only (locally or in the Render dashboard).

---

## ☁️ Deploy to Render

1. Push the project to a GitHub repository.
2. On [render.com](https://render.com) choose **New → Web Service** and connect the repo (branch `main`).
3. Render reads `render.yaml` automatically:
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `gunicorn app:app --bind 0.0.0.0:$PORT`
4. Add `DATABASE_URL` under **Environment** with your database connection string.

---

## 📲 Install on Android

1. Open the link in **Chrome** on your phone.
2. Tap the menu (⋮).
3. Choose **"Install app"** or **"Add to Home screen"**.
4. The COLBA icon appears on your screen and opens full-screen like any app.

---

## 🔌 API (summary)

| Route | Purpose |
|-------|---------|
| `/api/products` · `/api/categories` | Products and categories |
| `/api/invoices` | Receiving invoices |
| `/api/price-changes` | Price change log and revaluation |
| `/api/stocktake/*` | Stocktake sessions |
| `/api/box/transactions` | Cash box movements |
| `/api/summary` | Financial summary |
| `/api/stats/*` | Daily stats and cash counts |
| `/api/analytics/*` | Analytics and charts |
| `/api/health` | Service health check |

---

## 🕰️ Development Journey: From Desktop to Web

COLBA began as a **Tkinter** desktop program and evolved through successive versions, each teaching me something new, until I rebuilt it completely as a web app.

| Version | Platform | Highlights |
|---------|----------|------------|
| `v0.1.3` → `v0.1.6` | Desktop (Tkinter + SQLite) | The basics: product tables, add/edit/delete, totals, daily and stocktake screens |
| `v0.1.7` | Desktop | Code reorganized with helper functions, and matplotlib charts |
| `v0.1.9` | Desktop | Multiple databases (create a new one or pick an existing one) |
| **`v1.0.0`** | **Web (Flask + PWA)** | **Full rebuild: invoices, revaluation, cash count, analytics, PostgreSQL** |

> 📂 Old versions are preserved in the [`legacy/desktop`](https://github.com/Jaafar-Daoud-AC/colba/tree/legacy/desktop) branch, while the current version always lives on `main`. Details for each version are on the [Releases](https://github.com/Jaafar-Daoud-AC/colba/releases) page and in [CHANGELOG.md](CHANGELOG.md).

---

## 🎓 What I Learned

- Building a complete **REST API** with Flask and modeling data with SQLAlchemy.
- Moving from **text files** to **SQLite** and then to **PostgreSQL**.
- Practical SQLite vs PostgreSQL differences (such as strict date comparisons) and the **psycopg 3** driver.
- Turning a desktop program into a **responsive web app** with no framework.
- Building a **PWA**: Manifest, Service Worker, and cache versioning.
- Designing **accounting logic** with a documented trail: invoices, revaluation, stocktake, and surplus/deficit.
- Deploying on **Render**, managing environment variables, and protecting secrets.
- Managing **releases** with Git, Semantic Versioning, and GitHub Releases.

---

## 🗺️ Roadmap

- [ ] User login and permissions.
- [ ] Automatic data backups.
- [ ] Report export (PDF / Excel).
- [ ] Multi-branch / multi-warehouse support.
- [ ] Automated tests.

---

## ⚠️ Notes

- **The app currently has no login system.** Avoid putting sensitive real data on a public link without extra protection.
- The live link is for browsing the interface; its data may be empty or unavailable (see the database warning above).
- Never commit database files (`*.db`) or your `.env` file to the repository.

---

## 🤝 Contributing

Feedback and suggestions are welcome. Feel free to open an **Issue** or submit a **Pull Request**.

---

## 📄 License

Released under the **MIT** License.

---

## 👤 Author

**Jaafar Daoud** (جعفر داؤد)

- GitHub: [@Jaafar-Daoud-AC](https://github.com/Jaafar-Daoud-AC)
- Other projects: [Gold & Dollar Telegram bot](https://github.com/Jaafar-Daoud-AC/pot_telegram)

<div align="center">

⭐ If you like this project, consider giving it a star!

</div>
