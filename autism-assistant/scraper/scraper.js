"use strict";
/**
 * scraper.js — Crawl tài liệu từ Google Sites và ghi vào Google Sheets Knowledge_Base
 *
 * Cách dùng:
 *   cp .env.example .env        # điền SPREADSHEET_ID + GOOGLE_CREDENTIALS_PATH
 *   node scraper.js             # chạy scraper
 *
 * Bước 1: Fetch HTML từ Google Sites → trích xuất tất cả link Drive/Docs
 * Bước 2: Classify từng tài liệu theo category bằng rules-based
 * Bước 3: Batch write vào sheet Knowledge_Base (ghi đè từ row 2)
 */

require("dotenv").config();

const axios      = require("axios");
const cheerio    = require("cheerio");
const { google } = require("googleapis");
const path       = require("path");
const fs         = require("fs");

const SOURCE_URL         = "https://sites.google.com/site/tranvancong/tailieu";
const SPREADSHEET_ID     = process.env.SPREADSHEET_ID;
const CREDENTIALS_PATH   = process.env.GOOGLE_CREDENTIALS_PATH || path.join(__dirname, "credentials/service-account.json");
const SHEET_NAME         = "Knowledge_Base";

// ─── Document catalog (pre-classified known documents) ────────────────────────
// Format: { id, category, subcategory, title_vi, tags }
// source_url will be filled from scraping; summary_vi filled manually after
const KNOWN_CATALOG = [
  { id: "KB-001", category: "general",    subcategory: "",          title_vi: "Một số nguyên lý làm việc với trẻ rối loạn phát triển", tags: "principles,general" },
  { id: "KB-002", category: "autism",     subcategory: "",          title_vi: "100 ngày đầu tiên",                                     tags: "early_intervention,autism" },
  { id: "KB-003", category: "autism",     subcategory: "sensory",   title_vi: "Bài tập điều hoà cảm giác",                             tags: "sensory,regulation,autism" },
  { id: "KB-004", category: "nutrition",  subcategory: "gfcf",      title_vi: "Ăn uống cho người tự kỷ",                               tags: "nutrition,autism,gfcf" },
  { id: "KB-005", category: "adhd",       subcategory: "nutrition", title_vi: "Dinh dưỡng cho trẻ ADHD",                               tags: "nutrition,adhd" },
  { id: "KB-006", category: "adhd",       subcategory: "motor",     title_vi: "Tập hợp bài tập (ADHD)",                                tags: "exercise,adhd,motor" },
  { id: "KB-007", category: "motor",      subcategory: "gross",     title_vi: "Các bài luyện tập tâm vận động",                        tags: "motor,gross_motor,psychomotor" },
  { id: "KB-008", category: "tubucnho",   subcategory: "tap1",      title_vi: "Từng bước nhỏ, tập 1 – Giới thiệu chương trình",        tags: "tubucnho,tap1,intro" },
  { id: "KB-009", category: "tubucnho",   subcategory: "tap2",      title_vi: "Từng bước nhỏ, tập 2 – Chương trình cơ bản",            tags: "tubucnho,tap2,basic" },
  { id: "KB-010", category: "tubucnho",   subcategory: "tap3",      title_vi: "Từng bước nhỏ, tập 3 – Kỹ năng nền",                   tags: "tubucnho,tap3,foundation" },
  { id: "KB-011", category: "tubucnho",   subcategory: "tap4",      title_vi: "Từng bước nhỏ, tập 4 – Vận động thô",                   tags: "tubucnho,tap4,gross_motor" },
  { id: "KB-012", category: "tubucnho",   subcategory: "tap5",      title_vi: "Từng bước nhỏ, tập 5 – Vận động tinh",                  tags: "tubucnho,tap5,fine_motor" },
  { id: "KB-013", category: "tubucnho",   subcategory: "tap6",      title_vi: "Từng bước nhỏ, tập 6 – Ngôn ngữ",                      tags: "tubucnho,tap6,language" },
  { id: "KB-014", category: "tubucnho",   subcategory: "tap7",      title_vi: "Từng bước nhỏ, tập 7 – Xã hội hoá",                    tags: "tubucnho,tap7,socialization" },
  { id: "KB-015", category: "speech",     subcategory: "",          title_vi: "12 bước tiến lên ngôn ngữ",                             tags: "speech,language,steps" },
  { id: "KB-016", category: "social",     subcategory: "",          title_vi: "Dạy kỹ năng giao tiếp xã hội",                         tags: "social,communication" },
  { id: "KB-017", category: "behavior",   subcategory: "",          title_vi: "100 bài can thiệp hành vi",                             tags: "behavior,intervention,100_bai" },
  { id: "KB-018", category: "speech",     subcategory: "therapy",   title_vi: "Âm ngữ trị liệu cơ bản",                               tags: "speech,therapy,language" },
  { id: "KB-019", category: "autism",     subcategory: "play",      title_vi: "Dạy kỹ năng chơi cho trẻ tự kỷ",                       tags: "autism,play,social" },
  { id: "KB-020", category: "motor",      subcategory: "fine",      title_vi: "Bài tập vận động tinh tại nhà",                        tags: "motor,fine_motor,home" }
];

