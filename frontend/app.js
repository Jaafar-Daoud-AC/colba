// ============================================================
// كولبا - منطق التطبيق (يستهلك API الخاص بالباك اند Flask)
// ============================================================

const API = "/api";

const state = {
  products: [],
  categories: [],
  costs: null,
  summary: null,
  currentView: "home",
  analyticsPeriod: "daily",
  topPeriod: "all",
  topSortBy: "quantity",
  invoicesSort: "date_desc",
  laborMode: "percent",
  visibility: {
    "section-totals": true,
    "section-timeseries": true,
    "section-top": true,
    "section-minmax": true,
    "section-product-chart": false,
    "section-price-changes": true,
  },
  priceChangeArrows: {}, // "{product_id}:buy" أو "{product_id}:sell" -> {direction, old_price, new_price}
};

const VISIBILITY_KEY = "colba_analytics_visibility"; // ملاحظة: نخزنها في الذاكرة فقط (لا localStorage) — انظر تحميل الحالة أدناه

// -------------------- أدوات مساعدة --------------------

function money(n) {
  const num = Number(n) || 0;
  return num.toLocaleString("en-US", { maximumFractionDigits: 2 });
}

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function showToast(msg, isError = false) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.classList.remove("hidden", "error");
  if (isError) el.classList.add("error");
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => el.classList.add("hidden"), 2600);
}

async function api(path, options = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || "حدث خطأ غير متوقع");
  }
  document.getElementById("db-warning").classList.add("hidden");
  return data;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// -------------------- فحص الاتصال بقاعدة البيانات --------------------

async function checkHealth() {
  try {
    const res = await fetch(API + "/health");
    if (!res.ok) throw new Error();
    document.getElementById("db-warning").classList.add("hidden");
  } catch (err) {
    document.getElementById("db-warning").classList.remove("hidden");
  }
}

// -------------------- التنقل بين الشاشات --------------------

function switchView(view) {
  state.currentView = view;
  document.querySelectorAll(".view").forEach((v) => v.classList.add("hidden"));
  document.getElementById(`view-${view}`).classList.remove("hidden");
  document.querySelectorAll(".nav-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.view === view);
  });
  if (view === "products") loadProducts();
  if (view === "stats") loadDailyStats();
  if (view === "home") { loadSummary(); }
  if (view === "analytics") loadAnalytics();
  if (view === "stocktake") loadStocktakeView();
}

document.querySelectorAll(".nav-btn").forEach((btn) => {
  btn.addEventListener("click", () => switchView(btn.dataset.view));
});

// -------------------- الشاشة الرئيسية / الملخص --------------------

async function loadSummary() {
  try {
    const [summary, costs] = await Promise.all([api("/summary"), api("/costs")]);
    state.summary = summary;
    state.costs = costs;
    state.laborMode = costs.labor_mode || "percent";

    document.getElementById("stat-capital").textContent = money(summary.capital);
    document.getElementById("stat-total-return").textContent = money(summary.total_return);
    document.getElementById("stat-actual-return").textContent = money(summary.actual_return);
    document.getElementById("stat-box-balance").textContent = money(summary.box_balance);
    document.getElementById("stat-total-capital-box").textContent = money(summary.total_capital_with_box);

    const surplusEl = document.getElementById("stat-cash-surplus");
    const surplusCard = document.getElementById("stat-cash-surplus-card");
    surplusEl.textContent = money(summary.cash_surplus);
    surplusCard.classList.remove("positive", "negative");
    if (summary.cash_surplus > 0) surplusCard.classList.add("positive");
    else if (summary.cash_surplus < 0) surplusCard.classList.add("negative");

    document.getElementById("input-project-costs").value = costs.project_costs || "";
    document.getElementById("input-tax-costs").value = costs.tax_costs || "";
    document.getElementById("input-labor-costs").value = costs.labor_costs || "";

    setLaborModeUI(state.laborMode);
    loadRecentBoxTransactions();
  } catch (err) {
    showToast(err.message, true);
  }
}

// ---- مبدّل وضع أجرة العمال: نسبة % أو رقم ثابت ----

function setLaborModeUI(mode) {
  state.laborMode = mode;
  document.querySelectorAll("#labor-mode-segmented .segmented-btn").forEach((b) => {
    b.classList.toggle("active", b.dataset.mode === mode);
  });
  const hint = document.getElementById("labor-mode-hint");
  const input = document.getElementById("input-labor-costs");
  if (mode === "fixed") {
    hint.textContent = "مبلغ ثابت يُصرف بغض النظر عن الربح";
    input.placeholder = "مثال: 5000";
  } else {
    hint.textContent = "نسبة مئوية تُحسب من الربح اليومي";
    input.placeholder = "مثال: 10";
  }
}

document.querySelectorAll("#labor-mode-segmented .segmented-btn").forEach((btn) => {
  btn.addEventListener("click", () => setLaborModeUI(btn.dataset.mode));
});

document.getElementById("costs-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api("/costs", {
      method: "PUT",
      body: JSON.stringify({
        project_costs: document.getElementById("input-project-costs").value || 0,
        tax_costs: document.getElementById("input-tax-costs").value || 0,
        labor_costs: document.getElementById("input-labor-costs").value || 0,
        labor_mode: state.laborMode,
      }),
    });
    showToast("تم حفظ التكاليف");
    loadSummary();
  } catch (err) {
    showToast(err.message, true);
  }
});

document.getElementById("box-add-btn").addEventListener("click", () => submitBoxTx(1));
document.getElementById("box-remove-btn").addEventListener("click", () => openWithdrawNoteModal());

async function submitBoxTx(sign, note) {
  const input = document.getElementById("input-box-amount");
  const val = parseFloat(input.value);
  if (!val || val <= 0) {
    showToast("أدخل مبلغًا صحيحًا", true);
    return;
  }
  try {
    await api("/box/transactions", {
      method: "POST",
      body: JSON.stringify({ amount: val * sign, note: note || (sign > 0 ? "إضافة يدوية" : "") }),
    });
    input.value = "";
    showToast(sign > 0 ? "تمت الإضافة إلى الصندوق" : "تم السحب من الصندوق");
    loadSummary();
  } catch (err) {
    showToast(err.message, true);
  }
}

function openWithdrawNoteModal() {
  const val = parseFloat(document.getElementById("input-box-amount").value);
  if (!val || val <= 0) {
    showToast("أدخل مبلغًا صحيحًا أولًا", true);
    return;
  }
  document.getElementById("withdraw-note-amount").textContent = `سيتم سحب ${money(val)} من الصندوق`;
  document.getElementById("withdraw-note-input").value = "";
  openModal("withdraw-note-modal");
}

