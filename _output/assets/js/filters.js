(() => {
  const grid = document.getElementById("loc-grid");
  if (!grid) return;

  const cards = Array.from(grid.querySelectorAll(".loc-card"));
  const status = document.getElementById("filter-status");
  const q = document.getElementById("filter-q");
  const sort = document.getElementById("filter-sort");
  const buttons = Array.from(document.querySelectorAll(".chip-btn"));

  let filter = "all";

  const priceOf = (card) => {
    const raw = card.dataset.price;
    if (!raw) return null;
    const n = Number(raw);
    return Number.isFinite(n) ? n : null;
  };

  const milesOf = (card) => {
    const raw = card.dataset.miles;
    if (!raw) return null;
    const n = Number(raw);
    return Number.isFinite(n) ? n : null;
  };

  const matches = (card) => {
    const query = (q?.value || "").trim().toLowerCase();
    if (query && !(card.dataset.name || "").includes(query)) return false;
    const price = priceOf(card);
    const flags = card.dataset.flags === "1";
    switch (filter) {
      case "under5":
        return price != null && price <= 5000;
      case "under6":
        return price != null && price <= 6000;
      case "unknown":
        return price == null;
      case "flags":
        return flags;
      default:
        return true;
    }
  };

  const sortCards = (list) => {
    const mode = sort?.value || "price";
    return list.slice().sort((a, b) => {
      if (mode === "name") {
        return (a.dataset.name || "").localeCompare(b.dataset.name || "");
      }
      if (mode === "miles") {
        const am = milesOf(a);
        const bm = milesOf(b);
        if (am == null && bm == null) return 0;
        if (am == null) return 1;
        if (bm == null) return -1;
        return am - bm;
      }
      const ap = priceOf(a);
      const bp = priceOf(b);
      if (ap == null && bp == null) return 0;
      if (ap == null) return 1;
      if (bp == null) return -1;
      return ap - bp;
    });
  };

  const render = () => {
    const visible = sortCards(cards.filter(matches));
    cards.forEach((card) => {
      card.hidden = true;
    });
    visible.forEach((card) => {
      card.hidden = false;
      grid.appendChild(card);
    });
    if (status) {
      const label =
        filter === "all"
          ? "all locations"
          : filter === "under5"
            ? "under $5k"
            : filter === "under6"
              ? "under $6k"
              : filter === "unknown"
                ? "unknown price"
                : "material red flags";
      status.textContent = `Showing ${visible.length} of ${cards.length} · ${label}`;
    }
  };

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      filter = btn.dataset.filter || "all";
      buttons.forEach((b) => b.classList.toggle("is-active", b === btn));
      render();
    });
  });

  q?.addEventListener("input", render);
  sort?.addEventListener("change", render);
  render();
})();