// ─── Rules-based classifier ───────────────────────────────────────────────────
function classifyDocument(title, url) {
  const t = title.toLowerCase();

  if (t.includes("từng bước nhỏ")) {
    const tapMatch = t.match(/tập\s*(\d+)/);
    const tapNum   = tapMatch ? tapMatch[1] : "1";
    const subcat   = "tap" + tapNum;
    const domain   = t.includes("vận động thô")   ? "gross_motor"
                   : t.includes("vận động tinh")   ? "fine_motor"
                   : t.includes("ngôn ngữ")         ? "language"
                   : t.includes("xã hội")           ? "socialization"
                   : t.includes("giới thiệu")       ? "intro"
                   : "general";
    return { category: "tubucnho", subcategory: subcat, tags: ["tubucnho", subcat, domain] };
  }
  if (t.includes("adhd") || t.includes("tăng động"))
    return { category: "adhd", subcategory: "", tags: ["adhd"] };
  if (t.includes("chậm nói") || t.includes("âm ngữ") || t.includes("ngôn ngữ"))
    return { category: "speech", subcategory: "", tags: ["speech", "language"] };
  if (t.includes("tự kỷ") || t.includes("autism") || t.includes("rối loạn phát triển"))
    return { category: "autism", subcategory: "", tags: ["autism"] };
  if (t.includes("dinh dưỡng") || t.includes("ăn uống") || t.includes("gfcf"))
    return { category: "nutrition", subcategory: "gfcf", tags: ["nutrition", "gfcf"] };
  if (t.includes("vận động") || t.includes("tâm vận") || t.includes("bài tập"))
    return { category: "motor", subcategory: "", tags: ["motor"] };
  if (t.includes("xã hội") || t.includes("giao tiếp") || t.includes("kỹ năng"))
    return { category: "social", subcategory: "", tags: ["social"] };
  if (t.includes("hành vi") || t.includes("can thiệp"))
    return { category: "behavior", subcategory: "", tags: ["behavior"] };
  return { category: "general", subcategory: "", tags: ["general"] };
}

// ─── Scrape Google Sites page ─────────────────────────────────────────────────
async function fetchDocumentLinks() {
  console.log("Fetching:", SOURCE_URL);
  let html;
  try {
    const resp = await axios.get(SOURCE_URL, {
      headers: {
        "User-Agent": "Mozilla/5.0 (compatible; autism-assistant-scraper/1.0)"
      },
      timeout: 15000
    });
    html = resp.data;
  } catch (err) {
    console.warn("Could not fetch Google Sites page:", err.message);
    console.log("Falling back to pre-classified catalog only.");
    return [];
  }

  const $    = cheerio.load(html);
  const docs = [];
  const seen = new Set();

  // Google Sites classic: links to Drive/Docs appear in various selectors
  $("a").each((i, el) => {
    const href  = $(el).attr("href") || "";
    const title = $(el).text().trim();

    if (!href || !title) return;
    if (!href.includes("drive.google.com") && !href.includes("docs.google.com")) return;
    if (seen.has(href)) return;
    seen.add(href);

    docs.push({ title, url: href });
  });

  console.log("Found " + docs.length + " document links on the page.");
  return docs;
}