document.getElementById("withdraw-note-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const note = document.getElementById("withdraw-note-input").value.trim();
  if (!note) {
    showToast("الملاحظة مطلوبة", true);
    return;
  }
  closeModal("withdraw-note-modal");
  await submitBoxTx(-1, note);
});

async function loadRecentBoxTransactions() {
  const el = document.getElementById("box-recent");
  if (!el) return;
  try {
    const txs = await api("/box/transactions?limit=6");
    if (!txs.length) {
      el.innerHTML = "";
      return;
    }
    el.innerHTML = txs.map((t) => {
      const sign = t.amount >= 0 ? "+" : "";
      const cls = t.amount >= 0 ? "positive" : "negative";
      return `
        <div class="box-recent-row">
          <span class="box-recent-note">${escapeHtml(t.note || "—")}</span>
          <span class="box-recent-amount ${cls}">${sign}${money(t.amount)}</span>
        </div>
      `;
    }).join("");
  } catch (err) {
    el.innerHTML = "";
  }
}

document.getElementById("refresh-btn").addEventListener("click", () => {
  loadSummary();
  if (state.currentView === "products") loadProducts();
  if (state.currentView === "stats") loadDailyStats();
  if (state.currentView === "stocktake") loadStocktakeView();
  if (state.currentView === "analytics") loadAnalytics();
  checkHealth();
  showToast("تم التحديث");
});

// ---- تذكير بالجرود المفتوحة في الشاشة الرئيسية ----



// -------------------- المنتجات --------------------

async function loadProducts() {
  try {
    const [products] = await Promise.all([api("/products"), loadPriceChangeArrows(), loadCategories()]);
    state.products = products;
    renderProducts(products);
  } catch (err) {
    showToast(err.message, true);
  }
}

async function loadCategories() {
  try {
    const categories = await api("/categories");
    state.categories = categories;
  } catch (err) {
    state.categories = [];
  }
}

// ---- أسهم تغيّر السعر (أخضر للأعلى / أحمر للأسفل) بجانب سعر الشراء/البيع ----

async function loadPriceChangeArrows() {
  try {
    const data = await api("/price-changes/timeseries?limit=500");
    const map = {};
    (data.latest_changes || []).forEach((c) => {
      if (c.direction === "none") return;
      map[`${c.product_id}:${c.price_field}`] = c;
    });
    state.priceChangeArrows = map;
  } catch (err) {
    // لا نمنع تحميل المنتجات إن فشل هذا الطلب
    state.priceChangeArrows = {};
  }
}

function priceArrowHtml(productId, field) {
  const change = state.priceChangeArrows[`${productId}:${field}`];
  if (!change) return "";
  const isUp = change.direction === "up";
  const color = isUp ? "#3F6B3F" : "#A6432E";
  const path = isUp ? "M12 4l7 8h-4v8h-6v-8H5l7-8z" : "M12 20l-7-8h4V4h6v8h4l-7 8z";
  const title = `${isUp ? "ارتفع" : "انخفض"} من ${money(change.old_price)} إلى ${money(change.new_price)}`;
  return `<svg class="price-change-arrow" viewBox="0 0 24 24" width="13" height="13" title="${escapeHtml(title)}"><path fill="${color}" d="${path}"/></svg>`;
}

function renderProducts(products) {
  const list = document.getElementById("products-list");
  const empty = document.getElementById("products-empty");
  list.innerHTML = "";

  if (!products.length) {
    empty.classList.remove("hidden");
    return;
  }
  empty.classList.add("hidden");

  // تجميع المنتجات حسب الصنف (المنتجات مرتّبة مسبقًا من الـ API بحيث يكون
  // كل صنف متتاليًا)، ثم عرض عنوان لكل صنف يليه منتجاته، والمنتجات بدون
  // صنف تُعرض أخيرًا تحت عنوان "بدون صنف".
  const groups = [];
  let currentKey = undefined;
  let currentGroup = null;
  for (const p of products) {
    const key = p.category_id || "none";
    if (key !== currentKey) {
      currentKey = key;
      currentGroup = { categoryId: p.category_id, categoryName: p.category_name, items: [] };
      groups.push(currentGroup);
    }
    currentGroup.items.push(p);
  }

  for (const group of groups) {
    const section = document.createElement("div");
    section.className = "product-category-group";

    const header = document.createElement("div");
    header.className = "product-category-header";
    header.innerHTML = `
      <span class="product-category-title">${escapeHtml(group.categoryName || "بدون صنف")}</span>
      <span class="product-category-count">${group.items.length}</span>
    `;
    section.appendChild(header);

    const cardsWrap = document.createElement("div");
    cardsWrap.className = "products-list";

    for (const p of group.items) {
      const card = document.createElement("div");
      card.className = "product-card";
      const lowStock = p.quantity <= 3;
      card.innerHTML = `
        <div class="product-top">
          <span class="product-name">${escapeHtml(p.name)}</span>
          <span class="product-qty ${lowStock ? "low" : ""}">${p.quantity} قطعة</span>
        </div>
        <div class="product-prices">
          <span>شراء: <b>${money(p.buy_price)}</b>${priceArrowHtml(p.id, "buy")}</span>
          <span>بيع: <b>${money(p.sell_price)}</b>${priceArrowHtml(p.id, "sell")}</span>
          <span>ربح/وحدة: <b>${money(p.sell_price - p.buy_price)}</b></span>
        </div>
        <div class="product-actions">
          <button class="btn btn-ghost" data-action="edit" data-id="${p.id}">تعديل</button>
        </div>
      `;
      cardsWrap.appendChild(card);
    }
    section.appendChild(cardsWrap);
    list.appendChild(section);
  }

  list.querySelectorAll('[data-action="edit"]').forEach((btn) => {
    btn.addEventListener("click", () => openProductModal(btn.dataset.id));
  });
}

// ---- نافذة إضافة/تعديل منتج ----

const productModal = document.getElementById("product-modal");
const productForm = document.getElementById("product-form");

document.getElementById("add-product-btn").addEventListener("click", () => openProductModal(null));

function openProductModal(id) {
  const isEdit = Boolean(id);
  document.getElementById("product-modal-title").textContent = isEdit ? "تعديل المنتج" : "منتج جديد";
  document.getElementById("product-delete-btn").classList.toggle("hidden", !isEdit);
  document.getElementById("product-id").value = id || "";

  const categorySelect = document.getElementById("product-category");
  categorySelect.innerHTML =
    `<option value="">— بدون صنف —</option>` +
    state.categories.map((c) => `<option value="${c.id}">${escapeHtml(c.name)}</option>`).join("");

  if (isEdit) {
    const p = state.products.find((x) => String(x.id) === String(id));
    document.getElementById("product-name").value = p.name;
    document.getElementById("product-quantity").value = p.quantity;
    document.getElementById("product-buy").value = p.buy_price;
    document.getElementById("product-sell").value = p.sell_price;
    categorySelect.value = p.category_id || "";
  } else {
    productForm.reset();
    categorySelect.value = "";
  }
  openModal("product-modal");
}

productForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = document.getElementById("product-id").value;
  const payload = {
    name: document.getElementById("product-name").value,
    quantity: document.getElementById("product-quantity").value,
    buy_price: document.getElementById("product-buy").value,
    sell_price: document.getElementById("product-sell").value,
    category_id: document.getElementById("product-category").value || null,
  };
  try {
    if (id) {
      await api(`/products/${id}`, { method: "PUT", body: JSON.stringify(payload) });
      showToast("تم تحديث المنتج");
    } else {
      await api("/products", { method: "POST", body: JSON.stringify(payload) });
      showToast("تمت إضافة المنتج");
    }
    closeModal("product-modal");
    loadProducts();
    loadSummary();
  } catch (err) {
    showToast(err.message, true);
  }
});

document.getElementById("product-delete-btn").addEventListener("click", async () => {
  const id = document.getElementById("product-id").value;
  if (!id) return;
  if (!confirm("هل تريد حذف هذا المنتج نهائيًا؟")) return;
  try {
    await api(`/products/${id}`, { method: "DELETE" });
    showToast("تم حذف المنتج");
    closeModal("product-modal");
    loadProducts();
    loadSummary();
  } catch (err) {
    showToast(err.message, true);
  }
});

// -------------------- الإحصاء اليومي --------------------

const statsDateInput = document.getElementById("stats-date");
statsDateInput.value = todayISO();
statsDateInput.addEventListener("change", loadDailyStats);

async function loadDailyStats() {
  const dateVal = statsDateInput.value || todayISO();
  try {
    const stats = await api(`/stats/daily?date=${dateVal}`);
    document.getElementById("stat-daily-profit").textContent = money(stats.daily_profit);
    document.getElementById("stat-daily-capital").textContent = money(stats.daily_capital);
    document.getElementById("stat-daily-total").textContent = money(stats.daily_total);
    document.getElementById("stat-labor-share").textContent = money(stats.labor_share);
    document.getElementById("labor-share-label").textContent =
      stats.labor_mode === "fixed" ? "حصة العمال (مبلغ ثابت)" : "حصة العمال (نسبة من الربح)";
    renderDailyProducts(stats.products);
    document.getElementById("close-day-result").classList.add("hidden");
    const cashBox = document.getElementById("cash-count-result");
    if (stats.cash_count) {
      renderCashCountResult(stats.cash_count, cashBox);
      cashBox.classList.remove("hidden");
    } else {
      cashBox.classList.add("hidden");
    }
  } catch (err) {
    showToast(err.message, true);
  }
}

function renderDailyProducts(products) {
  const list = document.getElementById("daily-products");
  list.innerHTML = "";
  if (!products.length) {
    list.innerHTML = `<p class="empty-hint">لا توجد مبيعات مسجّلة في هذا التاريخ.</p>`;
    return;
  }
  for (const p of products) {
    const card = document.createElement("div");
    card.className = "product-card";
    card.innerHTML = `
      <div class="product-top">
        <span class="product-name">${escapeHtml(p.product_name)}</span>
        <span class="product-qty">${p.quantity_sold} مباعة</span>
      </div>
      <div class="product-prices">
        <span>شراء: <b>${money(p.buy_price)}</b></span>
        <span>بيع: <b>${money(p.sell_price)}</b></span>
      </div>
    `;
    list.appendChild(card);
  }
}

document.getElementById("close-day-btn").addEventListener("click", async () => {
  const expenses = document.getElementById("daily-expenses").value || 0;
  const actualCashInput = document.getElementById("daily-actual-cash").value;
  const cashNote = document.getElementById("daily-cash-note").value;
  const dateVal = statsDateInput.value || todayISO();
  const payload = { date: dateVal, expenses };
  if (actualCashInput !== "") {
    payload.actual_cash = actualCashInput;
    payload.cash_note = cashNote;
  }
  try {
    const result = await api("/stats/daily/close", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    const resEl = document.getElementById("close-day-result");
    resEl.textContent = `تمت إضافة ${money(result.net)} إلى الصندوق`;
    resEl.classList.remove("hidden");

    const cashBox = document.getElementById("cash-count-result");
    if (result.cash_count) {
      renderCashCountResult(result.cash_count, cashBox);
      cashBox.classList.remove("hidden");
    } else {
      cashBox.classList.add("hidden");
    }

    document.getElementById("daily-expenses").value = "";
    document.getElementById("daily-actual-cash").value = "";
    document.getElementById("daily-cash-note").value = "";
    showToast("تم إغلاق اليوم بنجاح");
    loadSummary();
  } catch (err) {
    showToast(err.message, true);
  }
});

function renderCashCountResult(cc, container) {
  const isSurplus = cc.status === "surplus";
  const isDeficit = cc.status === "deficit";
  const label = isSurplus ? "فائض نقدي" : isDeficit ? "عجز نقدي" : "الصندوق مطابق تمامًا";
  const cls = isSurplus ? "positive" : isDeficit ? "negative" : "";
  container.innerHTML = `
    <div class="cash-count-row"><span>المتوقع في الصندوق</span><b>${money(cc.expected_cash)}</b></div>
    <div class="cash-count-row"><span>المبلغ الحقيقي المُدخَل</span><b>${money(cc.actual_cash)}</b></div>
    <div class="cash-count-row highlight ${cls}"><span>${label}</span><b>${money(Math.abs(cc.diff))}</b></div>
    ${cc.note ? `<p class="hint-text tiny">${escapeHtml(cc.note)}</p>` : ""}
  `;
}

// -------------------- الجرد (شاشة جماعية واحدة، مثل الفاتورة) --------------------

const stocktakeDateInput = document.getElementById("stocktake-date");
stocktakeDateInput.value = todayISO();

async function loadStocktakeView() {
  try {
    const products = state.products.length ? state.products : await api("/products");
    state.products = products;
    renderStocktakeBulkList(products);
  } catch (err) {
    showToast(err.message, true);
  }
  await loadStocktakeHistory();
}

function renderStocktakeBulkList(products) {
  const list = document.getElementById("stocktake-bulk-list");
  const empty = document.getElementById("stocktake-bulk-empty");
  list.innerHTML = "";

  if (!products.length) {
    empty.classList.remove("hidden");
    return;
  }
  empty.classList.add("hidden");

  products.forEach((p, idx) => {
    const row = document.createElement("div");
    row.className = "stocktake-row";
    row.dataset.productId = p.id;
    row.dataset.name = p.name.toLowerCase();
    row.innerHTML = `
      <div class="stocktake-row-info">
        <span class="stocktake-row-name">${escapeHtml(p.name)}</span>
        <span class="stocktake-row-ref">المسجّل حاليًا: <b>${p.quantity}</b></span>
      </div>
      <input
        type="number"
        inputmode="numeric"
        class="stocktake-row-input"
        data-product-id="${p.id}"
        data-reference="${p.quantity}"
        value="${p.quantity}"
        placeholder="0"
      >
    `;
    list.appendChild(row);
  });

  // إعداد الانتقال السريع بالـ Enter إلى الحقل التالي، وتحديد كامل النص
  // عند التركيز حتى تتم الكتابة فوق الرقم مباشرة دون الحاجة لحذفه يدويًا،
  // وتلوين الحقل عند وجود فرق عن القيمة المرجعية.
  const inputs = Array.from(list.querySelectorAll(".stocktake-row-input"));
  inputs.forEach((input, i) => {
    input.addEventListener("focus", () => input.select());
    input.addEventListener("input", () => updateStocktakeRowState(input));
    input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        const next = inputs[i + 1];
        if (next) {
          next.focus();
          next.select();
        } else {
          input.blur();
        }
      }
    });
  });
}