// ─── Merge scraped links with known catalog ───────────────────────────────────
function buildFinalCatalog(scrapedDocs) {
  const catalog = [...KNOWN_CATALOG];
  const knownTitles = new Set(catalog.map(d => d.title_vi.toLowerCase()));
  let nextId = catalog.length + 1;

  for (const doc of scrapedDocs) {
    const normTitle = doc.title.toLowerCase();
    const existing  = catalog.find(c => normTitle.includes(c.title_vi.toLowerCase().slice(0, 15)));

    if (existing) {
      // Enrich existing entry with scraped URL
      existing.source_url = doc.url;
    } else if (!knownTitles.has(normTitle)) {
      // New document found on page
      const classification = classifyDocument(doc.title, doc.url);
      const id = "KB-" + String(nextId++).padStart(3, "0");
      catalog.push({
        id,
        category:    classification.category,
        subcategory: classification.subcategory,
        title_vi:    doc.title,
        source_url:  doc.url,
        tags:        classification.tags.join(",")
      });
      knownTitles.add(normTitle);
    }
  }

  return catalog;
}

// ─── Write to Google Sheets ───────────────────────────────────────────────────
async function writeToSheets(catalog) {
  if (!SPREADSHEET_ID) {
    throw new Error("SPREADSHEET_ID not set in .env");
  }

  if (!fs.existsSync(CREDENTIALS_PATH)) {
    throw new Error("Service account credentials not found at: " + CREDENTIALS_PATH + "\n" +
      "Create a Google Cloud service account, download the JSON key, save it there, " +
      "and share the spreadsheet with the service account email.");
  }

  const auth   = new google.auth.GoogleAuth({
    keyFile: CREDENTIALS_PATH,
    scopes:  ["https://www.googleapis.com/auth/spreadsheets"]
  });
  const sheets = google.sheets({ version: "v4", auth });
  const now    = new Date().toISOString();

  // Headers (row 1)
  const headers = [["id", "category", "subcategory", "title_vi", "source_url", "summary_vi", "tags", "age_range", "difficulty", "scraped_at"]];

  // Data rows
  const rows = catalog.map(doc => [
    doc.id,
    doc.category,
    doc.subcategory || "",
    doc.title_vi,
    doc.source_url || "",
    doc.summary_vi || "",   // empty — fill manually
    typeof doc.tags === "string" ? doc.tags : (doc.tags || []).join(","),
    doc.age_range || "2-10",
    doc.difficulty || "medium",
    now
  ]);

  // Write headers
  await sheets.spreadsheets.values.update({
    spreadsheetId:    SPREADSHEET_ID,
    range:            SHEET_NAME + "!A1",
    valueInputOption: "RAW",
    requestBody:      { values: headers }
  });

  // Write data rows (from row 2)
  if (rows.length > 0) {
    await sheets.spreadsheets.values.update({
      spreadsheetId:    SPREADSHEET_ID,
      range:            SHEET_NAME + "!A2",
      valueInputOption: "RAW",
      requestBody:      { values: rows }
    });
  }

  console.log("✓ Wrote " + rows.length + " documents to " + SHEET_NAME);
  console.log("\nNEXT STEP: Mở Google Sheets → tab Knowledge_Base → điền cột F (summary_vi) cho mỗi tài liệu.");
  console.log("Ưu tiên: tubucnho, motor, autism, speech");
}

// ─── Main ─────────────────────────────────────────────────────────────────────
async function main() {
  console.log("=== Autism Assistant — Knowledge Base Scraper ===\n");

  const scrapedDocs  = await fetchDocumentLinks();
  const finalCatalog = buildFinalCatalog(scrapedDocs);

  console.log("Total documents in catalog:", finalCatalog.length);

  // Print summary by category
  const byCat = {};
  finalCatalog.forEach(d => { byCat[d.category] = (byCat[d.category] || 0) + 1; });
  console.log("\nBy category:");
  Object.entries(byCat).sort((a,b) => b[1]-a[1]).forEach(([cat, count]) => {
    console.log("  " + cat.padEnd(12) + count);
  });

  try {
    await writeToSheets(finalCatalog);
  } catch (err) {
    console.error("\n✗ Failed to write to Sheets:", err.message);
    console.log("\nDry run — catalog would be written:");
    finalCatalog.forEach(d => console.log("  [" + d.id + "] " + d.category + " | " + d.title_vi));
    process.exit(1);
  }
}

main().catch(err => {
  console.error("Fatal:", err);
  process.exit(1);
});