function updateStocktakeRowState(input) {
  const ref = Number(input.dataset.reference);
  const val = input.value === "" ? ref : Number(input.value);
  const row = input.closest(".stocktake-row");
  row.classList.remove("changed", "invalid");
  if (input.value !== "" && (isNaN(val) || val < 0)) {
    row.classList.add("invalid");
    return;
  }
  if (val !== ref) row.classList.add("changed");
}

// ---- بحث سريع للتصفية/الانتقال المباشر لمنتج ----

document.getElementById("stocktake-search").addEventListener("input", (e) => {
  const q = e.target.value.trim().toLowerCase();
  const rows = document.querySelectorAll("#stocktake-bulk-list .stocktake-row");
  let firstMatch = null;
  rows.forEach((row) => {
    const match = !q || row.dataset.name.includes(q);
    row.classList.toggle("hidden", !match);
    if (match && !firstMatch) firstMatch = row;
  });
  if (q && firstMatch) {
    firstMatch.scrollIntoView({ behavior: "smooth", block: "center" });
  }
});

// ---- حفظ الجرد الجماعي ----

document.getElementById("stocktake-save-btn").addEventListener("click", async () => {
  const inputs = Array.from(document.querySelectorAll("#stocktake-bulk-list .stocktake-row-input"));
  const items = [];
  for (const input of inputs) {
    if (input.value === "") continue;
    const val = Number(input.value);
    if (isNaN(val) || val < 0) {
      showToast("توجد كمية غير صحيحة في أحد المنتجات", true);
      input.focus();
      return;
    }
    const ref = Number(input.dataset.reference);
    if (val === ref) continue; // لا فرق = لا داعي لإرساله
    items.push({ product_id: input.dataset.productId, counted_quantity: val });
  }

  if (!items.length) {
    showToast("لم تُدخل أي كمية مختلفة عن المسجّل حاليًا", true);
    return;
  }

  try {
    const result = await api("/stocktake/bulk", {
      method: "POST",
      body: JSON.stringify({ date: stocktakeDateInput.value || todayISO(), items }),
    });
    showToast(`تم حفظ الجرد — تم بيع ${result.total_sold_quantity} قطعة`);
    loadProducts();
    loadStocktakeView();
    loadSummary();
    if (state.currentView === "stats") loadDailyStats();
  } catch (err) {
    showToast(err.message, true);
  }
});

// ---- جرد اليوم كقائمة واحدة متصلة (كل دفعة حفظ = قسم بفاصل)، مع مجموع كلي ----

async function loadStocktakeHistory() {
  const list = document.getElementById("stocktake-day-list");
  const empty = document.getElementById("stocktake-day-empty");
  const totalBox = document.getElementById("stocktake-day-total");
  try {
    const dateVal = stocktakeDateInput.value || todayISO();
    const data = await api(`/stocktake/day?date=${dateVal}`);
    list.innerHTML = "";

    if (!data.batches.length) {
      empty.classList.remove("hidden");
      totalBox.classList.add("hidden");
      return;
    }
    empty.classList.add("hidden");

    data.batches.forEach((batch, idx) => {
      if (idx > 0) {
        const sep = document.createElement("div");
        sep.className = "stocktake-batch-separator";
        sep.innerHTML = `<span>جرد جديد${batch.created_at ? " — " + formatTimeOnly(batch.created_at) : ""}</span>`;
        list.appendChild(sep);
      }

      batch.items.forEach((it) => {
        const row = document.createElement("div");
        row.className = "stocktake-day-item";
        row.innerHTML = `
          <span class="stocktake-day-item-name">${escapeHtml(it.product_name)}</span>
          <span class="stocktake-day-item-qty">-${it.quantity_sold}</span>
          <span class="stocktake-day-item-revenue">${money(it.revenue)}</span>
        `;
        list.appendChild(row);
      });

      const batchTotal = document.createElement("div");
      batchTotal.className = "stocktake-batch-total";
      batchTotal.innerHTML = `
        <span>مجموع هذه الدفعة (${batch.total_quantity} قطعة)</span>
        <span>${money(batch.total_revenue)} · ربح ${money(batch.total_profit)}</span>
      `;
      list.appendChild(batchTotal);
    });

    totalBox.classList.remove("hidden");
    totalBox.innerHTML = `
      <div class="stocktake-day-total-row">
        <span>إجمالي الكمية المباعة اليوم</span>
        <b>${data.total_quantity}</b>
      </div>
      <div class="stocktake-day-total-row">
        <span>إجمالي الإيراد</span>
        <b>${money(data.total_revenue)}</b>
      </div>
      <div class="stocktake-day-total-row highlight">
        <span>إجمالي الربح</span>
        <b>${money(data.total_profit)}</b>
      </div>
    `;
  } catch (err) {
    empty.classList.remove("hidden");
    totalBox.classList.add("hidden");
  }
}

function formatTimeOnly(isoString) {
  try {
    const d = new Date(isoString);
    return d.toLocaleTimeString("ar-EG", { hour: "2-digit", minute: "2-digit" });
  } catch (err) {
    return "";
  }
}

stocktakeDateInput.addEventListener("change", () => loadStocktakeHistory());


// -------------------- التحليلات (رسم بياني + الأكثر مبيعًا) --------------------

// تبديل فترة الرسم البياني
document.querySelectorAll("#period-segmented .segmented-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("#period-segmented .segmented-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    state.analyticsPeriod = btn.dataset.period;
    loadTimeseries();
  });
});

// تبديل ترتيب "الأكثر مبيعًا" (كمية / ربح / إيراد)
document.querySelectorAll("#top-sort-segmented .segmented-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("#top-sort-segmented .segmented-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    state.topSortBy = btn.dataset.sort;
    loadTopProducts();
  });
});

// تبديل فترة "الأكثر مبيعًا" (يستخدمها أيضًا قسم أعلى/أقل كمية)
document.querySelectorAll("#top-period-segmented .segmented-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("#top-period-segmented .segmented-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    state.topPeriod = btn.dataset.period;
    loadTopProducts();
  });
});

// ---- لوحة تخصيص عرض التحليلات (إظهار/إخفاء) ----

document.getElementById("analytics-visibility-btn").addEventListener("click", () => {
  document.getElementById("analytics-visibility-panel").classList.toggle("hidden");
});

document.querySelectorAll('[data-toggle]').forEach((checkbox) => {
  checkbox.addEventListener("change", () => {
    const key = checkbox.dataset.toggle;
    state.visibility[key] = checkbox.checked;
    applyVisibility();
    if (key === "section-product-chart" && checkbox.checked) {
      loadProductChart();
    }
  });
});

function applyVisibility() {
  Object.entries(state.visibility).forEach(([key, visible]) => {
    const el = document.getElementById(key);
    if (el) el.classList.toggle("hidden", !visible);
  });
}

async function loadAnalytics() {
  applyVisibility();
  const tasks = [loadTimeseries(), loadTopProducts(), loadPriceChangesSection()];
  if (state.visibility["section-product-chart"]) tasks.push(loadProductChartOptions());
  await Promise.all(tasks);
}

// ---- قسم التحليلات: تغيّر أسعار الشراء/البيع عبر الوقت ----

async function loadPriceChangesSection() {
  const list = document.getElementById("price-changes-list");
  const empty = document.getElementById("price-changes-empty");
  if (!list) return;
  try {
    const data = await api("/price-changes/timeseries?limit=200");
    const points = (data.points || []).slice().reverse(); // الأحدث أولًا
    list.innerHTML = "";
    if (!points.length) {
      empty.classList.remove("hidden");
      return;
    }
    empty.classList.add("hidden");
    points.forEach((p) => list.appendChild(buildPriceChangeRow(p)));
  } catch (err) {
    showToast(err.message, true);
  }
}

function buildPriceChangeRow(p) {
  const row = document.createElement("div");
  row.className = "price-change-row";
  const isUp = p.direction === "up";
  const arrowColor = isUp ? "#3F6B3F" : "#A6432E";
  const arrowPath = isUp ? "M12 4l7 8h-4v8h-6v-8H5l7-8z" : "M12 20l-7-8h4V4h6v8h4l-7 8z";
  const fieldLabel = p.price_field === "buy" ? "سعر الشراء" : "سعر البيع";
  row.innerHTML = `
    <svg viewBox="0 0 24 24" width="16" height="16" class="price-change-row-arrow"><path fill="${arrowColor}" d="${arrowPath}"/></svg>
    <div class="price-change-row-info">
      <span class="price-change-row-name">${escapeHtml(p.product_name || "منتج محذوف")} — ${fieldLabel}</span>
      <span class="price-change-row-sub">${money(p.old_price)} ← ${money(p.new_price)} · ${p.date || ""}</span>
    </div>
    <span class="price-change-row-impact ${p.impact >= 0 ? "positive" : "negative"}">${p.impact >= 0 ? "+" : ""}${money(p.impact)}</span>
  `;
  return row;
}

async function loadTimeseries() {
  const period = state.analyticsPeriod;
  const pointsMap = { daily: 14, weekly: 8, monthly: 12, yearly: 5 };
  try {
    const data = await api(`/analytics/timeseries?period=${period}&points=${pointsMap[period]}`);
    document.getElementById("analytics-total-profit").textContent = money(data.total_profit);
    document.getElementById("analytics-total-revenue").textContent = money(data.total_revenue);
    document.getElementById("analytics-total-quantity").textContent = money(data.total_quantity);
    document.getElementById("analytics-total-cost").textContent = money(data.total_cost);
    renderChart(data.points, period, "chart-svg", "chart-labels", "chart-empty", "chart-container", "chart-tooltip");
  } catch (err) {
    showToast(err.message, true);
  }
}

function renderChart(points, period, svgId, labelsId, emptyId, containerId, tooltipId) {
  const svg = document.getElementById(svgId);
  const labelsEl = document.getElementById(labelsId);
  const emptyEl = document.getElementById(emptyId);
  svg.innerHTML = "";
  labelsEl.innerHTML = "";

  const hasData = points.some((p) => p.profit !== 0 || p.quantity !== 0);
  if (!points.length || !hasData) {
    emptyEl.classList.remove("hidden");
    document.getElementById(containerId).style.display = "none";
    return;
  }
  emptyEl.classList.add("hidden");
  document.getElementById(containerId).style.display = "block";

  const W = 340, H = 200, PAD_X = 12, PAD_Y = 16;
  const n = points.length;
  const stepX = n > 1 ? (W - PAD_X * 2) / (n - 1) : 0;

  const profits = points.map((p) => p.profit);
  const qtys = points.map((p) => p.quantity);
  const maxProfit = Math.max(...profits, 1);
  const minProfit = Math.min(...profits, 0);
  const maxQty = Math.max(...qtys, 1);

  function xAt(i) { return PAD_X + (n > 1 ? i * stepX : (W - PAD_X * 2) / 2); }
  function yAtProfit(v) {
    const range = maxProfit - minProfit || 1;
    return H - PAD_Y - ((v - minProfit) / range) * (H - PAD_Y * 2);
  }
  function yAtQty(v) {
    return H - PAD_Y - (v / maxQty) * (H - PAD_Y * 2);
  }

  const nsSVG = "http://www.w3.org/2000/svg";

  function buildPolyline(values, yFn, colorVar, dashed) {
    const coords = values.map((v, i) => `${xAt(i)},${yFn(v)}`).join(" ");
    const poly = document.createElementNS(nsSVG, "polyline");
    poly.setAttribute("points", coords);
    poly.setAttribute("fill", "none");
    poly.setAttribute("stroke", colorVar);
    poly.setAttribute("stroke-width", "2.5");
    poly.setAttribute("stroke-linecap", "round");
    poly.setAttribute("stroke-linejoin", "round");
    if (dashed) poly.setAttribute("stroke-dasharray", "4 3");
    return poly;
  }

  if (minProfit < 0) {
    const zeroY = yAtProfit(0);
    const zeroLine = document.createElementNS(nsSVG, "line");
    zeroLine.setAttribute("x1", PAD_X);
    zeroLine.setAttribute("x2", W - PAD_X);
    zeroLine.setAttribute("y1", zeroY);
    zeroLine.setAttribute("y2", zeroY);
    zeroLine.setAttribute("stroke", "#E3DBC9");
    zeroLine.setAttribute("stroke-width", "1");
    svg.appendChild(zeroLine);
  }

  if (n > 1) {
    svg.appendChild(buildPolyline(qtys, yAtQty, "#2F3B2C99", true));
    svg.appendChild(buildPolyline(profits, yAtProfit, "#B8863E", false));
  }

  points.forEach((p, i) => {
    const cxQty = xAt(i), cyQty = yAtQty(p.quantity);
    const dotQty = document.createElementNS(nsSVG, "circle");
    dotQty.setAttribute("cx", cxQty);
    dotQty.setAttribute("cy", cyQty);
    dotQty.setAttribute("r", "2.5");
    dotQty.setAttribute("fill", "#2F3B2C99");
    svg.appendChild(dotQty);

    const cx = xAt(i), cy = yAtProfit(p.profit);
    const dot = document.createElementNS(nsSVG, "circle");
    dot.setAttribute("cx", cx);
    dot.setAttribute("cy", cy);
    dot.setAttribute("r", "4.5");
    dot.setAttribute("fill", "#B8863E");
    dot.setAttribute("stroke", "#FFFFFF");
    dot.setAttribute("stroke-width", "1.5");
    dot.setAttribute("class", "chart-point");

    dot.addEventListener("click", (e) => showChartTooltip(e, p, containerId, tooltipId));
    dot.addEventListener("touchstart", (e) => showChartTooltip(e, p, containerId, tooltipId), { passive: true });

    svg.appendChild(dot);
  });

  const labelStep = Math.max(1, Math.ceil(n / 6));
  points.forEach((p, i) => {
    if (i % labelStep !== 0 && i !== n - 1) return;
    const span = document.createElement("span");
    span.textContent = formatChartLabel(p.label, period);
    labelsEl.appendChild(span);
  });
}

function formatChartLabel(label, period) {
  if (period === "daily") return label.slice(5);
  if (period === "weekly") return label.replace("أسبوع ", "").slice(5);
  if (period === "monthly") return label.slice(5);
  return label;
}

function showChartTooltip(evt, point, containerId, tooltipId) {
  const tooltip = document.getElementById(tooltipId);
  const container = document.getElementById(containerId);
  const rect = container.getBoundingClientRect();
  const clientX = evt.touches ? evt.touches[0].clientX : evt.clientX;
  const clientY = evt.touches ? evt.touches[0].clientY : evt.clientY;
  const x = clientX - rect.left;
  const y = clientY - rect.top;

  tooltip.innerHTML = `${point.label || point.date}<br>الربح: ${money(point.profit)} · الكمية: ${point.quantity}`;
  tooltip.style.left = `${x}px`;
  tooltip.style.top = `${y}px`;
  tooltip.classList.remove("hidden");

  clearTimeout(showChartTooltip._t);
  showChartTooltip._t = setTimeout(() => tooltip.classList.add("hidden"), 2200);
}

async function loadTopProducts() {
  try {
    const data = await api(`/analytics/top-products?period=${state.topPeriod}&sort_by=${state.topSortBy}&limit=10`);
    renderTopProducts(data.items, state.topSortBy);
    renderMinMax(data.items);
  } catch (err) {
    showToast(err.message, true);
  }
}

function renderTopProducts(items, sortBy) {
  const list = document.getElementById("top-products-list");
  const empty = document.getElementById("top-products-empty");
  list.innerHTML = "";

  if (!items.length) {
    empty.classList.remove("hidden");
    return;
  }
  empty.classList.add("hidden");

  items.forEach((item, idx) => {
    const rank = idx + 1;
    const rankClass = rank === 1 ? "rank-1" : rank === 2 ? "rank-2" : rank === 3 ? "rank-3" : "rank-other";
    let metricValue, metricLabel;
    if (sortBy === "profit") { metricValue = item.profit; metricLabel = ""; }
    else if (sortBy === "revenue") { metricValue = item.revenue; metricLabel = ""; }
    else { metricValue = item.quantity_sold; metricLabel = " قطعة"; }

    const row = document.createElement("div");
    row.className = "top-product-row";
    row.innerHTML = `
      <span class="top-rank ${rankClass}">${rank}</span>
      <div class="top-info">
        <span class="top-name">${escapeHtml(item.product_name)}</span>
        <span class="top-sub">إيراد: ${money(item.revenue)} · ربح: ${money(item.profit)}</span>
      </div>
      <span class="top-metric">${money(metricValue)}${metricLabel}</span>
    `;
    list.appendChild(row);
  });
}

// ---- أعلى/أقل كمية بيعت لكل منتج (ضمن نفس فترة "الأكثر مبيعًا") ----

function renderMinMax(items) {
  const list = document.getElementById("minmax-list");
  const empty = document.getElementById("minmax-empty");
  list.innerHTML = "";

  if (!items.length) {
    empty.classList.remove("hidden");
    return;
  }
  empty.classList.add("hidden");

  // نرتب حسب الفرق بين الأعلى والأقل تنازليًا لإبراز الأكثر تذبذبًا أولًا
  const sorted = [...items].sort((a, b) => (b.max_sale_qty - b.min_sale_qty) - (a.max_sale_qty - a.min_sale_qty));

  sorted.forEach((item) => {
    const row = document.createElement("div");
    row.className = "minmax-row";
    row.innerHTML = `
      <span class="minmax-name">${escapeHtml(item.product_name)}</span>
      <div class="minmax-values">
        <span class="minmax-tag max">أعلى: ${item.max_sale_qty}</span>
        <span class="minmax-tag min">أقل: ${item.min_sale_qty}</span>
      </div>
    `;
    list.appendChild(row);
  });
}

// ---- خط بياني تفصيلي لمنتج محدد ----

async function loadProductChartOptions() {
  try {
    const products = state.products.length ? state.products : await api("/products");
    state.products = products;
    const select = document.getElementById("product-chart-select");
    const prevVal = select.value;
    select.innerHTML = products.map((p) => `<option value="${p.id}">${escapeHtml(p.name)}</option>`).join("");
    if (prevVal && products.some((p) => String(p.id) === prevVal)) select.value = prevVal;
    if (products.length) loadProductChart();
  } catch (err) {
    showToast(err.message, true);
  }
}

document.getElementById("product-chart-select").addEventListener("change", loadProductChart);

async function loadProductChart() {
  const select = document.getElementById("product-chart-select");
  const productId = select.value;
  if (!productId) return;

  try {
    const data = await api(`/analytics/product-timeseries?product_id=${productId}&limit=30`);
    document.getElementById("product-chart-max").textContent = money(data.max_quantity);
    document.getElementById("product-chart-min").textContent = money(data.min_quantity);

    const points = data.points.map((p) => ({
      label: p.date,
      date: p.date,
      profit: p.profit,
      quantity: p.quantity,
    }));

    const emptyEl = document.getElementById("product-chart-empty");
    if (!points.length) {
      emptyEl.classList.remove("hidden");
      document.getElementById("product-chart-container").style.display = "none";
      document.getElementById("product-chart-labels").innerHTML = "";
      return;
    }
    emptyEl.classList.add("hidden");

    renderChart(
      points,
      "daily",
      "product-chart-svg",
      "product-chart-labels",
      "product-chart-empty",
      "product-chart-container",
      "product-chart-tooltip"
    );
  } catch (err) {
    showToast(err.message, true);
  }
}

// -------------------- إدارة الأصناف --------------------

document.getElementById("manage-categories-btn").addEventListener("click", () => {
  openModal("categories-modal");
  loadCategoriesModal();
});

async function loadCategoriesModal() {
  await loadCategories();
  renderCategoriesList();
}

function renderCategoriesList() {
  const list = document.getElementById("categories-list");
  const empty = document.getElementById("categories-empty");
  list.innerHTML = "";

  if (!state.categories.length) {
    empty.classList.remove("hidden");
    return;
  }
  empty.classList.add("hidden");

  state.categories.forEach((c) => {
    const row = document.createElement("div");
    row.className = "category-row";
    row.innerHTML = `
      <input type="text" class="category-row-input" value="${escapeHtml(c.name)}" data-id="${c.id}">
      <span class="category-row-count">${c.products_count} منتج</span>
      <button class="btn btn-ghost small" data-action="rename-category" data-id="${c.id}">حفظ</button>
      <button class="btn btn-ghost danger small" data-action="delete-category" data-id="${c.id}">حذف</button>
    `;
    list.appendChild(row);
  });

  list.querySelectorAll('[data-action="rename-category"]').forEach((btn) => {
    btn.addEventListener("click", () => renameCategory(btn.dataset.id));
  });
  list.querySelectorAll('[data-action="delete-category"]').forEach((btn) => {
    btn.addEventListener("click", () => deleteCategory(btn.dataset.id));
  });
}

document.getElementById("category-add-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = document.getElementById("category-name-input");
  const name = input.value.trim();
  if (!name) return;
  try {
    await api("/categories", { method: "POST", body: JSON.stringify({ name }) });
    input.value = "";
    showToast("تمت إضافة الصنف");
    await loadCategoriesModal();
  } catch (err) {
    showToast(err.message, true);
  }
});

async function renameCategory(id) {
  const input = document.querySelector(`.category-row-input[data-id="${id}"]`);
  const name = input.value.trim();
  if (!name) {
    showToast("اسم الصنف مطلوب", true);
    return;
  }
  try {
    await api(`/categories/${id}`, { method: "PUT", body: JSON.stringify({ name }) });
    showToast("تم حفظ الصنف");
    await loadCategoriesModal();
    loadProducts();
  } catch (err) {
    showToast(err.message, true);
  }
}

async function deleteCategory(id) {
  if (!confirm("حذف هذا الصنف؟ ستبقى منتجاته لكنها ستصبح بدون صنف.")) return;
  try {
    await api(`/categories/${id}`, { method: "DELETE" });
    showToast("تم حذف الصنف");
    await loadCategoriesModal();
    loadProducts();
  } catch (err) {
    showToast(err.message, true);
  }
}

// -------------------- الفواتير (إضافة مخزون) --------------------

const invoiceModal = document.getElementById("invoice-modal");
const invoiceItemsEl = document.getElementById("invoice-items");
const invoiceRowTemplate = document.getElementById("invoice-row-template");

document.getElementById("add-invoice-btn").addEventListener("click", openInvoiceModal);

async function openInvoiceModal() {
  try {
    const products = state.products.length ? state.products : await api("/products");
    state.products = products;
    if (!state.categories.length) await loadCategories();
  } catch (err) {
    showToast(err.message, true);
    return;
  }
  document.getElementById("invoice-date").value = todayISO();
  document.getElementById("invoice-note").value = "";
  invoiceItemsEl.innerHTML = "";
  addInvoiceRow();
  updateInvoiceTotal();
  openModal("invoice-modal");
}

document.getElementById("invoice-add-row-btn").addEventListener("click", () => addInvoiceRow());

function addInvoiceRow() {
  const frag = invoiceRowTemplate.content.cloneNode(true);
  const row = frag.querySelector(".invoice-row");
  const select = row.querySelector(".invoice-row-product");

  state.products.forEach((p) => {
    const opt = document.createElement("option");
    opt.value = p.id;
    opt.textContent = `${p.name} (متوفر: ${p.quantity})`;
    select.insertBefore(opt, select.querySelector('option[value="__new__"]'));
  });

  const newNameWrap = row.querySelector(".invoice-row-new-name");
  const newCategoryWrap = row.querySelector(".invoice-row-new-category");
  const categorySelect = row.querySelector(".invoice-row-category");
  const buyInput = row.querySelector(".invoice-row-buy");
  const sellInput = row.querySelector(".invoice-row-sell");
  const hint = row.querySelector(".invoice-row-hint");

  if (categorySelect) {
    categorySelect.innerHTML =
      `<option value="">— بدون صنف —</option>` +
      state.categories.map((c) => `<option value="${c.id}">${escapeHtml(c.name)}</option>`).join("");
  }

  function refreshRowState() {
    const val = select.value;
    if (val === "__new__") {
      newNameWrap.classList.remove("hidden");
      if (newCategoryWrap) newCategoryWrap.classList.remove("hidden");
      hint.textContent = "منتج جديد بالكامل — سيُضاف للنظام عند حفظ الفاتورة.";
      buyInput.value = "";
      sellInput.value = "";
    } else if (val) {
      newNameWrap.classList.add("hidden");
      if (newCategoryWrap) newCategoryWrap.classList.add("hidden");
      const p = state.products.find((x) => String(x.id) === String(val));
      if (p) {
        buyInput.value = p.buy_price;
        sellInput.value = p.sell_price;
        hint.textContent = `السعر الحالي: شراء ${money(p.buy_price)} · بيع ${money(p.sell_price)} — عدّل إذا اختلف في هذه الفاتورة`;
      }
    } else {
      newNameWrap.classList.add("hidden");
      if (newCategoryWrap) newCategoryWrap.classList.add("hidden");
      hint.textContent = "";
    }
  }

  select.addEventListener("change", refreshRowState);
  row.querySelector('[data-action="remove-row"]').addEventListener("click", () => {
    row.remove();
    updateInvoiceTotal();
  });
  row.querySelectorAll(".invoice-row-qty, .invoice-row-buy").forEach((inp) => {
    inp.addEventListener("input", updateInvoiceTotal);
  });

  invoiceItemsEl.appendChild(row);
}

function updateInvoiceTotal() {
  let total = 0;
  invoiceItemsEl.querySelectorAll(".invoice-row").forEach((row) => {
    const qty = parseFloat(row.querySelector(".invoice-row-qty").value) || 0;
    const buy = parseFloat(row.querySelector(".invoice-row-buy").value) || 0;
    total += qty * buy;
  });
  document.getElementById("invoice-total-cost").textContent = money(total);
}

document.getElementById("invoice-save-btn").addEventListener("click", async () => {
  const rows = Array.from(invoiceItemsEl.querySelectorAll(".invoice-row"));
  if (!rows.length) {
    showToast("أضف منتجًا واحدًا على الأقل", true);
    return;
  }

  const items = [];
  for (const row of rows) {
    const productVal = row.querySelector(".invoice-row-product").value;
    const qty = row.querySelector(".invoice-row-qty").value;
    const buy = row.querySelector(".invoice-row-buy").value;
    const sell = row.querySelector(".invoice-row-sell").value;

    if (!productVal) {
      showToast("اختر منتجًا لكل سطر في الفاتورة", true);
      return;
    }
    if (!qty || Number(qty) <= 0) {
      showToast("أدخل كمية صحيحة لكل منتج", true);
      return;
    }

    const item = { quantity: qty, buy_price: buy || 0, sell_price: sell || 0 };
    if (productVal === "__new__") {
      const name = row.querySelector(".invoice-row-name").value.trim();
      if (!name) {
        showToast("أدخل اسم المنتج الجديد", true);
        return;
      }
      item.name = name;
      const categorySelect = row.querySelector(".invoice-row-category");
      if (categorySelect && categorySelect.value) {
        item.category_id = categorySelect.value;
      }
    } else {
      item.product_id = productVal;
    }
    items.push(item);
  }

  const payload = {
    invoice_date: document.getElementById("invoice-date").value || todayISO(),
    note: document.getElementById("invoice-note").value,
    items,
  };

  try {
    const result = await api("/invoices", { method: "POST", body: JSON.stringify(payload) });
    let msg = "تم حفظ الفاتورة وتحديث المخزون";
    if (result.price_changes && result.price_changes.length) {
      const gains = result.price_changes.filter((c) => c.direction === "gain").length;
      const losses = result.price_changes.filter((c) => c.direction === "loss").length;
      if (gains || losses) {
        msg += ` (تغيّر سعر: ${gains} ربح استثماري، ${losses} خسارة استثمارية)`;
      }
    }
    showToast(msg);
    closeModal("invoice-modal");
    loadProducts();
    loadSummary();
    if (state.currentView === "analytics") loadPriceChangesSection();
  } catch (err) {
    showToast(err.message, true);
  }
});

// ---- سجل الفواتير ----

document.getElementById("open-invoices-btn").addEventListener("click", () => {
  openModal("invoices-modal");
  loadInvoices();
});

document.querySelectorAll("#invoices-sort-segmented .segmented-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("#invoices-sort-segmented .segmented-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    state.invoicesSort = btn.dataset.sort;
    loadInvoices();
  });
});

async function loadInvoices() {
  const list = document.getElementById("invoices-list");
  const empty = document.getElementById("invoices-empty");
  try {
    const sortBy = state.invoicesSort || "date_desc";
    const invoices = await api(`/invoices?sort_by=${sortBy}`);
    list.innerHTML = "";
    if (!invoices.length) {
      empty.classList.remove("hidden");
      return;
    }
    empty.classList.add("hidden");
    invoices.forEach((inv) => list.appendChild(buildInvoiceCard(inv)));
  } catch (err) {
    showToast(err.message, true);
  }
}

function buildInvoiceCard(inv) {
  const card = document.createElement("div");
  card.className = "invoice-card";
  const itemsHtml = (inv.items || []).map((it) => `
    <div class="invoice-item-row">
      <span class="invoice-item-name">${escapeHtml(it.product_name || "")}</span>
      <span class="invoice-item-qty">+${it.quantity}</span>
      <span class="invoice-item-cost">${money(it.line_cost)}</span>
    </div>
  `).join("");

  card.innerHTML = `
    <div class="invoice-card-top">
      <span class="invoice-card-date">${inv.invoice_date}</span>
      <span class="invoice-card-total">${money(inv.total_cost)}</span>
    </div>
    ${inv.note ? `<p class="hint-text tiny">${escapeHtml(inv.note)}</p>` : ""}
    <div class="invoice-items-list">${itemsHtml}</div>
    <div class="invoice-card-footer">
      <span>إجمالي القطع: ${inv.total_quantity}</span>
      <button class="btn btn-ghost danger tiny-btn" data-action="delete-invoice" data-id="${inv.id}">حذف</button>
    </div>
  `;

  card.querySelector('[data-action="delete-invoice"]').addEventListener("click", () => deleteInvoice(inv.id));
  return card;
}

async function deleteInvoice(id) {
  if (!confirm("حذف هذه الفاتورة؟ سيتم خصم كمياتها من المنتجات المرتبطة بها.")) return;
  try {
    await api(`/invoices/${id}`, { method: "DELETE" });
    showToast("تم حذف الفاتورة");
    loadInvoices();
    loadProducts();
    loadSummary();
  } catch (err) {
    showToast(err.message, true);
  }
}

// -------------------- النوافذ المنبثقة (Modals) --------------------

function openModal(id) {
  document.getElementById(id).classList.remove("hidden");
  document.body.style.overflow = "hidden";
}
function closeModal(id) {
  document.getElementById(id).classList.add("hidden");
  document.body.style.overflow = "";
}
document.querySelectorAll("[data-close]").forEach((el) => {
  el.addEventListener("click", () => closeModal(el.dataset.close));
});

// -------------------- التاريخ في الرأس --------------------

function renderTodayDate() {
  const now = new Date();
  const formatter = new Intl.DateTimeFormat("ar-EG", { weekday: "long", day: "numeric", month: "long" });
  document.getElementById("today-date").textContent = formatter.format(now);
}

// -------------------- تسجيل Service Worker (PWA) --------------------

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
  });
}

// -------------------- بدء التشغيل --------------------

renderTodayDate();
checkHealth();
loadSummary();
loadCategories();
applyVisibility();
